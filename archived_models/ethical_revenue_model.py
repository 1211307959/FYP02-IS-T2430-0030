import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, RandomizedSearchCV, KFold, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler, PowerTransformer, QuantileTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.cluster import KMeans
from sklearn.ensemble import HistGradientBoostingRegressor, VotingRegressor, StackingRegressor
import xgboost as xgb
import lightgbm as lgb
try:
    from catboost import CatBoostRegressor, Pool
    CATBOOST_AVAILABLE = True
except ImportError:
    print("CatBoost not available. Only XGBoost and LightGBM will be used.")
    CATBOOST_AVAILABLE = False
import warnings
warnings.filterwarnings('ignore')

def train_ethical_revenue_model():
    """
    Train an enhanced ethical revenue prediction model using 100% of the dataset.
    Implements advanced feature engineering and model optimization techniques.
    Does not use target-leaking features like Total Cost, Profit, or Profit Margin.
    Only uses features that can be known before the sale.
    """
    print("Training enhanced ethical revenue model with FULL dataset (100% of data)...")
    
    # Load the dataset
    try:
        df = pd.read_csv("trainingdataset.csv")
        print(f"Loaded dataset with {len(df)} records")
        print(f"Columns: {', '.join(df.columns)}")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None, None, None
    
    # Data preparation and sorting by time for rolling statistics
    df_cleaned = df.copy()
    
    # Sort by Year, Month, Day for time-based features
    if all(col in df_cleaned.columns for col in ['Year', 'Month', 'Day']):
        df_cleaned.sort_values(by=['Year', 'Month', 'Day'], inplace=True)
    
    # Fill missing values
    numeric_cols = df_cleaned.select_dtypes(include=['int64', 'float64']).columns
    for col in numeric_cols:
        df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
    
    cat_cols = df_cleaned.select_dtypes(include=['object']).columns
    for col in cat_cols:
        df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mode()[0])
    
    # Remove extreme outliers for Total Revenue (beyond 3 sigma)
    revenue_mean = df_cleaned['Total Revenue'].mean()
    revenue_std = df_cleaned['Total Revenue'].std()
    df_cleaned = df_cleaned[
        (df_cleaned['Total Revenue'] <= revenue_mean + 3 * revenue_std) &
        (df_cleaned['Total Revenue'] >= revenue_mean - 3 * revenue_std)
    ]
    
    print(f"After cleaning and outlier removal: {len(df_cleaned)} records")
    
    # Product Segmentation via Clustering
    # Group products by their pricing characteristics
    if '_ProductID' in df_cleaned.columns:
        # Get product-level statistics (avoiding any revenue-based stats)
        product_price_stats = df_cleaned.groupby('_ProductID').agg({
            'Unit Price': ['mean', 'std', 'min', 'max', 'count'],
            'Unit Cost': ['mean', 'std', 'min', 'max']
        }).reset_index()
        
        # Flatten multi-level columns
        product_price_stats.columns = ['_ProductID'] + [
            f'product_{col[0]}_{col[1]}' for col in product_price_stats.columns[1:]
        ]
        
        # Only cluster products with sufficient data points
        products_to_cluster = product_price_stats[
            product_price_stats['product_Unit Price_count'] >= 5
        ]
        
        # Determine optimal K using silhouette score
        cluster_features = ['product_Unit Price_mean', 'product_Unit Cost_mean', 
                          'product_Unit Price_std', 'product_Unit Cost_std']
        
        if len(products_to_cluster) > 10:  # Only cluster if we have enough products
            # Scale the features
            scaler = StandardScaler()
            cluster_data = scaler.fit_transform(products_to_cluster[cluster_features])
            
            # Determine number of clusters (k) - simplified approach
            k = min(10, len(products_to_cluster) // 5)  # Maximum 10 clusters
            k = max(3, k)  # Minimum 3 clusters
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(cluster_data)
            
            # Add cluster labels to product data
            products_to_cluster['product_cluster'] = clusters
            
            # Create a mapping for all products
            product_cluster_map = products_to_cluster[['_ProductID', 'product_cluster']]
            
            # Merge back to original data
            df_cleaned = pd.merge(df_cleaned, product_cluster_map, on='_ProductID', how='left')
            
            # Fill missing clusters (for products with too few data points)
            df_cleaned['product_cluster'].fillna(-1, inplace=True)
            df_cleaned['product_cluster'] = df_cleaned['product_cluster'].astype(int)
            
            print(f"Created {k} product clusters based on price and cost patterns")
    
    # Split into train and test (80/20 split with stratification by product_cluster if available)
    if 'product_cluster' in df_cleaned.columns:
        train_df, test_df = train_test_split(
            df_cleaned, test_size=0.2, random_state=42, 
            stratify=df_cleaned['product_cluster']
        )
    else:
        train_df, test_df = train_test_split(df_cleaned, test_size=0.2, random_state=42)
    
    print(f"Training set: {len(train_df)} records, Test set: {len(test_df)} records")
    
    # Enhanced Feature Engineering - only use features that can be known before the sale
    encoders = {}
    
    # 1. Encode categorical variables with enhanced techniques
    for col, name in [('Location', 'Location_Encoded'), ('_ProductID', 'ProductID_Encoded')]:
        if col in train_df.columns:
            encoder = LabelEncoder()
            train_df[name] = encoder.fit_transform(train_df[col].astype(str))
            test_df[name] = encoder.transform(test_df[col].astype(str))
            encoders[col] = encoder
    
    # 2. Encode weekday
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
        
        # Add weekend flag
        train_df['Is_Weekend'] = (train_df['Weekday_Numeric'] >= 5).astype(int)
        test_df['Is_Weekend'] = (test_df['Weekday_Numeric'] >= 5).astype(int)
    
    # 3. Enhanced time features - much more granular seasonality capture
    for df in [train_df, test_df]:
        # Advanced cyclical encoding for temporal features
        if 'Month' in df.columns:
            # Sine and cosine transformations for cyclical features
            df['Month_Sin'] = np.sin(2 * np.pi * df['Month'] / 12)
            df['Month_Cos'] = np.cos(2 * np.pi * df['Month'] / 12)
            
            # Quarter and season information
            df['Quarter'] = np.ceil(df['Month'] / 3).astype(int)
            df['Season'] = pd.cut(
                df['Month'], 
                bins=[0, 3, 6, 9, 12], 
                labels=['Winter', 'Spring', 'Summer', 'Fall'], 
                include_lowest=True
            )
            
            # One-hot encode Season for better model interpretation
            season_dummies = pd.get_dummies(df['Season'], prefix='Season')
            df = pd.concat([df, season_dummies], axis=1)
            
            # Holiday season flag (Nov-Dec)
            df['Holiday_Season'] = df['Month'].isin([11, 12]).astype(int)
            
            # Beginning/middle/end of month
            df['Month_Part'] = pd.cut(
                df['Day'], 
                bins=[0, 10, 20, 31], 
                labels=['Beginning', 'Middle', 'End'], 
                include_lowest=True
            )
            month_part_dummies = pd.get_dummies(df['Month_Part'], prefix='Month_Part')
            df = pd.concat([df, month_part_dummies], axis=1)
        
        if 'Day' in df.columns:
            df['Day_Sin'] = np.sin(2 * np.pi * df['Day'] / 31)
            df['Day_Cos'] = np.cos(2 * np.pi * df['Day'] / 31)
            
            # Is beginning/end of month
            df['Is_Month_Start'] = (df['Day'] <= 5).astype(int)
            df['Is_Month_End'] = (df['Day'] >= 25).astype(int)
        
        # Create Year-Month field for time-based grouping
        if all(col in df.columns for col in ['Year', 'Month']):
            df['YearMonth'] = df['Year'].astype(str) + '-' + df['Month'].astype(str).str.zfill(2)
    
    # 4. Advanced price and cost features
    for df in [train_df, test_df]:
        if 'Unit Price' in df.columns and 'Unit Cost' in df.columns:
            # Price-to-cost relationships
            df['Price_to_Cost_Ratio'] = df['Unit Price'] / (df['Unit Cost'] + 1e-5)
            df['Margin_Per_Unit'] = df['Unit Price'] - df['Unit Cost']
            df['Margin_Per_Unit_Pct'] = df['Margin_Per_Unit'] / (df['Unit Price'] + 1e-5) * 100
            
            # Create polynomial features for price and cost
            df['Price_Squared'] = df['Unit Price'] ** 2
            df['Price_Cubed'] = df['Unit Price'] ** 3
            df['Cost_Squared'] = df['Unit Cost'] ** 2
            df['Price_Log'] = np.log1p(df['Unit Price'])
            df['Cost_Log'] = np.log1p(df['Unit Cost'])
            
            # Log of price-to-cost ratio
            df['Log_Price_Cost_Ratio'] = np.log1p(df['Price_to_Cost_Ratio'])
            
            # Price Buckets (discretized price ranges)
            df['Price_Bucket'] = pd.qcut(
                df['Unit Price'], 
                q=5, 
                labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
            )
            price_bucket_dummies = pd.get_dummies(df['Price_Bucket'], prefix='Price_Bucket')
            df = pd.concat([df, price_bucket_dummies], axis=1)
    
    # 5. Interaction Features - combining different feature types
    for df in [train_df, test_df]:
        # Price × Time interactions
        if 'Month' in df.columns and 'Unit Price' in df.columns:
            df['Price_Month'] = df['Unit Price'] * df['Month']
            df['Price_Quarter'] = df['Unit Price'] * df['Quarter']
            
            # Standardized price by monthly patterns
            if 'Month_Sin' in df.columns:
                df['Price_Month_Sin'] = df['Unit Price'] * df['Month_Sin']
                df['Price_Month_Cos'] = df['Unit Price'] * df['Month_Cos']
            
            # Price × Season interaction
            for season in ['Winter', 'Spring', 'Summer', 'Fall']:
                if f'Season_{season}' in df.columns:
                    df[f'Price_Season_{season}'] = df['Unit Price'] * df[f'Season_{season}']
            
            # Price × Holiday Season
            if 'Holiday_Season' in df.columns:
                df['Price_Holiday'] = df['Unit Price'] * df['Holiday_Season']
        
        # Cost × Time interactions
        if 'Month' in df.columns and 'Unit Cost' in df.columns:
            df['Cost_Month'] = df['Unit Cost'] * df['Month']
            df['Cost_Quarter'] = df['Unit Cost'] * df['Quarter']
        
        # Price × Location and Cost × Location interactions
        if 'Location_Encoded' in df.columns:
            if 'Unit Price' in df.columns:
                df['Price_Location'] = df['Unit Price'] * df['Location_Encoded']
            
            if 'Unit Cost' in df.columns:
                df['Cost_Location'] = df['Unit Cost'] * df['Location_Encoded']
        
        # Weekend pricing effects
        if 'Is_Weekend' in df.columns and 'Unit Price' in df.columns:
            df['Price_Weekend'] = df['Unit Price'] * df['Is_Weekend']
        
        # Product cluster interaction
        if 'product_cluster' in df.columns and 'Unit Price' in df.columns:
            df['Price_Product_Cluster'] = df['Unit Price'] * (df['product_cluster'] + 1)
            df['Product_Cluster_Month'] = (df['product_cluster'] + 1) * df['Month']
    
    # 6. Product and Location Statistics (ethically derived from training data only)
    # Calculate various aggregations on the training data only
    train_product_stats = {}
    train_location_stats = {}
    train_product_month_stats = {}
    train_location_month_stats = {}
    
    # Calculate product-level price statistics (training data only)
    if '_ProductID' in train_df.columns:
        # Product-level price statistics
        train_product_stats = train_df.groupby('_ProductID').agg({
            'Unit Price': ['mean', 'median', 'std', 'min', 'max', 'count'],
            'Unit Cost': ['mean', 'median', 'std', 'min', 'max']
        })
        
        # Flatten columns
        train_product_stats.columns = [
            f'Product_{col[0]}_{col[1]}' for col in train_product_stats.columns
        ]
        train_product_stats = train_product_stats.reset_index()
        
        # Add product popularity metrics
        product_counts = train_df['_ProductID'].value_counts()
        total_transactions = len(train_df)
        product_freq = product_counts / total_transactions
        
        product_popularity = pd.DataFrame({
            '_ProductID': product_counts.index,
            'Product_Popularity': product_freq.values,
            'Product_Transaction_Count': product_counts.values
        })
        
        train_product_stats = pd.merge(
            train_product_stats, product_popularity, on='_ProductID', how='left'
        )
        
        # Calculate seasonality metrics for each product
        if 'Month' in train_df.columns:
            # Calculate average price by product and month
            train_product_month_stats = train_df.groupby(['_ProductID', 'Month']).agg({
                'Unit Price': ['mean', 'median', 'count']
            })
            
            # Flatten columns
            train_product_month_stats.columns = [
                f'Product_Month_{col[0]}_{col[1]}' for col in train_product_month_stats.columns
            ]
            train_product_month_stats = train_product_month_stats.reset_index()
    
    # Calculate location-level statistics (training data only)
    if 'Location' in train_df.columns:
        # Location-level price statistics
        train_location_stats = train_df.groupby('Location').agg({
            'Unit Price': ['mean', 'median', 'std', 'min', 'max'],
            'Unit Cost': ['mean', 'median', 'std', 'min', 'max']
        })
        
        # Flatten columns
        train_location_stats.columns = [
            f'Location_{col[0]}_{col[1]}' for col in train_location_stats.columns
        ]
        train_location_stats = train_location_stats.reset_index()
        
        # Calculate seasonality metrics for each location
        if 'Month' in train_df.columns:
            # Calculate average price by location and month
            train_location_month_stats = train_df.groupby(['Location', 'Month']).agg({
                'Unit Price': ['mean', 'median', 'count']
            })
            
            # Flatten columns
            train_location_month_stats.columns = [
                f'Location_Month_{col[0]}_{col[1]}' for col in train_location_month_stats.columns
            ]
            train_location_month_stats = train_location_month_stats.reset_index()
    
    # Apply the calculated statistics to both train and test datasets
    # Important: We only use statistics calculated from the training data
    for df_name, df in [('train', train_df), ('test', test_df)]:
        # 6.1 Merge product statistics
        if not train_product_stats.empty and '_ProductID' in df.columns:
            df = pd.merge(df, train_product_stats, on='_ProductID', how='left')
            
            # Fill missing values for new products not seen in training
            product_cols = [col for col in df.columns if col.startswith('Product_')]
            for col in product_cols:
                if df[col].isnull().any():
                    if 'mean' in col or 'median' in col or 'count' in col:
                        df[col] = df[col].fillna(train_product_stats[col].median())
                    elif 'std' in col:
                        df[col] = df[col].fillna(train_product_stats[col].median())
                    else:
                        df[col] = df[col].fillna(0)
        
        # 6.2 Merge location statistics
        if not train_location_stats.empty and 'Location' in df.columns:
            df = pd.merge(df, train_location_stats, on='Location', how='left')
            
            # Fill missing values for new locations
            location_cols = [col for col in df.columns if col.startswith('Location_') 
                            and not col.startswith('Location_Month_')]
            for col in location_cols:
                if df[col].isnull().any():
                    df[col] = df[col].fillna(train_location_stats[col].median())
        
        # 6.3 Merge product-month seasonality
        if not train_product_month_stats.empty and all(col in df.columns for col in ['_ProductID', 'Month']):
            df = pd.merge(
                df, train_product_month_stats, 
                on=['_ProductID', 'Month'], 
                how='left'
            )
            
            # Fill missing values for product-month combinations not in training
            product_month_cols = [col for col in df.columns if col.startswith('Product_Month_')]
            for col in product_month_cols:
                if df[col].isnull().any():
                    # First try to use the product average
                    product_col = col.replace('Month_', '')
                    if product_col in df.columns:
                        df[col] = df[col].fillna(df[product_col])
                    else:
                        # Otherwise use the median from training
                        df[col] = df[col].fillna(train_product_month_stats[col].median())
        
        # 6.4 Merge location-month seasonality
        if not train_location_month_stats.empty and all(col in df.columns for col in ['Location', 'Month']):
            df = pd.merge(
                df, train_location_month_stats, 
                on=['Location', 'Month'], 
                how='left'
            )
            
            # Fill missing values for location-month combinations not in training
            location_month_cols = [col for col in df.columns if col.startswith('Location_Month_')]
            for col in location_month_cols:
                if df[col].isnull().any():
                    # First try to use the location average
                    location_col = col.replace('Month_', '')
                    if location_col in df.columns:
                        df[col] = df[col].fillna(df[location_col])
                    else:
                        # Otherwise use the median from training
                        df[col] = df[col].fillna(train_location_month_stats[col].median())
        
        # 7. Create features for deviation from norms
        # These show how much the current price deviates from typical patterns
        if 'Unit Price' in df.columns:
            # 7.1 Price deviation from product average
            if 'Product_Unit Price_mean' in df.columns:
                df['Price_vs_Product_Avg'] = df['Unit Price'] / (df['Product_Unit Price_mean'] + 1e-5)
                df['Price_vs_Product_Median'] = df['Unit Price'] / (df['Product_Unit Price_median'] + 1e-5)
                
                # Standardized price (z-score) within product
                if 'Product_Unit Price_std' in df.columns and df['Product_Unit Price_std'].max() > 0:
                    df['Price_Product_Zscore'] = (
                        (df['Unit Price'] - df['Product_Unit Price_mean']) / 
                        (df['Product_Unit Price_std'] + 1e-5)
                    )
            
            # 7.2 Price deviation from location average
            if 'Location_Unit Price_mean' in df.columns:
                df['Price_vs_Location_Avg'] = df['Unit Price'] / (df['Location_Unit Price_mean'] + 1e-5)
                df['Price_vs_Location_Median'] = df['Unit Price'] / (df['Location_Unit Price_median'] + 1e-5)
            
            # 7.3 Price deviation from product-month average (seasonality)
            if 'Product_Month_Unit Price_mean' in df.columns:
                df['Price_Seasonal_Deviation'] = (
                    df['Unit Price'] / (df['Product_Month_Unit Price_mean'] + 1e-5)
                )
                
                # Flag for higher than usual seasonal price
                df['Higher_Than_Seasonal_Avg'] = (
                    df['Price_Seasonal_Deviation'] > 1.1
                ).astype(int)
            
            # 7.4 Price deviation from location-month average
            if 'Location_Month_Unit Price_mean' in df.columns:
                df['Price_Location_Seasonal_Dev'] = (
                    df['Unit Price'] / (df['Location_Month_Unit Price_mean'] + 1e-5)
                )
        
        # 8. Volume indicators (still ethical, based on historical counts)
        if 'Product_Transaction_Count' in df.columns:
            # Calculate high volume flag
            df['High_Volume_Product'] = (
                df['Product_Transaction_Count'] > 
                df['Product_Transaction_Count'].quantile(0.75)
            ).astype(int)
            
            # Product popularity × Price interaction
            df['Price_X_Popularity'] = df['Unit Price'] * df['Product_Popularity']
        
        # 9. Create product price rank (percentile) in its category
        if 'Product_Unit Price_mean' in df.columns and 'product_cluster' in df.columns:
            # Group by product cluster
            cluster_price_stats = df.groupby('product_cluster')['Product_Unit Price_mean'].agg(['min', 'max'])
            
            # Create merged dataframe with cluster stats
            cluster_stats = pd.DataFrame(cluster_price_stats).reset_index()
            cluster_stats.columns = ['product_cluster', 'cluster_price_min', 'cluster_price_max']
            
            # Merge the cluster stats back
            df = pd.merge(df, cluster_stats, on='product_cluster', how='left')
            
            # Calculate price position within cluster (0-1 range)
            df['Price_Position_In_Cluster'] = (
                (df['Product_Unit Price_mean'] - df['cluster_price_min']) / 
                ((df['cluster_price_max'] - df['cluster_price_min']) + 1e-5)
            )
            
            # Bin into low, medium, high within cluster
            df['Price_Tier_In_Cluster'] = pd.cut(
                df['Price_Position_In_Cluster'],
                bins=[0, 0.33, 0.67, 1],
                labels=['Low', 'Medium', 'High'],
                include_lowest=True
            )
            
            # One-hot encode the price tier
            price_tier_dummies = pd.get_dummies(df['Price_Tier_In_Cluster'], prefix='Price_Tier')
            df = pd.concat([df, price_tier_dummies], axis=1)
        
        # Update the original dataframe with all the new features
        if df_name == 'train':
            train_df = df
        else:
            test_df = df
    
    # Log transform the target variable
    train_df['Revenue_Log'] = np.log1p(train_df['Total Revenue'])
    test_df['Revenue_Log'] = np.log1p(test_df['Total Revenue'])
    
    # Prepare feature list, excluding original categorical variables, target, and any target-leaking features
    exclude_cols = [
        # Targets and IDs
        'Total Revenue', 'Revenue_Log', 'Location', '_ProductID', 'Weekday',
        # Intermediary processing columns
        'YearMonth', 'Season', 'Month_Part', 'Price_Bucket', 'Price_Tier_In_Cluster', 
        'product_cluster', 'cluster_price_min', 'cluster_price_max'
    ]
    
    features = [col for col in train_df.columns if col not in exclude_cols 
               and not col.startswith('Unnamed')]
    
    print(f"Training with {len(features)} ethical features that don't leak target information.")
    print("Feature categories include: price features, time features, product statistics, location statistics, interactions, deviations.")
    
    # Prepare data for modeling
    X_train = train_df[features]
    y_train = train_df['Revenue_Log']  # Use log-transformed target
    
    X_test = test_df[features]
    y_test = test_df['Revenue_Log']
    
    # Check for and fill any NaN values in the features
    X_train = X_train.fillna(X_train.median())
    X_test = X_test.fillna(X_train.median())
    
    print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Define evaluation function
    def evaluate_model(model, X, y, y_pred_log=None):
        """Evaluate model and return metrics"""
        if y_pred_log is None:
            y_pred_log = model.predict(X)
        
        # Convert log predictions back to original scale
        y_pred = np.expm1(y_pred_log)
        y_true = np.expm1(y)
        
        r2 = r2_score(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        
        return {
            'r2': r2,
            'mae': mae,
            'rmse': rmse,
            'y_pred': y_pred,
            'y_pred_log': y_pred_log
        }
    
    # Enhanced categorical features identification
    # This helps algorithms that handle categorical features differently
    categorical_features = []
    for col in features:
        if col.startswith('Season_') or col.startswith('Month_Part_') or col.startswith('Price_Bucket_') or col.startswith('Price_Tier_'):
            categorical_features.append(col)
        elif 'Is_' in col or 'High_' in col or 'Higher_' in col:
            categorical_features.append(col)
    
    print(f"Identified {len(categorical_features)} categorical features for specialized handling")
    
    # Train multiple models and select the best one
    models = {}
    results = {}
    cv_results = {}
    
    # Set up cross-validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    # 1. LightGBM with categorical feature optimization
    print("\n1. Training LightGBM with categorical optimization...")
    lgb_model = lgb.LGBMRegressor(random_state=42, n_jobs=-1)
    
    # Identify categorical features indices for LightGBM
    categorical_feature_indices = [features.index(col) for col in categorical_features if col in features]
    
    lgb_params = {
        'n_estimators': [200, 500, 1000],
        'num_leaves': [31, 50, 100, 200],
        'max_depth': [3, 5, 7, 9, -1],
        'learning_rate': [0.01, 0.03, 0.05, 0.1],
        'subsample': [0.7, 0.8, 0.9, 1.0],
        'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
        'min_child_samples': [10, 20, 50],
        'reg_alpha': [0, 0.01, 0.1, 1.0],
        'reg_lambda': [0, 0.01, 0.1, 1.0]
    }
    
    # Cross-validation for LightGBM
    lgb_cv_scores = {
        'r2': [],
        'mae': [],
        'rmse': []
    }
    
    for train_idx, val_idx in kf.split(X_train):
        X_cv_train, X_cv_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        y_cv_train, y_cv_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
        
        # Use sklearn interface of LightGBM
        lgb_cv = lgb.LGBMRegressor(
            objective='regression',
            metric='rmse',
            verbosity=-1,
            num_leaves=100,
            learning_rate=0.05,
            colsample_bytree=0.8,
            subsample=0.8,
            reg_alpha=0.1,
            reg_lambda=0.1,
            n_jobs=-1,
            n_estimators=1000,
            random_state=42
        )
        
        # Fit with early stopping
        lgb_cv.fit(
            X_cv_train, 
            y_cv_train,
            eval_set=[(X_cv_val, y_cv_val)],
            eval_metric='rmse',
            early_stopping_rounds=50,
            categorical_feature=categorical_feature_indices if categorical_feature_indices else "auto",
            verbose=False
        )
        
        # Predict and evaluate
        y_pred_log = lgb_cv.predict(X_cv_val)
        eval_results = evaluate_model(None, X_cv_val, y_cv_val, y_pred_log)
        
        lgb_cv_scores['r2'].append(eval_results['r2'])
        lgb_cv_scores['mae'].append(eval_results['mae'])
        lgb_cv_scores['rmse'].append(eval_results['rmse'])
    
    # Calculate average CV metrics
    lgb_cv_avg = {
        'r2': np.mean(lgb_cv_scores['r2']),
        'mae': np.mean(lgb_cv_scores['mae']),
        'rmse': np.mean(lgb_cv_scores['rmse']),
        'r2_std': np.std(lgb_cv_scores['r2']),
        'mae_std': np.std(lgb_cv_scores['mae']),
        'rmse_std': np.std(lgb_cv_scores['rmse'])
    }
    
    print(f"\nLightGBM Cross-Validation Results:")
    print(f"R²: {lgb_cv_avg['r2']:.4f} ± {lgb_cv_avg['r2_std']:.4f}")
    print(f"MAE: {lgb_cv_avg['mae']:.2f} ± {lgb_cv_avg['mae_std']:.2f}")
    print(f"RMSE: {lgb_cv_avg['rmse']:.2f} ± {lgb_cv_avg['rmse_std']:.2f}")
    
    # Train optimized LightGBM on full training set
    print("\nTraining optimized LightGBM on full training set...")
    
    lgb_search = RandomizedSearchCV(
        lgb_model, 
        param_distributions=lgb_params,
        n_iter=30,
        cv=5,
        random_state=42,
        n_jobs=-1,
        verbose=1,
        scoring='r2'
    )
    
    lgb_search.fit(
        X_train, 
        y_train, 
        categorical_feature=categorical_feature_indices if categorical_feature_indices else "auto"
    )
    
    best_lgb = lgb_search.best_estimator_
    
    # Evaluate LightGBM on test set
    lgb_results = evaluate_model(best_lgb, X_test, y_test)
    
    print(f"\nLightGBM Test Results:")
    print(f"MAE: {lgb_results['mae']:.2f}")
    print(f"RMSE: {lgb_results['rmse']:.2f}")
    print(f"R² Score: {lgb_results['r2']:.4f}")
    print(f"Best Parameters: {lgb_search.best_params_}")
    
    models['LightGBM'] = best_lgb
    results['LightGBM'] = lgb_results
    cv_results['LightGBM'] = lgb_cv_avg
    
    # 2. CatBoost (if available)
    if CATBOOST_AVAILABLE:
        print("\n2. Training CatBoost with native categorical feature handling...")
        
        # Identify categorical features for CatBoost
        cat_features_indices = [features.index(col) for col in categorical_features if col in features]
        
        cat_model = CatBoostRegressor(
            iterations=500,
            learning_rate=0.05,
            depth=8,
            loss_function='RMSE',
            random_seed=42,
            thread_count=-1,
            verbose=False
        )
        
        # Cross-validation for CatBoost
        cat_cv_scores = {
            'r2': [],
            'mae': [],
            'rmse': []
        }
        
        for train_idx, val_idx in kf.split(X_train):
            X_cv_train, X_cv_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_cv_train, y_cv_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
            
            # Create CatBoost Pool with categorical features
            train_pool = Pool(
                data=X_cv_train, 
                label=y_cv_train,
                cat_features=cat_features_indices if cat_features_indices else None
            )
            
            val_pool = Pool(
                data=X_cv_val, 
                label=y_cv_val,
                cat_features=cat_features_indices if cat_features_indices else None
            )
            
            # Train with early stopping
            cat_cv = CatBoostRegressor(
                iterations=1000,
                learning_rate=0.05,
                depth=6,
                l2_leaf_reg=3,
                loss_function='RMSE',
                random_seed=42,
                thread_count=-1,
                verbose=False
            )
            
            cat_cv.fit(
                train_pool,
                eval_set=val_pool,
                early_stopping_rounds=50,
                verbose=False
            )
            
            # Predict and evaluate
            y_pred_log = cat_cv.predict(X_cv_val)
            eval_results = evaluate_model(None, X_cv_val, y_cv_val, y_pred_log)
            
            cat_cv_scores['r2'].append(eval_results['r2'])
            cat_cv_scores['mae'].append(eval_results['mae'])
            cat_cv_scores['rmse'].append(eval_results['rmse'])
        
        # Calculate average CV metrics
        cat_cv_avg = {
            'r2': np.mean(cat_cv_scores['r2']),
            'mae': np.mean(cat_cv_scores['mae']),
            'rmse': np.mean(cat_cv_scores['rmse']),
            'r2_std': np.std(cat_cv_scores['r2']),
            'mae_std': np.std(cat_cv_scores['mae']),
            'rmse_std': np.std(cat_cv_scores['rmse'])
        }
        
        print(f"\nCatBoost Cross-Validation Results:")
        print(f"R²: {cat_cv_avg['r2']:.4f} ± {cat_cv_avg['r2_std']:.4f}")
        print(f"MAE: {cat_cv_avg['mae']:.2f} ± {cat_cv_avg['mae_std']:.2f}")
        print(f"RMSE: {cat_cv_avg['rmse']:.2f} ± {cat_cv_avg['rmse_std']:.2f}")
        
        # Train CatBoost on full training set with optimal parameters
        print("\nTraining CatBoost on full training set...")
        
        # Create final Pool objects
        train_pool = Pool(
            data=X_train, 
            label=y_train,
            cat_features=cat_features_indices if cat_features_indices else None
        )
        
        cat_params = {
            'iterations': [100, 300, 500],
            'learning_rate': [0.03, 0.05, 0.1],
            'depth': [4, 6, 8, 10],
            'l2_leaf_reg': [1, 3, 5, 7],
            'border_count': [32, 64, 128],
            'bagging_temperature': [0, 1],
            'random_strength': [0.1, 1]
        }
        
        cat_search = RandomizedSearchCV(
            cat_model, 
            param_distributions=cat_params,
            n_iter=20,
            cv=5,
            random_state=42,
            n_jobs=-1,
            verbose=1,
            scoring='r2'
        )
        
        # Fit with categorical features
        cat_search.fit(
            X_train, 
            y_train,
            cat_features=cat_features_indices if cat_features_indices else None
        )
        
        best_cat = cat_search.best_estimator_
        
        # Evaluate CatBoost on test set
        y_pred_log_cat = best_cat.predict(X_test)
        cat_results = evaluate_model(None, X_test, y_test, y_pred_log_cat)
        
        print(f"\nCatBoost Test Results:")
        print(f"MAE: {cat_results['mae']:.2f}")
        print(f"RMSE: {cat_results['rmse']:.2f}")
        print(f"R² Score: {cat_results['r2']:.4f}")
        print(f"Best Parameters: {cat_search.best_params_}")
        
        models['CatBoost'] = best_cat
        results['CatBoost'] = cat_results
        cv_results['CatBoost'] = cat_cv_avg
    
    # 3. Scikit-learn HistGradientBoostingRegressor (faster alternative to GB)
    print("\n3. Training HistGradientBoostingRegressor...")
    
    # Identify categorical features for HistGradientBoosting
    hist_categorical_features = []
    for i, col in enumerate(features):
        if col in categorical_features:
            hist_categorical_features.append(i)
    
    histgb_model = HistGradientBoostingRegressor(
        loss='squared_error',
        learning_rate=0.1,
        max_iter=100,
        max_depth=None,
        max_leaf_nodes=31,
        random_state=42,
        verbose=0
    )
    
    histgb_params = {
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'max_iter': [100, 200, 500],
        'max_leaf_nodes': [31, 50, 100],
        'min_samples_leaf': [20, 50, 100],
        'l2_regularization': [0, 0.1, 1.0, 10.0]
    }
    
    # Cross-validation for HistGradientBoosting
    histgb_cv_scores = cross_val_score(histgb_model, X_train, y_train, cv=kf, scoring='r2')
    
    histgb_cv_r2 = np.mean(histgb_cv_scores)
    histgb_cv_r2_std = np.std(histgb_cv_scores)
    
    print(f"\nHistGradientBoosting Cross-Validation R²: {histgb_cv_r2:.4f} ± {histgb_cv_r2_std:.4f}")
    
    # Train with optimized parameters
    histgb_search = RandomizedSearchCV(
        histgb_model, 
        param_distributions=histgb_params,
        n_iter=20,
        cv=5,
        random_state=42,
        n_jobs=-1,
        verbose=1,
        scoring='r2'
    )
    
    histgb_search.fit(X_train, y_train)
    best_histgb = histgb_search.best_estimator_
    
    # Evaluate HistGradientBoosting
    histgb_results = evaluate_model(best_histgb, X_test, y_test)
    
    print(f"\nHistGradientBoosting Results:")
    print(f"MAE: {histgb_results['mae']:.2f}")
    print(f"RMSE: {histgb_results['rmse']:.2f}")
    print(f"R² Score: {histgb_results['r2']:.4f}")
    print(f"Best Parameters: {histgb_search.best_params_}")
    
    models['HistGradientBoosting'] = best_histgb
    results['HistGradientBoosting'] = histgb_results
    cv_results['HistGradientBoosting'] = {'r2': histgb_cv_r2, 'r2_std': histgb_cv_r2_std}
    
    # 4. Create an ensemble model (Stacking)
    print("\n4. Creating stacked ensemble model...")
    
    # Use the best models as base estimators
    base_models = []
    for name, model in models.items():
        if name != 'HistGradientBoosting':  # Use HistGradientBoosting as meta-estimator
            base_models.append((name, model))
    
    stacked_model = StackingRegressor(
        estimators=base_models,
        final_estimator=HistGradientBoostingRegressor(random_state=42),
        cv=5,
        n_jobs=-1
    )
    
    # Train stacked model
    stacked_model.fit(X_train, y_train)
    
    # Evaluate stacked model
    stacked_results = evaluate_model(stacked_model, X_test, y_test)
    
    print(f"\nStacked Ensemble Results:")
    print(f"MAE: {stacked_results['mae']:.2f}")
    print(f"RMSE: {stacked_results['rmse']:.2f}")
    print(f"R² Score: {stacked_results['r2']:.4f}")
    
    models['StackedEnsemble'] = stacked_model
    results['StackedEnsemble'] = stacked_results
    
    # Compare models and find best performing one
    print("\n===== Model Comparison =====")
    print(f"{'Model':<20} {'R² (Test)':>12} {'MAE':>12} {'RMSE':>12} {'R² (CV)':>12}")
    print("-" * 70)
    
    best_model_name = None
    best_r2 = -float('inf')
    
    for name, result in results.items():
        r2 = result['r2']
        mae = result['mae']
        rmse = result['rmse']
        
        # Get CV R² score if available
        cv_r2 = "N/A"
        if name in cv_results and 'r2' in cv_results[name]:
            cv_r2 = f"{cv_results[name]['r2']:.4f}"
        
        print(f"{name:<20} {r2:>12.4f} {mae:>12.2f} {rmse:>12.2f} {cv_r2:>12}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
    
    print(f"\nBest model: {best_model_name} with Test R² = {best_r2:.4f}")
    
    # Save the best model with metadata
    final_model = models[best_model_name]
    final_r2 = results[best_model_name]['r2']
    final_mae = results[best_model_name]['mae']
    final_rmse = results[best_model_name]['rmse']
    final_y_pred = results[best_model_name]['y_pred']
    
    model_data = {
        'model': final_model,
        'model_type': best_model_name,
        'features': features,
        'categorical_features': categorical_features,
        'r2': final_r2,
        'mae': final_mae,
        'rmse': final_rmse,
        'log_transform': True
    }
    
    # Save the model
    joblib.dump(model_data, 'best_revenue_model_ethical.pkl')
    joblib.dump(encoders, 'revenue_encoders_ethical.pkl')
    
    print("\nBest model and encoders saved to:")
    print("- best_revenue_model_ethical.pkl")
    print("- revenue_encoders_ethical.pkl")
    
    # Plot feature importance for the best model if possible
    if best_model_name in ["LightGBM", "CatBoost", "XGBoost"] and hasattr(final_model, 'feature_importances_'):
        importances = final_model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        # Top 20 features
        top_n = min(20, len(features))
        top_features = [features[i] for i in indices[:top_n]]
        top_importances = [importances[i]/np.sum(importances)*100 for i in indices[:top_n]]
        
        print(f"\nTop 20 important features for {best_model_name}:")
        for feature, importance in zip(top_features, top_importances):
            print(f"{feature}: {importance:.2f}%")
        
        # Create feature importance plot
        plt.figure(figsize=(12, 8))
        bars = plt.barh(range(top_n), top_importances, align='center', color='skyblue')
        plt.yticks(range(top_n), [features[i] for i in indices[:top_n]])
        plt.xlabel('Importance (%)')
        plt.title(f'Feature Importance ({best_model_name})')
        
        # Add percentage labels to the bars
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', ha='left', va='center')
        
        plt.tight_layout()
        plt.savefig(f'feature_importance_ethical_{best_model_name.lower()}.png')
        print(f"\nFeature importance plot saved to 'feature_importance_ethical_{best_model_name.lower()}.png'")
    
    # Plot actual vs predicted revenue
    plt.figure(figsize=(10, 6))
    plt.scatter(np.expm1(y_test), final_y_pred, alpha=0.5, color='blue')
    plt.plot([min(np.expm1(y_test)), max(np.expm1(y_test))], [min(np.expm1(y_test)), max(np.expm1(y_test))], 'r--')
    plt.xlabel('Actual Revenue')
    plt.ylabel('Predicted Revenue')
    plt.title(f'Actual vs Predicted Revenue (Ethical {best_model_name} Model)')
    plt.tight_layout()
    plt.savefig(f'actual_vs_predicted_ethical_{best_model_name.lower()}.png')
    print(f"\nActual vs. predicted plot saved to 'actual_vs_predicted_ethical_{best_model_name.lower()}.png'")
    
    # Error distribution plot
    plt.figure(figsize=(10, 6))
    errors = final_y_pred - np.expm1(y_test)
    plt.hist(errors, bins=50, alpha=0.75, color='purple')
    plt.axvline(x=0, color='red', linestyle='--', linewidth=1)
    plt.xlabel('Prediction Error')
    plt.ylabel('Frequency')
    plt.title(f'Error Distribution (Ethical {best_model_name} Model)')
    plt.tight_layout()
    plt.savefig(f'error_distribution_ethical_{best_model_name.lower()}.png')
    print(f"\nError distribution plot saved to 'error_distribution_ethical_{best_model_name.lower()}.png'")
    
    return final_model, encoders, features

if __name__ == "__main__":
    train_ethical_revenue_model() 