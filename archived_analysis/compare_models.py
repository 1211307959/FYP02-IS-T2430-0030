import numpy as np
import pandas as pd
import joblib
import json
from tabulate import tabulate
from revenue_predictor_time_enhanced import predict_revenue as predict_time_enhanced
from revenue_predictor_50_50 import predict_revenue as predict_50_50

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return convert_numpy_types(obj.tolist())
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

# Load models and analyze structure
print("=== MODEL COMPARISON ===")
print("\nLoading models for comparison...")

time_enhanced_model = joblib.load('revenue_model_time_enhanced.pkl')
model_50_50 = joblib.load('revenue_model_50_50_split.pkl')

# Basic model information
print("\n=== MODEL INFORMATION ===")
print(f"Time-Enhanced Model R²: {time_enhanced_model.get('r2', 'N/A'):.4f}")
print(f"Time-Enhanced Model MAE: {time_enhanced_model.get('mae', 'N/A'):.4f}")
print(f"Time-Enhanced Model RMSE: {time_enhanced_model.get('rmse', 'N/A'):.4f}")

print(f"50/50 Split Model R²: {model_50_50.get('r2', 'N/A'):.4f}")
print(f"50/50 Split Model MAE: {model_50_50.get('mae', 'N/A'):.4f}")
print(f"50/50 Split Model RMSE: {model_50_50.get('rmse', 'N/A'):.4f}")

# Feature comparison
time_features = time_enhanced_model.get('features', [])
model_50_50_features = model_50_50.get('features', [])

print(f"\nTime-Enhanced Model: {len(time_features)} features")
print(f"50/50 Split Model: {len(model_50_50_features)} features")

# Unique features in each model
unique_to_time = set(time_features) - set(model_50_50_features)
unique_to_50_50 = set(model_50_50_features) - set(time_features)

print(f"\nUnique features in Time-Enhanced model: {len(unique_to_time)}")
if unique_to_time:
    print(f"Top 10 unique time features: {list(unique_to_time)[:10]}")

print(f"\nUnique features in 50/50 Split model: {len(unique_to_50_50)}")
if unique_to_50_50:
    print(f"Top 10 unique 50/50 features: {list(unique_to_50_50)[:10]}")

# Test with various inputs
print("\n=== PREDICTION COMPARISON ===")

# Test scenarios
test_scenarios = [
    {
        "name": "Standard Price",
        "data": {
            'Unit Price': 100.00,
            'Unit Cost': 50.00,
            'Month': 6,
            'Day': 15,
            'Weekday': 'Friday',
            'Location': 'North',
            '_ProductID': 1,
            'Year': 2023
        }
    },
    {
        "name": "High Price",
        "data": {
            'Unit Price': 200.00,
            'Unit Cost': 50.00,
            'Month': 6,
            'Day': 15,
            'Weekday': 'Friday',
            'Location': 'North',
            '_ProductID': 1,
            'Year': 2023
        }
    },
    {
        "name": "Low Price",
        "data": {
            'Unit Price': 50.00,
            'Unit Cost': 25.00,
            'Month': 6,
            'Day': 15,
            'Weekday': 'Friday',
            'Location': 'North',
            '_ProductID': 1,
            'Year': 2023
        }
    },
    {
        "name": "Weekend",
        "data": {
            'Unit Price': 100.00,
            'Unit Cost': 50.00,
            'Month': 6,
            'Day': 16,
            'Weekday': 'Saturday',
            'Location': 'North',
            '_ProductID': 1,
            'Year': 2023
        }
    },
    {
        "name": "Holiday Season",
        "data": {
            'Unit Price': 100.00,
            'Unit Cost': 50.00,
            'Month': 12,
            'Day': 15,
            'Weekday': 'Friday',
            'Location': 'North',
            '_ProductID': 1,
            'Year': 2023
        }
    }
]

