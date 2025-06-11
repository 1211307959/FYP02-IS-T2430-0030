import numpy as np
import pandas as pd
import joblib
import os

# Load the model and encoders
def load_model():
    """
    Load the trained model and encoders
    """
    model_path = 'enhanced_revenue_model_ethical.pkl'
    encoders_path = 'enhanced_revenue_encoders_ethical.pkl'
    
    if not os.path.exists(model_path) or not os.path.exists(encoders_path):
        raise FileNotFoundError(
            "Model files not found. Please run retrain_enhanced_ethical_model.py first."
        )
    
    model_data = joblib.load(model_path)
    encoders = joblib.load(encoders_path)
    
    return model_data, encoders

# Preprocess a single data point
def preprocess(data, model_data, encoders):
    """
    Preprocess a single data point for prediction.
    No target leakage - uses only features known before a sale.
    """
    # Start with basic input features
    processed = pd.DataFrame([data])
    
    # Encode categorical variables
    for col, encoder in encoders.items():
        if col in processed.columns:
            if col == 'Location':
                processed[f'{col}_Encoded'] = encoder.transform(processed[col].astype(str))
            elif col == '_ProductID':
                processed[f'{col}_Encoded'] = encoder.transform(processed[col].astype(str))
            elif col == 'Weekday':
                # Check if Weekday is already numeric
                if isinstance(processed[col].iloc[0], (int, float)):
                    processed['Weekday_Numeric'] = processed[col]
                else:
                    weekday_map = encoders['Weekday']
                    weekday = str(processed[col].iloc[0])
                    if weekday in weekday_map:
                        processed['Weekday_Numeric'] = weekday_map[weekday]
                    else:
                        try:
                            # Try to convert to integer (handles numeric formats)
                            processed['Weekday_Numeric'] = int(float(weekday)) % 7
                        except:
                            processed['Weekday_Numeric'] = 3  # Default to Wednesday
    
    # Temporal features
    if 'Month' in processed.columns:
        # Cyclical encoding for month
        processed['Month_Sin'] = np.sin(2 * np.pi * processed['Month'] / 12)
        processed['Month_Cos'] = np.cos(2 * np.pi * processed['Month'] / 12)
        
        # Quarter
        processed['Quarter'] = np.ceil(processed['Month'] / 3).astype(int)
        
        # Season flags
        processed['Is_Winter'] = processed['Month'].isin([12, 1, 2]).astype(int)
        processed['Is_Spring'] = processed['Month'].isin([3, 4, 5]).astype(int)
        processed['Is_Summer'] = processed['Month'].isin([6, 7, 8]).astype(int)
        processed['Is_Fall'] = processed['Month'].isin([9, 10, 11]).astype(int)
        
        # Holiday season
        processed['Is_Holiday_Season'] = processed['Month'].isin([11, 12]).astype(int)
    
    if 'Day' in processed.columns:
        # Cyclical encoding for day
        processed['Day_Sin'] = np.sin(2 * np.pi * processed['Day'] / 31)
        processed['Day_Cos'] = np.cos(2 * np.pi * processed['Day'] / 31)
    
    if 'Weekday_Numeric' in processed.columns:
        # Weekend flag
        processed['Is_Weekend'] = (processed['Weekday_Numeric'] >= 5).astype(int)
    
    # Price and cost features
    if 'Unit Price' in processed.columns and 'Unit Cost' in processed.columns:
        # Price/cost relationships
        processed['Price_to_Cost_Ratio'] = processed['Unit Price'] / (processed['Unit Cost'] + 1e-5)
        processed['Margin_Per_Unit'] = processed['Unit Price'] - processed['Unit Cost']
        processed['Margin_Per_Unit_Pct'] = processed['Margin_Per_Unit'] / (processed['Unit Price'] + 1e-5) * 100
        
        # Polynomial features
        processed['Price_Squared'] = processed['Unit Price'] ** 2
        processed['Price_Log'] = np.log1p(processed['Unit Price'])
    
    # Get model features
    model_features = model_data['features']
    
    # Initialize missing features to 0
    for feature in model_features:
        if feature not in processed.columns:
            processed[feature] = 0
    
    # Select and order features according to the model
    processed = processed[model_features]
    
    return processed

# Main prediction function
def predict_revenue(data):
    """
    Predict revenue for a single data point.
    
    Parameters:
    - data: dict with input features (Unit Price, Unit Cost, Location, _ProductID, Month, Day, etc.)
    
    Returns:
    - dict with predicted revenue, estimated quantity, etc.
    """
    # Load model and encoders
    model_data, encoders = load_model()
    model = model_data['model']
    
    # Preprocess data
    processed = preprocess(data, model_data, encoders)
    
    # Make prediction
    if model_data.get('log_transform', False):
        # Use log transform for predictions
        log_pred = model.predict(processed)[0]
        predicted_revenue = np.expm1(log_pred)
    else:
        # Direct prediction
        predicted_revenue = model.predict(processed)[0]
    
    # Estimate quantity (revenue / unit price)
    unit_price = data.get('Unit Price', 0)
    if unit_price > 0:
        estimated_quantity = max(0, round(predicted_revenue / unit_price))
    else:
        estimated_quantity = 0
    
    # Calculate derived metrics (no leakage here since it's post-prediction)
    unit_cost = data.get('Unit Cost', 0)
    total_cost = estimated_quantity * unit_cost
    profit = predicted_revenue - total_cost
    profit_margin_pct = (profit / predicted_revenue * 100) if predicted_revenue > 0 else 0
    
    # Return results
    return {
        'predicted_revenue': predicted_revenue,
        'estimated_quantity': estimated_quantity,
        'total_cost': total_cost,
        'profit': profit,
        'profit_margin_pct': profit_margin_pct,
        'unit_price': unit_price,
        'unit_cost': unit_cost
    }

