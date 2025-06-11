import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import matplotlib.pyplot as plt
from datetime import datetime

print("=== ENHANCED TIME-BASED ETHICAL MODEL TRAINING ===")
print("Training a model with improved time features but NO TARGET LEAKAGE")
print("This model uses only features that would be available at prediction time")

# Load and prepare data
print("\nLoading dataset...")
df = pd.read_csv('trainingdataset.csv')
print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# Fix weekday if it's numeric
if 'Weekday' in df.columns and pd.api.types.is_numeric_dtype(df['Weekday']):
    # Convert numeric weekday to string names
    weekday_map = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    df['Weekday'] = df['Weekday'].map(weekday_map)

# Feature engineering - Basic
print("\nPerforming ethical feature engineering (no target leakage)...")

# 1. Standard price features
df['Price_to_Cost_Ratio'] = df['Unit Price'] / df['Unit Cost']
df['Margin_Per_Unit'] = df['Unit Price'] - df['Unit Cost']
df['Margin_Per_Unit_Pct'] = (df['Margin_Per_Unit'] / df['Unit Price']) * 100
df['Price_Squared'] = df['Unit Price'] ** 2
df['Price_Log'] = np.log1p(df['Unit Price'])

# 2. ENHANCED TIME FEATURES
# Create a proper date column
df['Date'] = pd.to_datetime(df[['Year', 'Month', 'Day']].assign(Day=df['Day'].clip(1, 28)))

# Add day of year (1-366)
df['Day_of_Year'] = df['Date'].dt.dayofyear

# Add week of year (1-53)
df['Week_of_Year'] = df['Date'].dt.isocalendar().week

# Better cyclical encoding of time
df['Month_Sin'] = np.sin(2 * np.pi * df['Month'] / 12)
df['Month_Cos'] = np.cos(2 * np.pi * df['Month'] / 12)
df['Day_Sin'] = np.sin(2 * np.pi * df['Day'] / 31)
df['Day_Cos'] = np.cos(2 * np.pi * df['Day'] / 31)
df['Day_of_Year_Sin'] = np.sin(2 * np.pi * df['Day_of_Year'] / 366)
df['Day_of_Year_Cos'] = np.cos(2 * np.pi * df['Day_of_Year'] / 366)
df['Week_of_Year_Sin'] = np.sin(2 * np.pi * df['Week_of_Year'] / 53)
df['Week_of_Year_Cos'] = np.cos(2 * np.pi * df['Week_of_Year'] / 53)

# Quarter
df['Quarter'] = (df['Month'] - 1) // 3 + 1

# Seasons (Northern Hemisphere)
df['Is_Winter'] = ((df['Month'] == 12) | (df['Month'] == 1) | (df['Month'] == 2)).astype(int)
df['Is_Spring'] = ((df['Month'] == 3) | (df['Month'] == 4) | (df['Month'] == 5)).astype(int)
df['Is_Summer'] = ((df['Month'] == 6) | (df['Month'] == 7) | (df['Month'] == 8)).astype(int)
df['Is_Fall'] = ((df['Month'] == 9) | (df['Month'] == 10) | (df['Month'] == 11)).astype(int)

# Holiday season (Nov-Dec)
df['Is_Holiday_Season'] = ((df['Month'] == 11) | (df['Month'] == 12)).astype(int)

# Weekend
df['Is_Weekend'] = df['Weekday'].isin(['Saturday', 'Sunday']).astype(int)

# Holiday flags
holidays = [
    # USA holidays - simplified dates
    (1, 1),    # New Year's Day
    (7, 4),    # Independence Day
    (12, 25),  # Christmas
    (11, 25),  # Thanksgiving-ish (approximation)
    (5, 30),   # Memorial Day-ish (approximation)
    (9, 5),    # Labor Day-ish (approximation)
    (2, 14),   # Valentine's Day
    (10, 31),  # Halloween
]
df['Is_Holiday'] = df.apply(lambda row: 1 if (row['Month'], row['Day']) in holidays else 0, axis=1)

# 3. Product and Location features - AVOID using target data
# Calculate price and cost stats by product using only information available at prediction time
product_price_stats = df.groupby('_ProductID')['Unit Price'].agg(['mean', 'std', 'min', 'max'])
product_price_stats.columns = ['Product_Unit Price_mean', 'Product_Unit Price_std', 
                              'Product_Unit Price_min', 'Product_Unit Price_max']
df = df.merge(product_price_stats, on='_ProductID', how='left')

