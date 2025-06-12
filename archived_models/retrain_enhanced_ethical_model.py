import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')

def train_enhanced_ethical_model():
    """
    Train an enhanced ethical revenue prediction model using 100% of the dataset.
    Uses improved feature engineering but with a fixed model configuration.
    NO TARGET LEAKAGE: Does not use any features derived from the target variable or order quantity.
    Only uses features available before a sale: Unit Price, Unit Cost, Location, ProductID, time features.
    """
    print("Training enhanced ethical revenue model without target leakage...")
    
    # Load the dataset with the updated structure
    df = pd.read_csv("trainingdataset.csv")
    print(f"Loaded dataset with {len(df)} records")
    
    # Print columns to verify structure
    print(f"Dataset columns: {df.columns.tolist()}")
    
    # Basic data cleaning
    df_cleaned = df.copy()
    
    # Fill missing values
    numeric_cols = df_cleaned.select_dtypes(include=['int64', 'float64']).columns
    for col in numeric_cols:
        df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
    
    cat_cols = df_cleaned.select_dtypes(include=['object']).columns
    for col in cat_cols:
        df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mode()[0])
    
    # Remove revenue outliers (beyond 3 sigma)
    revenue_mean = df_cleaned['Total Revenue'].mean()
    revenue_std = df_cleaned['Total Revenue'].std()
    df_cleaned = df_cleaned[
        (df_cleaned['Total Revenue'] <= revenue_mean + 3 * revenue_std) &
        (df_cleaned['Total Revenue'] >= revenue_mean - 3 * revenue_std)
    ]
    
    print(f"After cleaning and outlier removal: {len(df_cleaned)} records")
    
    # Split into train and test (80/20 split)
    train_df, test_df = train_test_split(df_cleaned, test_size=0.2, random_state=42)
    
    # Feature engineering - starting with label encoding for categorical features
    encoders = {}
    
    # 1. Encode categorical variables
    for col, name in [('Location', 'Location_Encoded'), ('_ProductID', 'ProductID_Encoded')]:
        if col in train_df.columns:
            encoder = LabelEncoder()
            train_df[name] = encoder.fit_transform(train_df[col].astype(str))
            test_df[name] = encoder.transform(test_df[col].astype(str))
            encoders[col] = encoder
    
    # 2. Weekday encoding
    if 'Weekday' in train_df.columns:
        # Check if Weekday is already numeric
        if train_df['Weekday'].dtype == np.int64 or train_df['Weekday'].dtype == np.float64:
            train_df['Weekday_Numeric'] = train_df['Weekday']
            test_df['Weekday_Numeric'] = test_df['Weekday']
        else:
            weekday_map = {
                'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                'Friday': 4, 'Saturday': 5, 'Sunday': 6,
                # Also handle numeric strings
                '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6
            }
            unknown_days = set(train_df['Weekday'].astype(str).unique()) - set(weekday_map.keys())
            for day in unknown_days:
                try:
                    # Try to convert to integer (handles numeric formats)
                    weekday_map[day] = int(float(day)) % 7
                except:
                    weekday_map[day] = 3  # Default to Wednesday
            
            train_df['Weekday_Numeric'] = train_df['Weekday'].astype(str).map(weekday_map).fillna(3)
            test_df['Weekday_Numeric'] = test_df['Weekday'].astype(str).map(weekday_map).fillna(3)
            encoders['Weekday'] = weekday_map
    
    # 3. Feature creation for both datasets
    for df in [train_df, test_df]:
        # Temporal features
        if 'Month' in df.columns:
            # Cyclical encoding for month
            df['Month_Sin'] = np.sin(2 * np.pi * df['Month'] / 12)
            df['Month_Cos'] = np.cos(2 * np.pi * df['Month'] / 12)
            
            # Quarter
            df['Quarter'] = np.ceil(df['Month'] / 3).astype(int)
            
            # Season flags
            df['Is_Winter'] = df['Month'].isin([12, 1, 2]).astype(int)
            df['Is_Spring'] = df['Month'].isin([3, 4, 5]).astype(int)
            df['Is_Summer'] = df['Month'].isin([6, 7, 8]).astype(int)
            df['Is_Fall'] = df['Month'].isin([9, 10, 11]).astype(int)
            
            # Holiday season
            df['Is_Holiday_Season'] = df['Month'].isin([11, 12]).astype(int)
        
        if 'Day' in df.columns:
            # Cyclical encoding for day
            df['Day_Sin'] = np.sin(2 * np.pi * df['Day'] / 31)
            df['Day_Cos'] = np.cos(2 * np.pi * df['Day'] / 31)
        
        if 'Weekday_Numeric' in df.columns:
            # Weekend flag
            df['Is_Weekend'] = (df['Weekday_Numeric'] >= 5).astype(int)
        
        # Price and cost features
        if 'Unit Price' in df.columns and 'Unit Cost' in df.columns:
            # Price/cost relationships
            df['Price_to_Cost_Ratio'] = df['Unit Price'] / (df['Unit Cost'] + 1e-5)
            df['Margin_Per_Unit'] = df['Unit Price'] - df['Unit Cost']
            df['Margin_Per_Unit_Pct'] = df['Margin_Per_Unit'] / (df['Unit Price'] + 1e-5) * 100
            
            # Polynomial features
            df['Price_Squared'] = df['Unit Price'] ** 2
            df['Price_Log'] = np.log1p(df['Unit Price'])
    
    # 4. Calculate product-level statistics from training data only
    product_stats = train_df.groupby('_ProductID').agg({
        'Unit Price': ['mean', 'std', 'min', 'max'],
        'Unit Cost': ['mean']
    })
    
    # Flatten columns
    product_stats.columns = [f'Product_{col[0]}_{col[1]}' for col in product_stats.columns]
    product_stats = product_stats.reset_index()
    
    # Calculate product popularity
    product_counts = train_df['_ProductID'].value_counts()
    product_popularity = pd.DataFrame({
        '_ProductID': product_counts.index,
        'Product_Popularity': product_counts.values / len(train_df)
    })
    
    # 5. Calculate location-level statistics from training data only
    location_stats = train_df.groupby('Location').agg({
        'Unit Price': ['mean', 'std', 'min', 'max'],
        'Unit Cost': ['mean']
    })
    
    # Flatten columns
    location_stats.columns = [f'Location_{col[0]}_{col[1]}' for col in location_stats.columns]
    location_stats = location_stats.reset_index()
    
    # 6. Calculate product-month seasonal patterns from training data
    product_month_stats = train_df.groupby(['_ProductID', 'Month']).agg({
        'Unit Price': ['mean']
    })
    
    # Flatten columns
    product_month_stats.columns = [f'Product_Month_{col[0]}_{col[1]}' for col in product_month_stats.columns]
    product_month_stats = product_month_stats.reset_index()
    
    # Apply statistics to both train and test sets
    for df_name, df in [('train', train_df), ('test', test_df)]:
        # Merge product statistics
        df = pd.merge(df, product_stats, on='_ProductID', how='left')
        df = pd.merge(df, product_popularity, on='_ProductID', how='left')
        
        # Merge location statistics
        df = pd.merge(df, location_stats, on='Location', how='left')
        
        # Merge seasonal patterns
        if '_ProductID' in df.columns and 'Month' in df.columns:
            df = pd.merge(df, product_month_stats, on=['_ProductID', 'Month'], how='left')
        
        # Fill missing values for any NaN created during merges
        for col in df.columns:
            if df[col].isnull().any():
                if col.endswith('_mean') or col.endswith('_median'):
                    df[col] = df[col].fillna(df[col].median())
                elif col.endswith('_std'):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(0)
        
        # 7. Create price deviation features
        if 'Unit Price' in df.columns:
            # Price vs product average
            if 'Product_Unit Price_mean' in df.columns:
                df['Price_vs_Product_Avg'] = df['Unit Price'] / (df['Product_Unit Price_mean'] + 1e-5)
            
            # Price vs location average
            if 'Location_Unit Price_mean' in df.columns:
                df['Price_vs_Location_Avg'] = df['Unit Price'] / (df['Location_Unit Price_mean'] + 1e-5)
            
            # Price vs seasonal average
            if 'Product_Month_Unit Price_mean' in df.columns:
                df['Price_Seasonal_Deviation'] = df['Unit Price'] / (df['Product_Month_Unit Price_mean'] + 1e-5)
        
        # 8. Interaction features
        if 'Unit Price' in df.columns:
            # Price × popularity
            if 'Product_Popularity' in df.columns:
                df['Price_Popularity'] = df['Unit Price'] * df['Product_Popularity']
            
            # Price × location
            if 'Location_Encoded' in df.columns:
                df['Price_Location'] = df['Unit Price'] * df['Location_Encoded']
            
            # Price × seasonality
            if 'Month' in df.columns:
                df['Price_Month'] = df['Unit Price'] * df['Month']
                df['Price_Quarter'] = df['Unit Price'] * df['Quarter']
        
        # Update dataframe
        if df_name == 'train':
            train_df = df
        else:
            test_df = df
    
    # Log transform the target variable
    train_df['Revenue_Log'] = np.log1p(train_df['Total Revenue'])
    test_df['Revenue_Log'] = np.log1p(test_df['Total Revenue'])
    
    # Prepare feature list, excluding original categorical variables and target
    exclude_cols = [
        'Total Revenue', 'Revenue_Log', 'Location', '_ProductID', 'Weekday'
    ]
    
    features = [col for col in train_df.columns if col not in exclude_cols 
               and not col.startswith('Unnamed')]
    
    print(f"Training with {len(features)} ethical features that don't leak target information.")
    
    # Prepare data for modeling
    X_train = train_df[features]
    y_train = train_df['Revenue_Log']  # Use log-transformed target
    
    X_test = test_df[features]
    y_test = test_df['Revenue_Log']
    
    # Check for and fill any NaN values in the features
    X_train = X_train.fillna(X_train.median())
    X_test = X_test.fillna(X_train.median())
    
    print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Identify categorical features for LightGBM
    categorical_features = []
    for col in features:
        # Binary indicators and encoded categories
        if col.startswith('Is_') or '_Encoded' in col:
            categorical_features.append(features.index(col))
    
    print(f"Identified {len(categorical_features)} categorical features for LightGBM")
    
    # Do a quick 5-fold cross-validation to check performance
    print("\nPerforming 5-fold cross-validation...")
    
    # Define fixed parameters
    lgb_params = {
        'objective': 'regression',
        'n_estimators': 500,
        'learning_rate': 0.05,
        'num_leaves': 63,
        'max_depth': 7,
        'min_child_samples': 20,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.1,
        'reg_lambda': 0.1,
        'random_state': 42,
        'n_jobs': -1,
        'verbose': -1
    }
    
    # Create model
    lgb_model = lgb.LGBMRegressor(**lgb_params)
    
    # Do cross-validation
    cv_scores = cross_val_score(
        lgb_model, 
        X_train, 
        y_train, 
        cv=5, 
        scoring='r2',
        verbose=1
    )
    
    # Print CV results
    print(f"\nCross-validation R² scores: {cv_scores}")
    print(f"Mean R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    # Train final model
    print("\nTraining final model...")
    
    # Define model
    final_model = lgb.LGBMRegressor(**lgb_params)
    
    # Train model
    final_model.fit(
        X_train,
        y_train,
        categorical_feature=categorical_features
    )
    
    # Evaluate on test set
    y_pred_log = final_model.predict(X_test)
    y_pred = np.expm1(y_pred_log)
    y_true = np.expm1(y_test)
    
    # Calculate final metrics
    test_r2 = r2_score(y_true, y_pred)
    test_mae = mean_absolute_error(y_true, y_pred)
    test_rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    
    print("\nTest set performance:")
    print(f"R²: {test_r2:.4f}")
    print(f"MAE: {test_mae:.2f}")
    print(f"RMSE: {test_rmse:.2f}")
    
    # Get feature importance
    importances = final_model.feature_importances_
    feature_importance = pd.DataFrame({
        'Feature': features,
        'Importance': importances
    })
    feature_importance['Importance_Pct'] = feature_importance['Importance'] / feature_importance['Importance'].sum() * 100
    feature_importance = feature_importance.sort_values('Importance', ascending=False)
    
    # Output top 20 features
    print("\nTop 20 features by importance:")
    for idx, row in feature_importance.head(20).iterrows():
        print(f"{row['Feature']}: {row['Importance_Pct']:.2f}%")
    
    # Plot feature importance
    plt.figure(figsize=(12, 10))
    top_features = feature_importance.head(20)
    plt.barh(
        np.arange(len(top_features)),
        top_features['Importance_Pct'],
        align='center'
    )
    plt.yticks(np.arange(len(top_features)), top_features['Feature'])
    plt.xlabel('Importance (%)')
    plt.title('Feature Importance')
    plt.tight_layout()
    plt.savefig('feature_importance_enhanced_ethical.png')
    
    # Plot actual vs predicted
    plt.figure(figsize=(10, 6))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], 'r--')
    plt.xlabel('Actual Revenue')
    plt.ylabel('Predicted Revenue')
    plt.title('Actual vs Predicted Revenue')
    plt.tight_layout()
    plt.savefig('actual_vs_predicted_enhanced_ethical.png')
    
    # Save model and metadata
    model_data = {
        'model': final_model,
        'features': features,
        'r2': test_r2,
        'mae': test_mae,
        'rmse': test_rmse,
        'params': lgb_params,
        'log_transform': True
    }
    
    # Save model and encoders
    joblib.dump(model_data, 'enhanced_revenue_model_ethical.pkl')
    joblib.dump(encoders, 'enhanced_revenue_encoders_ethical.pkl')
    
    print("\nModel and encoders saved to:")
    print("- enhanced_revenue_model_ethical.pkl")
    print("- enhanced_revenue_encoders_ethical.pkl")
    
    return final_model, encoders, features

if __name__ == "__main__":
    train_enhanced_ethical_model() 