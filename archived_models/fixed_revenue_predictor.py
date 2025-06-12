import pandas as pd
import numpy as np
import joblib

def load_revenue_model():
    """
    Load the revenue prediction model and its encoders.
    """
    try:
        model_data = joblib.load('best_revenue_model_improved.pkl')
        model = model_data['model']
        features = model_data['features']
        log_transform = model_data.get('log_transform', True)
        encoders = joblib.load('revenue_encoders_improved.pkl')
        return model, encoders, features, log_transform
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None, None, False

def preprocess_input(input_data, encoders, features):
    """
    Preprocess input data for prediction.
    """
    # Convert input to DataFrame
    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    else:
        df = input_data.copy()
    
    # Create processed dataframe
    processed = df.copy()
    
    # Encode categorical variables
    if 'Location' in processed.columns and 'Location' in encoders:
        # Convert to string first to avoid type issues
        processed['Location'] = processed['Location'].astype(str)
        encoder = encoders['Location']
        
        # Handle unknown values by replacing with a known one
        known_values = set(encoder.classes_)
        for val in processed['Location'].unique():
            if val not in known_values:
                # Use the first known value as default
                default_val = encoder.classes_[0]
                processed.loc[processed['Location'] == val, 'Location'] = default_val
        
        # Now transform
        processed['Location_Encoded'] = encoder.transform(processed['Location'])
    
    if '_ProductID' in processed.columns and '_ProductID' in encoders:
        # Convert to string first for consistency
        processed['_ProductID'] = processed['_ProductID'].astype(str)
        encoder = encoders['_ProductID']
        
        # Handle unknown values
        known_values = set(encoder.classes_.astype(str))
        for val in processed['_ProductID'].unique():
            if val not in known_values:
                # Use the first known value as default
                default_val = encoder.classes_[0]
                processed.loc[processed['_ProductID'] == val, '_ProductID'] = default_val
        
        # Now transform
        processed['ProductID_Encoded'] = encoder.transform(processed['_ProductID'])
    
    # Handle weekday encoding
    if 'Weekday' in processed.columns and 'Weekday' in encoders:
        weekday_map = encoders['Weekday']
        processed['Weekday_Numeric'] = processed['Weekday'].map(weekday_map)
        
        # Fill any NaN values with a default (3 = Wednesday)
        processed['Weekday_Numeric'] = processed['Weekday_Numeric'].fillna(3)
    
    # Feature engineering
    # Create time features
    if 'Month' in processed.columns:
        processed['Month_Sin'] = np.sin(2 * np.pi * processed['Month'] / 12)
        processed['Month_Cos'] = np.cos(2 * np.pi * processed['Month'] / 12)
        processed['Quarter'] = np.ceil(processed['Month'] / 3).astype(int)
    
    if 'Day' in processed.columns:
        processed['Day_Sin'] = np.sin(2 * np.pi * processed['Day'] / 31)
        processed['Day_Cos'] = np.cos(2 * np.pi * processed['Day'] / 31)
    
    # Create price/cost features
    if 'Unit Price' in processed.columns and 'Unit Cost' in processed.columns:
        processed['Price_to_Cost_Ratio'] = processed['Unit Price'] / (processed['Unit Cost'] + 1e-5)
        processed['Margin_USD'] = processed['Unit Price'] - processed['Unit Cost']
        processed['Price_Squared'] = processed['Unit Price'] ** 2
        
        # Create interaction features
        if 'Month' in processed.columns:
            processed['Price_Month'] = processed['Unit Price'] * processed['Month']
        
        if 'Location_Encoded' in processed.columns:
            processed['Price_Location'] = processed['Unit Price'] * processed['Location_Encoded']
    
    # Add default values for aggregation features
    if 'Avg_Product_Revenue' not in processed.columns and 'Avg_Product_Revenue' in features:
        processed['Avg_Product_Revenue'] = 10000  # Default value
    
    if 'Std_Product_Revenue' not in processed.columns and 'Std_Product_Revenue' in features:
        processed['Std_Product_Revenue'] = 1000  # Default value
    
    if 'Avg_Location_Revenue' not in processed.columns and 'Avg_Location_Revenue' in features:
        processed['Avg_Location_Revenue'] = 10000  # Default value
    
    if 'Std_Location_Revenue' not in processed.columns and 'Std_Location_Revenue' in features:
        processed['Std_Location_Revenue'] = 1000  # Default value
    
    # Make sure all required features exist
    missing_features = set(features) - set(processed.columns)
    if missing_features:
        print(f"Warning: Adding missing features with default values: {missing_features}")
        for feat in missing_features:
            processed[feat] = 0  # Default value
    
    # Return only the features required by the model
    result = processed[features].copy()
    
    # Fill any remaining NaN values
    for col in result.columns:
        if result[col].isnull().any():
            if np.issubdtype(result[col].dtype, np.number):
                result[col] = result[col].fillna(0)
            else:
                result[col] = result[col].fillna('unknown')
    
    return result