# Product cost stats
product_cost_stats = df.groupby('_ProductID')['Unit Cost'].agg(['mean'])
product_cost_stats.columns = ['Product_Unit Cost_mean']
df = df.merge(product_cost_stats, on='_ProductID', how='left')

# Product popularity (count of sales) - Ethical approach that doesn't use revenue
product_counts = df.groupby('_ProductID').size().reset_index(name='Product_Popularity')
df = df.merge(product_counts, on='_ProductID', how='left')

# Location price stats
location_price_stats = df.groupby('Location')['Unit Price'].agg(['mean', 'std', 'min', 'max'])
location_price_stats.columns = ['Location_Unit Price_mean', 'Location_Unit Price_std',
                               'Location_Unit Price_min', 'Location_Unit Price_max']
df = df.merge(location_price_stats, on='Location', how='left')

# Location cost stats
location_cost_stats = df.groupby('Location')['Unit Cost'].agg(['mean'])
location_cost_stats.columns = ['Location_Unit Cost_mean']
df = df.merge(location_cost_stats, on='Location', how='left')

# 4. TIME INTERACTION FEATURES - ETHICAL VERSIONS WITHOUT TARGET LEAKAGE
# Product-Month interactions (seasonal product patterns) - use price instead of revenue
product_month_stats = df.groupby(['_ProductID', 'Month'])['Unit Price'].agg(['mean']).reset_index()
product_month_stats.columns = ['_ProductID', 'Month', 'Product_Month_Unit Price_mean']
df = df.merge(product_month_stats, on=['_ProductID', 'Month'], how='left')

# Product-Quarter interactions 
product_quarter_stats = df.groupby(['_ProductID', 'Quarter'])['Unit Price'].agg(['mean']).reset_index()
product_quarter_stats.columns = ['_ProductID', 'Quarter', 'Product_Quarter_Unit Price_mean']
df = df.merge(product_quarter_stats, on=['_ProductID', 'Quarter'], how='left')

# Location-Month interactions (regional seasonal patterns)
location_month_stats = df.groupby(['Location', 'Month'])['Unit Price'].agg(['mean']).reset_index()
location_month_stats.columns = ['Location', 'Month', 'Location_Month_Unit Price_mean']
df = df.merge(location_month_stats, on=['Location', 'Month'], how='left')

# Weekend-Location interactions - using price, not revenue
weekend_location_stats = df.groupby(['Location', 'Is_Weekend'])['Unit Price'].agg(['mean']).reset_index()
weekend_location_stats.columns = ['Location', 'Is_Weekend', 'Location_Weekend_Price_mean']
df = df.merge(weekend_location_stats, on=['Location', 'Is_Weekend'], how='left')

# Product-Weekend interactions - using price, not revenue
weekend_product_stats = df.groupby(['_ProductID', 'Is_Weekend'])['Unit Price'].agg(['mean']).reset_index()
weekend_product_stats.columns = ['_ProductID', 'Is_Weekend', 'Product_Weekend_Price_mean']
df = df.merge(weekend_product_stats, on=['_ProductID', 'Is_Weekend'], how='left')

# 5. Price comparison features
df['Price_vs_Product_Avg'] = df['Unit Price'] / df['Product_Unit Price_mean']
df['Price_vs_Location_Avg'] = df['Unit Price'] / df['Location_Unit Price_mean']
df['Price_Seasonal_Deviation'] = df['Unit Price'] / df['Product_Month_Unit Price_mean']

# 6. Feature interactions
df['Price_Popularity'] = df['Unit Price'] * df['Product_Popularity']
df['Price_Location'] = df['Unit Price'] * df['Location_Unit Price_mean']
df['Price_Month'] = df['Unit Price'] * df['Month']
df['Price_Quarter'] = df['Unit Price'] * df['Quarter']
df['Price_Holiday'] = df['Unit Price'] * df['Is_Holiday']
df['Price_Weekend'] = df['Unit Price'] * df['Is_Weekend']

print(f"Ethical feature engineering complete. Total features: {df.shape[1]}")

# Encode categorical variables
print("\nEncoding categorical variables...")
encoders = {}

# Location encoding
location_encoder = LabelEncoder()
df['Location_Encoded'] = location_encoder.fit_transform(df['Location'])
encoders['Location'] = location_encoder

# ProductID encoding
product_encoder = LabelEncoder()
df['ProductID_Encoded'] = product_encoder.fit_transform(df['_ProductID'].astype(str))
encoders['_ProductID'] = product_encoder