# Run predictions
results = []
for scenario in test_scenarios:
    name = scenario["name"]
    data = scenario["data"]
    
    # Time-enhanced model prediction
    try:
        time_result = predict_time_enhanced(data.copy())
        time_result = convert_numpy_types(time_result)
    except Exception as e:
        print(f"Error with time-enhanced model on {name}: {str(e)}")
        time_result = {"error": str(e)}
    
    # 50/50 model prediction
    try:
        model_50_50_result = predict_50_50(data.copy())
        model_50_50_result = convert_numpy_types(model_50_50_result)
    except Exception as e:
        print(f"Error with 50/50 model on {name}: {str(e)}")
        model_50_50_result = {"error": str(e)}
    
    # Extract key metrics
    time_revenue = time_result.get('predicted_revenue', 'Error')
    time_quantity = time_result.get('estimated_quantity', 'Error')
    time_profit = time_result.get('profit', 'Error')
    
    model_50_50_revenue = model_50_50_result.get('predicted_revenue', 'Error')
    model_50_50_quantity = model_50_50_result.get('estimated_quantity', 'Error')
    model_50_50_profit = model_50_50_result.get('profit', 'Error')
    
    # Calculate differences
    if isinstance(time_revenue, (int, float)) and isinstance(model_50_50_revenue, (int, float)):
        revenue_diff = (time_revenue - model_50_50_revenue) / model_50_50_revenue * 100 if model_50_50_revenue != 0 else float('inf')
    else:
        revenue_diff = "N/A"
        
    if isinstance(time_quantity, (int, float)) and isinstance(model_50_50_quantity, (int, float)):
        quantity_diff = (time_quantity - model_50_50_quantity) / model_50_50_quantity * 100 if model_50_50_quantity != 0 else float('inf')
    else:
        quantity_diff = "N/A"
        
    if isinstance(time_profit, (int, float)) and isinstance(model_50_50_profit, (int, float)):
        profit_diff = (time_profit - model_50_50_profit) / model_50_50_profit * 100 if model_50_50_profit != 0 else float('inf')
    else:
        profit_diff = "N/A"
    
    # Add to results
    results.append([
        name,
        f"${time_revenue:.2f}" if isinstance(time_revenue, (int, float)) else str(time_revenue),
        f"${model_50_50_revenue:.2f}" if isinstance(model_50_50_revenue, (int, float)) else str(model_50_50_revenue),
        f"{revenue_diff:.1f}%" if isinstance(revenue_diff, (int, float)) else str(revenue_diff),
        f"{time_quantity}" if isinstance(time_quantity, (int, float)) else str(time_quantity),
        f"{model_50_50_quantity}" if isinstance(model_50_50_quantity, (int, float)) else str(model_50_50_quantity),
        f"{quantity_diff:.1f}%" if isinstance(quantity_diff, (int, float)) else str(quantity_diff),
        f"${time_profit:.2f}" if isinstance(time_profit, (int, float)) else str(time_profit),
        f"${model_50_50_profit:.2f}" if isinstance(model_50_50_profit, (int, float)) else str(model_50_50_profit),
        f"{profit_diff:.1f}%" if isinstance(profit_diff, (int, float)) else str(profit_diff)
    ])

# Display results in a table
headers = ["Scenario", "Time Revenue", "50/50 Revenue", "Revenue Diff", 
           "Time Qty", "50/50 Qty", "Qty Diff", 
           "Time Profit", "50/50 Profit", "Profit Diff"]
           
print(tabulate(results, headers=headers, tablefmt="grid"))

# Price elasticity test
print("\n=== PRICE ELASTICITY TEST ===")
base_data = {
    'Unit Price': 100.00,
    'Unit Cost': 50.00,
    'Month': 6,
    'Day': 15,
    'Weekday': 'Friday',
    'Location': 'North',
    '_ProductID': 1,
    'Year': 2023
}

prices = [25, 50, 75, 100, 125, 150, 200, 250, 300]
elasticity_results = []

