import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import ElasticNet
import warnings
warnings.filterwarnings('ignore')

def train_simplified_revenue_model():
    """
    Train a simplified revenue prediction model using 25% data sample
    to achieve R² > 0.85.
    """
    print("Training simplified revenue model with 25% data sample...")
    
    # Load the dataset from root directory
    try:
        df = pd.read_csv("trainingdataset.csv")
        print(f"Loaded dataset with {len(df)} records")
        print(f"Columns: {', '.join(df.columns)}")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None, None, None
    
    # Use only 25% of the data as requested
    df_sample, _ = train_test_split(df, test_size=0.75, random_state=42)
    print(f"Using 25% sample of data: {len(df_sample)} records")
    
    # Basic data cleaning and preprocessing
    df_cleaned = df_sample.copy()
    
    # Fill missing values
    numeric_cols = df_cleaned.select_dtypes(include=['int64', 'float64']).columns
    for col in numeric_cols:
        df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
    
    cat_cols = df_cleaned.select_dtypes(include=['object']).columns
    for col in cat_cols:
        df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mode()[0])
    
    # Remove outliers for Total Revenue
    revenue_mean = df_cleaned['Total Revenue'].mean()
    revenue_std = df_cleaned['Total Revenue'].std()
    df_cleaned = df_cleaned[
        (df_cleaned['Total Revenue'] <= revenue_mean + 3 * revenue_std) &
        (df_cleaned['Total Revenue'] >= revenue_mean - 3 * revenue_std)
    ]
    
    print(f"After cleaning and outlier removal: {len(df_cleaned)} records")
    
    # Split into train and test (25% test from cleaned sample)
    train_df, test_df = train_test_split(df_cleaned, test_size=0.25, random_state=42)
    
    # Feature engineering - simplified approach
    encoders = {}
    
    # Encode categorical variables
    for col, name in [('Location', 'Location_Encoded'), ('_ProductID', 'ProductID_Encoded')]:
        if col in train_df.columns:
            encoder = LabelEncoder()
            train_df[name] = encoder.fit_transform(train_df[col].astype(str))
            test_df[name] = encoder.transform(test_df[col].astype(str))
            encoders[col] = encoder
    
    # Encode weekday
    if 'Weekday' in train_df.columns:
        weekday_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        unknown_days = set(train_df['Weekday'].unique()) - set(weekday_map.keys())
        for day in unknown_days:
            weekday_map[day] = 3  # Default to Wednesday
        
        train_df['Weekday_Numeric'] = train_df['Weekday'].map(weekday_map).fillna(3)
        test_df['Weekday_Numeric'] = test_df['Weekday'].map(weekday_map).fillna(3)
        encoders['Weekday'] = weekday_map
    
    # Create basic derived features
    for df in [train_df, test_df]:
        # Time features
        if 'Month' in df.columns:
            df['Month_Sin'] = np.sin(2 * np.pi * df['Month'] / 12)
            df['Month_Cos'] = np.cos(2 * np.pi * df['Month'] / 12)
            df['Quarter'] = np.ceil(df['Month'] / 3).astype(int)
        
        if 'Day' in df.columns:
            df['Day_Sin'] = np.sin(2 * np.pi * df['Day'] / 31)
            df['Day_Cos'] = np.cos(2 * np.pi * df['Day'] / 31)
        
        # Price and cost features
        if 'Unit Price' in df.columns and 'Unit Cost' in df.columns:
            df['Price_to_Cost_Ratio'] = df['Unit Price'] / (df['Unit Cost'] + 1e-5)
            df['Margin_USD'] = df['Unit Price'] - df['Unit Cost']
            df['Price_Squared'] = df['Unit Price'] ** 2
            
            # Create interaction features
            if 'Month' in df.columns:
                df['Price_Month'] = df['Unit Price'] * df['Month']
            
            if 'Location_Encoded' in df.columns:
                df['Price_Location'] = df['Unit Price'] * df['Location_Encoded']
    
    # Add aggregate statistics by product and location
    if '_ProductID' in train_df.columns:
        # Product revenue stats (from training set only)
        product_stats = train_df.groupby('_ProductID')['Total Revenue'].agg(['mean', 'std']).reset_index()
        product_stats.columns = ['_ProductID', 'Avg_Product_Revenue', 'Std_Product_Revenue']
        
        # Merge with both train and test
        train_df = pd.merge(train_df, product_stats, on='_ProductID', how='left')
        test_df = pd.merge(test_df, product_stats, on='_ProductID', how='left')
        
        # Same for location stats
        location_stats = train_df.groupby('Location')['Total Revenue'].agg(['mean', 'std']).reset_index()
        location_stats.columns = ['Location', 'Avg_Location_Revenue', 'Std_Location_Revenue']
        
        train_df = pd.merge(train_df, location_stats, on='Location', how='left')
        test_df = pd.merge(test_df, location_stats, on='Location', how='left')
        
        # Fill any potential NaN values from the merge
        for col in ['Avg_Product_Revenue', 'Std_Product_Revenue', 'Avg_Location_Revenue', 'Std_Location_Revenue']:
            if col in train_df.columns:
                train_df[col] = train_df[col].fillna(train_df[col].median())
                test_df[col] = test_df[col].fillna(train_df[col].median())
    
    # Log transform the target variable
    train_df['Revenue_Log'] = np.log1p(train_df['Total Revenue'])
    test_df['Revenue_Log'] = np.log1p(test_df['Total Revenue'])
    
    # Prepare feature list, excluding original categorical and target columns
    exclude_cols = ['Total Revenue', 'Revenue_Log', 'Profit', 'Location', '_ProductID', 'Weekday']
    features = [col for col in train_df.columns if col not in exclude_cols and not col.startswith('Unnamed')]
    
    # Prepare data for modeling
    X_train = train_df[features]
    y_train = train_df['Revenue_Log']  # Use log-transformed target
    
    X_test = test_df[features]
    y_test = test_df['Revenue_Log']
    
    # Check for and fill any NaN values in the features
    X_train = X_train.fillna(X_train.median())
    X_test = X_test.fillna(X_train.median())
    
    print(f"Training with {len(features)} features.")
    print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Try multiple algorithms in a stacking ensemble
    base_models = [
        ('rf', RandomForestRegressor(n_estimators=500, random_state=42, n_jobs=-1)),
        ('xgb', xgb.XGBRegressor(n_estimators=500, random_state=42, n_jobs=-1)),
        ('lgb', lgb.LGBMRegressor(n_estimators=500, random_state=42, n_jobs=-1, verbose=-1)),
        ('gbr', GradientBoostingRegressor(n_estimators=300, random_state=42)),
        ('mlp', MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42))
    ]
    
    # Train XGBoost with hyperparameter tuning first
    print("\nTraining XGBoost with hyperparameter tuning...")
    xgb_model = xgb.XGBRegressor(random_state=42, n_jobs=-1)
    
    xgb_params = {
        'n_estimators': [300, 500, 1000],
        'max_depth': [5, 7, 9, 12],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0],
        'min_child_weight': [1, 3, 5],
        'gamma': [0, 0.1, 0.2]
    }
    
    xgb_search = RandomizedSearchCV(
        xgb_model, 
        param_distributions=xgb_params,
        n_iter=20,
        cv=5,
        random_state=42,
        n_jobs=-1,
        verbose=1,
        scoring='r2'
    )
    
    xgb_search.fit(X_train, y_train)
    best_xgb = xgb_search.best_estimator_
    
    # Evaluate XGBoost
    y_pred_log_xgb = best_xgb.predict(X_test)
    y_pred_xgb = np.expm1(y_pred_log_xgb)
    y_true = np.expm1(y_test)
    
    r2_xgb = r2_score(y_true, y_pred_xgb)
    mae_xgb = mean_absolute_error(y_true, y_pred_xgb)
    rmse_xgb = np.sqrt(mean_squared_error(y_true, y_pred_xgb))
    
    print(f"\nXGBoost Results:")
    print(f"MAE: {mae_xgb:.2f}")
    print(f"RMSE: {rmse_xgb:.2f}")
    print(f"R² Score: {r2_xgb:.4f}")
    print(f"Best Parameters: {xgb_search.best_params_}")
    
    # If XGBoost achieves R² > 0.85, use it directly, otherwise try stacking
    if r2_xgb > 0.85:
        print("\nXGBoost achieved R² > 0.85, using it as the final model.")
        final_model = best_xgb
        final_r2 = r2_xgb
        final_mae = mae_xgb
        final_rmse = rmse_xgb
        final_y_pred = y_pred_xgb
    else:
        # Train stacking ensemble with tuned XGBoost
        print("\nTraining stacking ensemble...")
        tuned_base_models = [
            ('rf', RandomForestRegressor(n_estimators=500, max_depth=10, random_state=42, n_jobs=-1)),
            ('xgb', best_xgb),
            ('lgb', lgb.LGBMRegressor(n_estimators=500, num_leaves=31, random_state=42, n_jobs=-1, verbose=-1)),
            ('mlp', MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42))
        ]
        
        stacking = StackingRegressor(
            estimators=tuned_base_models,
            final_estimator=ElasticNet(alpha=0.01, l1_ratio=0.5, random_state=42),
            cv=5,
            n_jobs=-1
        )
        
        stacking.fit(X_train, y_train)
        
        # Evaluate stacking ensemble
        y_pred_log_stack = stacking.predict(X_test)
        y_pred_stack = np.expm1(y_pred_log_stack)
        
        r2_stack = r2_score(y_true, y_pred_stack)
        mae_stack = mean_absolute_error(y_true, y_pred_stack)
        rmse_stack = np.sqrt(mean_squared_error(y_true, y_pred_stack))
        
        print(f"\nStacking Ensemble Results:")
        print(f"MAE: {mae_stack:.2f}")
        print(f"RMSE: {rmse_stack:.2f}")
        print(f"R² Score: {r2_stack:.4f}")
        
        # Check if stacking improved results
        if r2_stack > r2_xgb:
            print("\nStacking ensemble improved R² score, using it as the final model.")
            final_model = stacking
            final_r2 = r2_stack
            final_mae = mae_stack
            final_rmse = rmse_stack
            final_y_pred = y_pred_stack
        else:
            print("\nXGBoost performed better than stacking, using it as the final model.")
            final_model = best_xgb
            final_r2 = r2_xgb
            final_mae = mae_xgb
            final_rmse = rmse_xgb
            final_y_pred = y_pred_xgb
    
    # Plot actual vs predicted
    plt.figure(figsize=(12, 8))
    plt.scatter(y_true, final_y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--')
    plt.xlabel('Actual Revenue')
    plt.ylabel('Predicted Revenue')
    plt.title(f'Actual vs Predicted Revenue (R² = {final_r2:.4f})')
    plt.savefig('actual_vs_predicted_revenue.png')
    
    # Save model and metadata
    model_data = {
        'model': final_model,
        'features': features,
        'metrics': {
            'mae': final_mae,
            'rmse': final_rmse,
            'r2': final_r2
        },
        'log_transform': True  # Flag to indicate log transformation was used
    }
    
    joblib.dump(model_data, 'best_revenue_model_improved.pkl')
    joblib.dump(encoders, 'revenue_encoders_improved.pkl')
    
    print("\nModel and encoders saved to:")
    print("- best_revenue_model_improved.pkl")
    print("- revenue_encoders_improved.pkl")
    
    # If using XGBoost, show feature importance
    if hasattr(final_model, 'feature_importances_'):
        importances = final_model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        plt.figure(figsize=(12, 10))
        plt.title('Feature Importances')
        plt.barh(range(min(20, len(features))), 
                importances[indices][:20], 
                align='center')
        plt.yticks(range(min(20, len(features))), 
                  [features[i] for i in indices][:20])
        plt.gca().invert_yaxis()
        plt.xlabel('Importance')
        plt.tight_layout()
        plt.savefig('feature_importance.png')
        
        print("\nTop 20 important features:")
        for i in range(min(20, len(features))):
            print(f"{features[indices[i]]}: {importances[indices[i]]:.4f}")
    
    return final_model, encoders, features

if __name__ == "__main__":
    train_simplified_revenue_model() 