def predict_revenue(input_data):
    """
    Predict revenue using the trained model.
    """
    # Load model and encoders
    model, encoders, features, log_transform = load_revenue_model()
    
    if model is None:
        return {"error": "Failed to load model"}
    
    try:
        # Preprocess input
        X = preprocess_input(input_data, encoders, features)
        
        # Make prediction
        if log_transform:
            predicted_log = model.predict(X)[0]
            predicted_revenue = np.expm1(predicted_log)
        else:
            predicted_revenue = model.predict(X)[0]
        
        # Calculate quantity and profit
        unit_price = input_data.get('Unit Price', 0)
        unit_cost = input_data.get('Unit Cost', 0)
        
        # Avoid division by zero
        if unit_price > 0:
            estimated_quantity = round(predicted_revenue / unit_price)
        else:
            estimated_quantity = 0
        
        profit = estimated_quantity * (unit_price - unit_cost)
        
        return {
            "predicted_revenue": round(predicted_revenue, 2),
            "estimated_quantity": max(0, estimated_quantity),
            "profit": round(profit, 2)
        }
    
    except Exception as e:
        print(f"Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def simulate_price_variations(input_data):
    """
    Simulate different price points to find optimal pricing.
    """
    base_price = input_data.get('Unit Price', 100)
    unit_cost = input_data.get('Unit Cost', 50)
    
    # Define price points to simulate
    price_points = [
        round(base_price * 0.5, 2),
        round(base_price * 0.7, 2),
        round(base_price * 0.9, 2),
        base_price,
        round(base_price * 1.2, 2),
        round(base_price * 1.5, 2),
        round(base_price * 2.0, 2)
    ]
    
    variations = []
    max_revenue = 0
    max_profit = 0
    optimal_revenue_price = None
    optimal_profit_price = None
    
    # Simulate each price point
    for price in price_points:
        # Create a copy of the input data with the new price
        simulation_data = input_data.copy()
        simulation_data['Unit Price'] = price
        
        # Recalculate profit margin percentage
        if 'Unit Cost' in simulation_data:
            simulation_data['Profit Margin (%)'] = (price - unit_cost) / price * 100
        
        # Calculate Total Cost if needed
        if 'Total Cost' in simulation_data and unit_cost > 0:
            quantity = simulation_data.get('Order Quantity', 1)
            simulation_data['Total Cost'] = unit_cost * quantity
        
        # Get prediction
        result = predict_revenue(simulation_data)
        
        if 'error' in result:
            print(f"Error in simulation for price {price}: {result['error']}")
            continue
        
        # Extract results
        predicted_revenue = result['predicted_revenue']
        estimated_quantity = result['estimated_quantity']
        profit = result['profit']
        
        # Store result
        variation = {
            "unit_price": price,
            "quantity": estimated_quantity,
            "revenue": predicted_revenue,
            "profit": profit
        }
        variations.append(variation)
        
        # Check if this is a new maximum
        if predicted_revenue > max_revenue:
            max_revenue = predicted_revenue
            optimal_revenue_price = variation.copy()
        
        if profit > max_profit:
            max_profit = profit
            optimal_profit_price = variation.copy()
    
    # Sort variations by price
    variations.sort(key=lambda x: x['unit_price'])
    
    return {
        "base_price": base_price,
        "unit_cost": unit_cost,
        "model_type": "improved direct prediction (no quantity input)",
        "variations": variations,
        "optimal_revenue_price": optimal_revenue_price,
        "optimal_profit_price": optimal_profit_price
    }

# Example usage
if __name__ == "__main__":
    # Sample input data
    sample_input = {
        'Unit Price': 100,
        'Unit Cost': 50,
        'Total Cost': 500,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': 12,
        'Year': 2023,
        'Profit Margin (%)': 50  # (100-50)/100 * 100
    }
    
    # Make a prediction
    result = predict_revenue(sample_input)
    print("Prediction result:", result)
    
    # Simulate different price points
    if 'error' not in result:
        simulation = simulate_price_variations(sample_input)
        
        print("\nPrice simulation:")
        print(f"Base price: ${simulation['base_price']}")
        print(f"Unit cost: ${simulation['unit_cost']}")
        print("\nPrice variations:")
        
        for var in simulation['variations']:
            print(f"Price: ${var['unit_price']:.2f}, Quantity: {var['quantity']}, Revenue: ${var['revenue']:.2f}, Profit: ${var['profit']:.2f}")
        
        if simulation['optimal_revenue_price']:
            print(f"\nOptimal price for revenue: ${simulation['optimal_revenue_price']['unit_price']:.2f}")
            print(f"Maximum revenue: ${simulation['optimal_revenue_price']['revenue']:.2f}")
        
        if simulation['optimal_profit_price']:
            print(f"\nOptimal price for profit: ${simulation['optimal_profit_price']['unit_price']:.2f}")
            print(f"Maximum profit: ${simulation['optimal_profit_price']['profit']:.2f}")
    else:
        print("Skipping simulation due to prediction error") 