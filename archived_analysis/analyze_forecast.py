import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
from revenue_predictor_50_50 import predict_revenue

# Set up test data for multiple dates
def generate_test_dates(start_date_str='2023-06-01', days=30):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    return [start_date + timedelta(days=i) for i in days_range]

# Basic test parameters
base_data = {
    'Unit Price': 100.00,
    'Unit Cost': 50.00,
    'Location': 'North',
    '_ProductID': 1
}

# Generate date ranges
days_range = range(30)
test_dates = [datetime(2023, 6, 1) + timedelta(days=i) for i in days_range]

print("=== FORECAST ANALYSIS ===")
print(f"Testing forecasts across {len(test_dates)} days with the same product and location")

# Make predictions for each date
results = []
for date in test_dates:
    # Create data for this date
    data = base_data.copy()
    data['Year'] = date.year
    data['Month'] = date.month
    data['Day'] = date.day
    data['Weekday'] = date.strftime('%A')
    
    # Make prediction
    try:
        prediction = predict_revenue(data)
        
        # Store results
        results.append({
            'date': date.strftime('%Y-%m-%d'),
            'weekday': date.strftime('%A'),
            'revenue': prediction.get('predicted_revenue', 0),
            'quantity': prediction.get('estimated_quantity', 0)
        })
    except Exception as e:
        print(f"Error predicting for {date}: {str(e)}")

# Convert to dataframe
results_df = pd.DataFrame(results)

# Analyze the variation in predictions
revenue_std = results_df['revenue'].std()
revenue_mean = results_df['revenue'].mean()
revenue_min = results_df['revenue'].min()
revenue_max = results_df['revenue'].max()
revenue_range = revenue_max - revenue_min

print("\n=== PREDICTION VARIATION ANALYSIS ===")
print(f"Revenue Mean: ${revenue_mean:.2f}")
print(f"Revenue Std Dev: ${revenue_std:.2f}")
print(f"Revenue Min: ${revenue_min:.2f}")
print(f"Revenue Max: ${revenue_max:.2f}")
print(f"Revenue Range: ${revenue_range:.2f}")
print(f"Coefficient of Variation: {(revenue_std/revenue_mean)*100:.2f}%")

# Calculate day-to-day changes
results_df['revenue_change'] = results_df['revenue'].diff()
avg_change = results_df['revenue_change'].mean()
max_change = results_df['revenue_change'].max()

print(f"\nAverage day-to-day change: ${avg_change:.2f}")
print(f"Maximum day-to-day change: ${max_change:.2f}")

# Analyze by weekday
weekday_avg = results_df.groupby('weekday')['revenue'].mean()
print("\nRevenue by weekday:")
for weekday, avg in weekday_avg.items():
    print(f"  {weekday}: ${avg:.2f}")

# Look at the detailed results
print("\nDetailed daily forecasts:")
for i, row in results_df.iterrows():
    print(f"  {row['date']} ({row['weekday']}): ${row['revenue']:.2f}")

# Analyze why variation might be low
print("\n=== ANALYSIS OF LOW VARIATION ===")
print("Possible reasons for flat forecasts:")
print("1. Time features are not affecting predictions - model may not have learned temporal patterns")
print("2. The model uses time features, but their importance is low in the model")
print("3. Missing transformations of time features (cyclical encodings, etc.)")
print("4. Not enough training data with temporal variation")
print("5. Preprocessing might be removing time-based variations")

# Recommendations
print("\n=== RECOMMENDATIONS ===")
print("1. Add enhanced time features:")
print("   - Cyclical encoding of month/day (sin/cos transformations)")
print("   - Day of year (1-366)")
print("   - Week of year (1-52)")
print("   - Is holiday/special period flags")
print("   - Season indicators")
print("   - Month-Product interaction terms")

print("\n2. Update model training script to include these features")
print("3. Retrain the model with these features")
print("4. Add proper temporal test cases to validate time-based patterns")
print("5. Update prediction pipeline to include the same feature engineering")

print("\n=== FEATURE ENGINEERING EXAMPLES ===")
print("# Cyclical encoding of month")
print("month_sin = np.sin(2 * np.pi * month / 12)")
print("month_cos = np.cos(2 * np.pi * month / 12)")
print("\n# Day of year")
print("day_of_year = date.timetuple().tm_yday")
print("\n# Is weekend")
print("is_weekend = 1 if date.weekday() >= 5 else 0")
print("\n# Quarter")
print("quarter = (month - 1) // 3 + 1") 