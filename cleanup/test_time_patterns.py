
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Load model and encoders
model_data = joblib.load('revenue_model_time_enhanced.pkl')
model = model_data['model']
features = model_data['features']

# Create test dates
start_date = datetime(2023, 1, 1)
days = 365
test_dates = [start_date + timedelta(days=i) for i in range(days)]

# Base scenario
base_data = {
    'Unit Price': 100.00,
    'Unit Cost': 50.00,
    'Location_Encoded': 0,  # Assuming first location
    'ProductID_Encoded': 0,  # Assuming first product
}

# Prepare test data for all dates
test_rows = []
for date in test_dates:
    data = base_data.copy()
    
    # Basic time features
    data['Year'] = date.year
    data['Month'] = date.month
    data['Day'] = date.day
    data['Weekday_Numeric'] = date.weekday()
    
    # Enhanced time features
    data['Day_of_Year'] = date.timetuple().tm_yday
    data['Week_of_Year'] = date.isocalendar()[1]
    
    data['Month_Sin'] = np.sin(2 * np.pi * date.month / 12)
    data['Month_Cos'] = np.cos(2 * np.pi * date.month / 12)
    data['Day_Sin'] = np.sin(2 * np.pi * date.day / 31)
    data['Day_Cos'] = np.cos(2 * np.pi * date.day / 31)
    data['Day_of_Year_Sin'] = np.sin(2 * np.pi * data['Day_of_Year'] / 366)
    data['Day_of_Year_Cos'] = np.cos(2 * np.pi * data['Day_of_Year'] / 366)
    data['Week_of_Year_Sin'] = np.sin(2 * np.pi * data['Week_of_Year'] / 53)
    data['Week_of_Year_Cos'] = np.cos(2 * np.pi * data['Week_of_Year'] / 53)
    
    # Quarter
    data['Quarter'] = (date.month - 1) // 3 + 1
    
    # Seasons
    data['Is_Winter'] = 1 if date.month in [12, 1, 2] else 0
    data['Is_Spring'] = 1 if date.month in [3, 4, 5] else 0
    data['Is_Summer'] = 1 if date.month in [6, 7, 8] else 0
    data['Is_Fall'] = 1 if date.month in [9, 10, 11] else 0
    
    # Holiday season
    data['Is_Holiday_Season'] = 1 if date.month in [11, 12] else 0
    
    # Weekend
    data['Is_Weekend'] = 1 if date.weekday() >= 5 else 0
    
    # Holidays
    holidays = [
        (1, 1),    # New Year's Day
        (7, 4),    # Independence Day
        (12, 25),  # Christmas
        (11, 25),  # Thanksgiving-ish
        (5, 30),   # Memorial Day-ish
        (9, 5),    # Labor Day-ish
        (2, 14),   # Valentine's Day
        (10, 31),  # Halloween
    ]
    data['Is_Holiday'] = 1 if (date.month, date.day) in holidays else 0
    
    # Fill in the remaining features with default values
    # This depends on your specific features and will need to be adapted
    
    test_rows.append({
        'date': date,
        'data': data
    })

# Create a DataFrame for prediction
X_test = pd.DataFrame([row['data'] for row in test_rows])

# Fill missing features with 0
for feature in features:
    if feature not in X_test.columns:
        X_test[feature] = 0

# Select only the features used by the model
X_test = X_test[features]

# Make predictions
predictions = model.predict(X_test)

# If using log transform, convert back
if model_data.get('log_transform', False):
    predictions = np.expm1(predictions)

# Create results DataFrame
results = pd.DataFrame({
    'Date': [row['date'] for row in test_rows],
    'Revenue': predictions
})

# Plot results
plt.figure(figsize=(15, 7))
plt.plot(results['Date'], results['Revenue'])
plt.title('Revenue Forecast Over Time (Enhanced Time Features)')
plt.xlabel('Date')
plt.ylabel('Revenue')
plt.grid(True)
plt.tight_layout()
plt.savefig('time_forecast_test.png')

# Calculate stats
weekly_avg = results.groupby(results['Date'].dt.isocalendar().week)['Revenue'].mean()
monthly_avg = results.groupby(results['Date'].dt.month)['Revenue'].mean()

# Print summary
print('=== TEMPORAL PATTERN VALIDATION ===')
print(f'Overall average revenue: ${results["Revenue"].mean():.2f}')
print(f'Standard deviation: ${results["Revenue"].std():.2f}')
print(f'Coefficient of variation: {results["Revenue"].std() / results["Revenue"].mean() * 100:.2f}%')

print('\nMonthly revenue pattern:')
for month, avg in monthly_avg.items():
    print(f'Month {month}: ${avg:.2f}')

print('\nWeekday revenue pattern:')
for weekday in range(7):
    weekday_avg = results[results['Date'].dt.weekday == weekday]['Revenue'].mean()
    print(f'Weekday {weekday}: ${weekday_avg:.2f}')

print('\nSeasonal patterns:')
winter_avg = results[results['Date'].dt.month.isin([12, 1, 2])]['Revenue'].mean()
spring_avg = results[results['Date'].dt.month.isin([3, 4, 5])]['Revenue'].mean()
summer_avg = results[results['Date'].dt.month.isin([6, 7, 8])]['Revenue'].mean()
fall_avg = results[results['Date'].dt.month.isin([9, 10, 11])]['Revenue'].mean()

print(f'Winter: ${winter_avg:.2f}')
print(f'Spring: ${spring_avg:.2f}')
print(f'Summer: ${summer_avg:.2f}')
print(f'Fall: ${fall_avg:.2f}')

print('\nWeekend vs. Weekday:')
weekend_avg = results[results['Date'].dt.weekday >= 5]['Revenue'].mean()
weekday_avg = results[results['Date'].dt.weekday < 5]['Revenue'].mean()
print(f'Weekend average: ${weekend_avg:.2f}')
print(f'Weekday average: ${weekday_avg:.2f}')
print(f'Weekend/Weekday ratio: {weekend_avg/weekday_avg:.2f}')

print('\nTest complete! Results saved to time_forecast_test.png')