# Weekday encoding - Map to numeric values (0-6)
if not pd.api.types.is_numeric_dtype(df['Weekday']):
    weekday_map = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }
    df['Weekday_Numeric'] = df['Weekday'].map(weekday_map)
    encoders['Weekday'] = weekday_map
else:
    df['Weekday_Numeric'] = df['Weekday']
    encoders['Weekday'] = {i: i for i in range(7)}

# Define target and features
print("\nPreparing features and target...")
target = 'Total Revenue'
y = df[target]

# Log transform target (improves model performance)
y_log = np.log1p(y)

# Drop non-feature columns and any leaking columns 
exclude_columns = [
    'Date', 'Location', '_ProductID', 'Weekday', 'Total Revenue', 
    # Remove any columns that might contain target information
    'Month_Avg_Revenue', 'Weekday_Avg_Revenue', 'Revenue_Month_Ratio', 
    'Revenue_Weekday_Ratio', 'Location_Weekend_Revenue_mean', 'Product_Weekend_Revenue_mean'
]

# Check which columns exist and remove them
columns_to_drop = [col for col in exclude_columns if col in df.columns]
features = [col for col in df.columns if col not in columns_to_drop]

X = df[features]

# Save feature list
print(f"Total usable ethical features: {len(features)}")
print(f"First 10 features: {features[:10]}")

# Split data - 50/50 for direct comparison with existing model
print("\nSplitting data with 50/50 ratio...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_log, test_size=0.5, random_state=42
)

print(f"Training data: {X_train.shape[0]} samples")
print(f"Test data: {X_test.shape[0]} samples")

# Train LightGBM model with hyperparameter tuning
print("\nTraining LightGBM model...")

# Initial parameters
params = {
    'objective': 'regression',
    'metric': 'rmse',
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
    'verbose': -1,
    'n_jobs': -1
}

# Train the model
model = lgb.LGBMRegressor(**params)
model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    eval_metric='rmse',
    callbacks=[lgb.early_stopping(stopping_rounds=50)]
)

# Predict on test set (in log space)
y_pred_log = model.predict(X_test)

# Convert back from log space
y_pred = np.expm1(y_pred_log)
y_test_original = np.expm1(y_test)

# Calculate metrics
mae = mean_absolute_error(y_test_original, y_pred)
rmse = np.sqrt(mean_squared_error(y_test_original, y_pred))
r2 = r2_score(y_test_original, y_pred)

print("\nModel Performance:")
print(f"MAE: {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R²: {r2:.4f}")

# Feature importance
print("\nTop 15 features by importance:")
feature_importance = model.feature_importances_
importance_df = pd.DataFrame({
    'Feature': features,
    'Importance': feature_importance
}).sort_values('Importance', ascending=False)

for i, row in importance_df.head(15).iterrows():
    print(f"{row['Feature']}: {row['Importance'] * 100:.2f}%")

# Check time feature importance
time_features = [f for f in features if any(time_kw in f.lower() for time_kw in 
                                           ['month', 'day', 'year', 'week', 'weekend', 'holiday', 'season'])]
time_importance = importance_df[importance_df['Feature'].isin(time_features)]
total_time_importance = time_importance['Importance'].sum() * 100

print(f"\nTotal time feature importance: {total_time_importance:.2f}%")
print(f"Top 5 time features:")
for i, row in time_importance.head(5).iterrows():
    print(f"{row['Feature']}: {row['Importance'] * 100:.2f}%")

# Create model data dictionary
model_data = {
    'model': model,
    'features': features,
    'r2': r2,
    'mae': mae,
    'rmse': rmse,
    'params': params,
    'log_transform': True
}

# Save model, encoders and feature importance visualization
print("\nSaving model and encoders...")

# Save model data
joblib.dump(model_data, 'revenue_model_time_enhanced_ethical.pkl')

# Save encoders
joblib.dump(encoders, 'revenue_encoders_time_enhanced_ethical.pkl')

# Create feature importance plot
plt.figure(figsize=(12, 8))
importance_df.head(20).sort_values('Importance').plot(
    kind='barh', x='Feature', y='Importance', legend=False
)
plt.title('Top 20 Features by Importance (Ethical Time-Enhanced Model)')
plt.tight_layout()
plt.savefig('feature_importance_time_enhanced_ethical.png')

# Calculate training data statistics
print("\nCalculating training data statistics for reference...")
product_price_ref = df.groupby('_ProductID')['Unit Price'].mean().to_dict()
location_price_ref = df.groupby('Location')['Unit Price'].mean().to_dict()
product_cost_ref = df.groupby('_ProductID')['Unit Cost'].mean().to_dict()
location_cost_ref = df.groupby('Location')['Unit Cost'].mean().to_dict()