# Simulate revenue at different price points
def simulate_price_variations(base_data, min_price_factor=0.5, max_price_factor=2.0, steps=7):
    """
    Simulate revenue at different price points.
    
    Parameters:
    - base_data: dict with base input features
    - min_price_factor: minimum price factor (e.g., 0.5 = 50% of base price)
    - max_price_factor: maximum price factor (e.g., 2.0 = 200% of base price)
    - steps: number of price points to simulate
    
    Returns:
    - list of dicts with price, revenue, quantity, etc. at each price point
    """
    base_price = base_data.get('Unit Price', 0)
    if base_price <= 0:
        return []
    
    # Generate price factors
    price_factors = np.linspace(min_price_factor, max_price_factor, steps)
    
    # Simulate at each price point
    variations = []
    for factor in price_factors:
        # Create a copy of base data
        sim_data = base_data.copy()
        
        # Update price
        sim_data['Unit Price'] = base_price * factor
        
        # Make prediction
        prediction = predict_revenue(sim_data)
        
        # Add to variations
        variations.append({
            'unit_price': sim_data['Unit Price'],
            'revenue': prediction['predicted_revenue'],
            'quantity': prediction['estimated_quantity'],
            'profit': prediction['profit'],
            'price_factor': factor
        })
    
    return variations

# Find optimal price for revenue or profit
def optimize_price(base_data, metric='profit', min_price_factor=0.5, max_price_factor=2.0, steps=20):
    """
    Find optimal price for revenue or profit.
    
    Parameters:
    - base_data: dict with base input features
    - metric: 'revenue' or 'profit'
    - min_price_factor: minimum price factor
    - max_price_factor: maximum price factor
    - steps: number of price points to check
    
    Returns:
    - dict with optimal price, revenue, quantity, etc.
    """
    # Simulate price variations
    variations = simulate_price_variations(
        base_data, min_price_factor, max_price_factor, steps
    )
    
    if not variations:
        return {}
    
    # Find optimal price
    if metric == 'revenue':
        # Sort by revenue (descending)
        variations.sort(key=lambda x: x['revenue'], reverse=True)
    else:
        # Sort by profit (descending)
        variations.sort(key=lambda x: x['profit'], reverse=True)
    
    # Return the best variation
    return variations[0]

# Test the model
if __name__ == "__main__":
    # Test with example data
    test_data = {
        'Unit Price': 100,
        'Unit Cost': 50,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': 12,
        'Year': 2023
    }
    
    # Make prediction
    result = predict_revenue(test_data)
    print("\nPrediction for test data:")
    for key, value in result.items():
        print(f"{key}: {value}")
    
    # Test price sensitivity
    print("\nPrice sensitivity test:")
    
    # Normal price
    normal_price_data = test_data.copy()
    normal_result = predict_revenue(normal_price_data)
    
    # High price (double)
    high_price_data = test_data.copy()
    high_price_data['Unit Price'] = 200
    high_result = predict_revenue(high_price_data)
    
    # Low price (half)
    low_price_data = test_data.copy()
    low_price_data['Unit Price'] = 50
    low_result = predict_revenue(low_price_data)
    
    print(f"Low price ($50): Quantity = {low_result['estimated_quantity']}, Revenue = ${low_result['predicted_revenue']:.2f}")
    print(f"Normal price ($100): Quantity = {normal_result['estimated_quantity']}, Revenue = ${normal_result['predicted_revenue']:.2f}")
    print(f"High price ($200): Quantity = {high_result['estimated_quantity']}, Revenue = ${high_result['predicted_revenue']:.2f}")
    
    # Simple price elasticity check
    if high_result['estimated_quantity'] < normal_result['estimated_quantity'] < low_result['estimated_quantity']:
        print("\n✓ Price sensitivity looks correct: quantity decreases as price increases")
    else:
        print("\n⚠ Price sensitivity issue: quantity doesn't consistently decrease as price increases")
    
    # Test price optimization
    print("\nPrice optimization:")
    optimal_revenue = optimize_price(test_data, metric='revenue')
    optimal_profit = optimize_price(test_data, metric='profit')
    
    print(f"Optimal price for revenue: ${optimal_revenue['unit_price']:.2f}")
    print(f"Resulting revenue: ${optimal_revenue['revenue']:.2f}")
    print(f"Resulting profit: ${optimal_revenue['profit']:.2f}")
    
    print(f"Optimal price for profit: ${optimal_profit['unit_price']:.2f}")
    print(f"Resulting revenue: ${optimal_profit['revenue']:.2f}")
    print(f"Resulting profit: ${optimal_profit['profit']:.2f}")
    
    # Test with all price variations
    print("\nSimulating all price variations:")
    variations = simulate_price_variations(test_data)
    
    print(f"{'Price':<10} {'Quantity':<10} {'Revenue':<15} {'Profit':<15}")
    print(f"{'-'*50}")
    for v in variations:
        print(f"${v['unit_price']:<9.2f} {v['quantity']:<10} ${v['revenue']:<14.2f} ${v['profit']:<14.2f}") 