import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

def train_modified_revenue_model():
    """
    Train a revenue prediction model using the modified dataset with 25% data sample.
    Modified dataset no longer contains 'Total Cost', 'Profit', and 'Profit Margin (%)'.
    """
    print("Training revenue model with modified dataset (25% sample)...")
    
    # Load the dataset
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
    
    # Add derived features that were present in original model
    df_cleaned['Total Cost'] = df_cleaned['Unit Cost'] * (df_cleaned['Total Revenue'] / df_cleaned['Unit Price'])
    df_cleaned['Margin_USD'] = df_cleaned['Unit Price'] - df_cleaned['Unit Cost']
    df_cleaned['Profit Margin (%)'] = (df_cleaned['Margin_USD'] / df_cleaned['Unit Price']) * 100
    
    # Split into train and test (25% test from cleaned sample)
    train_df, test_df = train_test_split(df_cleaned, test_size=0.25, random_state=42)
    
    # Feature engineering - keep the same approach as the successful model
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
    
    # Create derived features
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
    exclude_cols = ['Total Revenue', 'Revenue_Log', 'Location', '_ProductID', 'Weekday']
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
    print(f"Features: {', '.join(features)}")
    print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Train XGBoost with hyperparameter tuning
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
    
    # Save the final model and metadata
    final_model = best_xgb
    final_r2 = r2_xgb
    final_mae = mae_xgb
    final_rmse = rmse_xgb
    final_y_pred = y_pred_xgb
    
    # Save the model with metadata
    model_data = {
        'model': final_model,
        'features': features,
        'r2': final_r2,
        'mae': final_mae,
        'rmse': final_rmse,
        'log_transform': True
    }
    
    joblib.dump(model_data, 'best_revenue_model_modified.pkl')
    joblib.dump(encoders, 'revenue_encoders_modified.pkl')
    
    print("\nModel and encoders saved to:")
    print("- best_revenue_model_modified.pkl")
    print("- revenue_encoders_modified.pkl")
    
    # Plot feature importance
    if hasattr(final_model, 'feature_importances_'):
        importances = final_model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        # Top 20 features
        top_n = min(20, len(features))
        top_features = [features[i] for i in indices[:top_n]]
        top_importances = [importances[i] for i in indices[:top_n]]
        
        print("\nTop 20 important features:")
        for feature, importance in zip(top_features, top_importances):
            print(f"{feature}: {importance:.4f}")
        
        # Create feature importance plot
        plt.figure(figsize=(12, 8))
        plt.barh(range(top_n), top_importances, align='center')
        plt.yticks(range(top_n), [features[i] for i in indices[:top_n]])
        plt.xlabel('Importance')
        plt.title('Feature Importance (XGBoost)')
        plt.tight_layout()
        plt.savefig('feature_importance_modified.png')
    
    # Plot actual vs predicted revenue
    plt.figure(figsize=(10, 6))
    plt.scatter(y_true, final_y_pred, alpha=0.5)
    plt.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], 'r--')
    plt.xlabel('Actual Revenue')
    plt.ylabel('Predicted Revenue')
    plt.title('Actual vs Predicted Revenue')
    plt.tight_layout()
    plt.savefig('actual_vs_predicted_modified.png')
    
    return final_model, encoders, features

if __name__ == "__main__":
    train_modified_revenue_model() 