# Save reference data for prediction
reference_data = {
    'product_price_avg': product_price_ref,
    'location_price_avg': location_price_ref,
    'product_cost_avg': product_cost_ref,
    'location_cost_avg': location_cost_ref,
    'global_price_avg': df['Unit Price'].mean()
}
joblib.dump(reference_data, 'reference_data_time_enhanced_ethical.pkl')

print("\nModel training complete!")
print(f"Model saved as: revenue_model_time_enhanced_ethical.pkl")
print(f"Encoders saved as: revenue_encoders_time_enhanced_ethical.pkl")
print(f"Feature importance plot saved as: feature_importance_time_enhanced_ethical.png")
print(f"Reference data saved as: reference_data_time_enhanced_ethical.pkl")

# Create a script to compare with previous model
print("\nCreating comparison script...")

comparison_script = """
import pandas as pd
import numpy as np
import joblib
from tabulate import tabulate
import matplotlib.pyplot as plt

print("=== MODEL COMPARISON - ETHICAL VS NON-ETHICAL ===")

# Load models
time_enhanced_model = joblib.load('revenue_model_time_enhanced.pkl')
time_enhanced_ethical_model = joblib.load('revenue_model_time_enhanced_ethical.pkl')

# Print performance metrics
print("\\nPerformance Metrics:")
print(f"Non-Ethical Model R²: {time_enhanced_model.get('r2', 'N/A'):.4f}")
print(f"Non-Ethical Model MAE: {time_enhanced_model.get('mae', 'N/A'):.4f}")
print(f"Non-Ethical Model RMSE: {time_enhanced_model.get('rmse', 'N/A'):.4f}")

print(f"Ethical Model R²: {time_enhanced_ethical_model.get('r2', 'N/A'):.4f}")
print(f"Ethical Model MAE: {time_enhanced_ethical_model.get('mae', 'N/A'):.4f}")
print(f"Ethical Model RMSE: {time_enhanced_ethical_model.get('rmse', 'N/A'):.4f}")

# Compare features
non_ethical_features = time_enhanced_model.get('features', [])
ethical_features = time_enhanced_ethical_model.get('features', [])

print(f"\\nNon-Ethical Model Features: {len(non_ethical_features)}")
print(f"Ethical Model Features: {len(ethical_features)}")

# Find leaking features (in non-ethical but not in ethical)
leaking_features = set(non_ethical_features) - set(ethical_features)
print(f"\\nPotential Leaking Features: {len(leaking_features)}")
if leaking_features:
    print("Top leaking features:")
    for feature in sorted(list(leaking_features))[:10]:
        print(f"- {feature}")

# Create feature importance comparison
print("\\nTop 10 Features by Importance:")
print("\\nNon-Ethical Model:")
non_ethical_importance = pd.DataFrame({
    'Feature': non_ethical_features,
    'Importance': time_enhanced_model['model'].feature_importances_
}).sort_values('Importance', ascending=False)

for i, row in non_ethical_importance.head(10).iterrows():
    print(f"{row['Feature']}: {row['Importance'] * 100:.2f}%")

print("\\nEthical Model:")
ethical_importance = pd.DataFrame({
    'Feature': ethical_features,
    'Importance': time_enhanced_ethical_model['model'].feature_importances_
}).sort_values('Importance', ascending=False)

for i, row in ethical_importance.head(10).iterrows():
    print(f"{row['Feature']}: {row['Importance'] * 100:.2f}%")

# Create comparison plot
plt.figure(figsize=(12, 10))
plt.subplot(2, 1, 1)
non_ethical_importance.head(10).sort_values('Importance').plot(
    kind='barh', x='Feature', y='Importance', legend=False
)
plt.title('Top 10 Features (Non-Ethical Model)')

plt.subplot(2, 1, 2)
ethical_importance.head(10).sort_values('Importance').plot(
    kind='barh', x='Feature', y='Importance', legend=False
)
plt.title('Top 10 Features (Ethical Model)')

plt.tight_layout()
plt.savefig('model_comparison_ethical_vs_non_ethical.png')
print("Comparison plot saved as: model_comparison_ethical_vs_non_ethical.png")

print("\\nComparison complete!")
"""

with open('compare_ethical_vs_non_ethical_models.py', 'w') as f:
    f.write(comparison_script)

print("Created comparison script: compare_ethical_vs_non_ethical_models.py") 