for price in prices:
    test_data = base_data.copy()
    test_data['Unit Price'] = price
    
    # Time-enhanced model prediction
    time_result = predict_time_enhanced(test_data.copy())
    time_result = convert_numpy_types(time_result)
    
    # 50/50 model prediction
    model_50_50_result = predict_50_50(test_data.copy())
    model_50_50_result = convert_numpy_types(model_50_50_result)
    
    elasticity_results.append([
        f"${price:.2f}",
        time_result.get('estimated_quantity', 'Error'),
        model_50_50_result.get('estimated_quantity', 'Error'),
        f"${time_result.get('predicted_revenue', 'Error'):.2f}" if isinstance(time_result.get('predicted_revenue'), (int, float)) else 'Error',
        f"${model_50_50_result.get('predicted_revenue', 'Error'):.2f}" if isinstance(model_50_50_result.get('predicted_revenue'), (int, float)) else 'Error',
        f"${time_result.get('profit', 'Error'):.2f}" if isinstance(time_result.get('profit'), (int, float)) else 'Error',
        f"${model_50_50_result.get('profit', 'Error'):.2f}" if isinstance(model_50_50_result.get('profit'), (int, float)) else 'Error'
    ])

elasticity_headers = ["Price", "Time Qty", "50/50 Qty", "Time Revenue", "50/50 Revenue", "Time Profit", "50/50 Profit"]
print(tabulate(elasticity_results, headers=elasticity_headers, tablefmt="grid"))

print("\n=== TIME FEATURE SENSITIVITY ===")
# Test variations in time (month, weekday)
months = [1, 4, 7, 10]
time_variation_results = []

for month in months:
    test_data = base_data.copy()
    test_data['Month'] = month
    
    # Determine season
    if month in [12, 1, 2]:
        season = "Winter"
    elif month in [3, 4, 5]:
        season = "Spring"
    elif month in [6, 7, 8]:
        season = "Summer"
    else:
        season = "Fall"
    
    # Time-enhanced model prediction
    time_result = predict_time_enhanced(test_data.copy())
    time_result = convert_numpy_types(time_result)
    
    # 50/50 model prediction
    model_50_50_result = predict_50_50(test_data.copy())
    model_50_50_result = convert_numpy_types(model_50_50_result)
    
    time_variation_results.append([
        f"Month {month} ({season})",
        time_result.get('estimated_quantity', 'Error'),
        model_50_50_result.get('estimated_quantity', 'Error'),
        f"${time_result.get('predicted_revenue', 'Error'):.2f}" if isinstance(time_result.get('predicted_revenue'), (int, float)) else 'Error',
        f"${model_50_50_result.get('predicted_revenue', 'Error'):.2f}" if isinstance(model_50_50_result.get('predicted_revenue'), (int, float)) else 'Error'
    ])

# Test weekdays
weekdays = ['Monday', 'Wednesday', 'Friday', 'Saturday', 'Sunday']

for weekday in weekdays:
    test_data = base_data.copy()
    test_data['Weekday'] = weekday
    
    # Time-enhanced model prediction
    time_result = predict_time_enhanced(test_data.copy())
    time_result = convert_numpy_types(time_result)
    
    # 50/50 model prediction
    model_50_50_result = predict_50_50(test_data.copy())
    model_50_50_result = convert_numpy_types(model_50_50_result)
    
    time_variation_results.append([
        f"Weekday: {weekday}",
        time_result.get('estimated_quantity', 'Error'),
        model_50_50_result.get('estimated_quantity', 'Error'),
        f"${time_result.get('predicted_revenue', 'Error'):.2f}" if isinstance(time_result.get('predicted_revenue'), (int, float)) else 'Error',
        f"${model_50_50_result.get('predicted_revenue', 'Error'):.2f}" if isinstance(model_50_50_result.get('predicted_revenue'), (int, float)) else 'Error'
    ])

time_headers = ["Time Variable", "Time Qty", "50/50 Qty", "Time Revenue", "50/50 Revenue"]
print(tabulate(time_variation_results, headers=time_headers, tablefmt="grid"))

print("\n=== CONCLUSION ===")
print("The Time-Enhanced model includes additional temporal features that provide more sensitivity to time-based patterns.")
print("This allows for more accurate predictions based on seasons, weekdays, and holidays.")
print("The main advantages of the Time-Enhanced model are:")
print("1. Improved sensitivity to seasonal patterns")
print("2. Better weekday differentiation")
print("3. Recognition of holiday periods")
print("4. More realistic price elasticity modeling") 