import numpy as np
import pandas as pd
import joblib
import os
from typing import Dict, Any, Union, Optional
from datetime import datetime

def validate_and_convert_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and convert input data to appropriate types.
    Returns a new dict with validated and converted values.
    """
    validated = {}
    
    # Required fields
    required_fields = ['Unit Price', 'Unit Cost', 'Month', 'Day', 'Weekday', 'Location', '_ProductID', 'Year']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Valid weekdays
    valid_weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Convert and validate numeric fields
    try:
        # Convert string inputs to appropriate types
        data['Unit Price'] = float(data['Unit Price'])
        data['Unit Cost'] = float(data['Unit Cost'])
        data['Month'] = int(data['Month'])
        data['Day'] = int(data['Day'])
        data['Year'] = int(data['Year'])
        # _ProductID: always treat as string
        data['_ProductID'] = str(data['_ProductID'])
        
        # Validate numeric ranges
        if not 1 <= data['Month'] <= 12:
            raise ValueError("Month must be between 1 and 12")
        if not 1 <= data['Day'] <= 31:
            raise ValueError("Day must be between 1 and 31")
        if data['Unit Price'] < 0:
            raise ValueError("Unit Price cannot be negative")
        if data['Unit Cost'] < 0:
            raise ValueError("Unit Cost cannot be negative")
        if data['Unit Cost'] > data['Unit Price']:
            raise ValueError("Unit Cost cannot be greater than Unit Price")
        
        # Validate weekday
        if isinstance(data['Weekday'], str) and data['Weekday'] not in valid_weekdays:
            raise ValueError(f"Weekday must be one of: {', '.join(valid_weekdays)}")
        
    except (ValueError, TypeError) as e:
        if isinstance(e, ValueError):
            raise ValueError(str(e))
        raise ValueError(f"Invalid numeric value: {str(e)}")
    
    return data

def load_model():
    """
    Load the trained model and encoders
    """
    model_path = 'revenue_model_time_enhanced.pkl'
    encoders_path = 'revenue_encoders_time_enhanced.pkl'
    
    if not os.path.exists(model_path) or not os.path.exists(encoders_path):
        raise FileNotFoundError(
            "Enhanced time model files not found. Please run train_time_enhanced_model.py first."
        )
    
    try:
        model_data = joblib.load(model_path)
        encoders = joblib.load(encoders_path)
        return model_data, encoders
    except Exception as e:
        raise RuntimeError(f"Error loading model files: {str(e)}")

def add_enhanced_time_features(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add enhanced time-based features to the input data.
    """
    # Create a proper date object
    try:
        year = data['Year']
        month = data['Month']
        day = min(data['Day'], 28)  # Clip to avoid month end issues
        date = datetime(year, month, day)
        
        # Add day of year (1-366)
        data['Day_of_Year'] = date.timetuple().tm_yday
        
        # Add week of year (1-53)
        data['Week_of_Year'] = date.isocalendar()[1]
        
        # Cyclical encoding of time
        data['Month_Sin'] = np.sin(2 * np.pi * month / 12)
        data['Month_Cos'] = np.cos(2 * np.pi * month / 12)
        data['Day_Sin'] = np.sin(2 * np.pi * day / 31)
        data['Day_Cos'] = np.cos(2 * np.pi * day / 31)
        data['Day_of_Year_Sin'] = np.sin(2 * np.pi * data['Day_of_Year'] / 366)
        data['Day_of_Year_Cos'] = np.cos(2 * np.pi * data['Day_of_Year'] / 366)
        data['Week_of_Year_Sin'] = np.sin(2 * np.pi * data['Week_of_Year'] / 53)
        data['Week_of_Year_Cos'] = np.cos(2 * np.pi * data['Week_of_Year'] / 53)
        
        # Quarter
        data['Quarter'] = (month - 1) // 3 + 1
        
        # Seasons (Northern Hemisphere)
        data['Is_Winter'] = 1 if month in [12, 1, 2] else 0
        data['Is_Spring'] = 1 if month in [3, 4, 5] else 0
        data['Is_Summer'] = 1 if month in [6, 7, 8] else 0
        data['Is_Fall'] = 1 if month in [9, 10, 11] else 0
        
        # Holiday season (Nov-Dec)
        data['Is_Holiday_Season'] = 1 if month in [11, 12] else 0
        
        # Weekend
        if isinstance(data['Weekday'], str):
            data['Is_Weekend'] = 1 if data['Weekday'] in ['Saturday', 'Sunday'] else 0
        else:
            weekday_num = data.get('Weekday_Numeric', data['Weekday'])
            data['Is_Weekend'] = 1 if weekday_num >= 5 else 0
        
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
        data['Is_Holiday'] = 1 if (month, day) in holidays else 0
        
        return data
        
    except Exception as e:
        raise ValueError(f"Error adding enhanced time features: {str(e)}")

def preprocess(data: Dict[str, Any], model_data: Dict[str, Any], encoders: Dict[str, Any]) -> pd.DataFrame:
    """
    Preprocess a single data point for prediction.
    No target leakage - uses only features known before a sale.
    """
    try:
        # Start with basic input features
        processed = pd.DataFrame([data])
        
        # Add enhanced time features
        for key, value in add_enhanced_time_features(data).items():
            if key not in processed.columns:
                processed[key] = value
        
        # Encode categorical variables
        for col, encoder in encoders.items():
            if col in processed.columns:
                try:
                    if col == 'Location':
                        # Handle unknown locations
                        if processed[col].iloc[0] not in encoder.classes_:
                            raise ValueError(f"Unknown location: {processed[col].iloc[0]}")
                        processed[f'{col}_Encoded'] = encoder.transform(processed[col])
                    elif col == '_ProductID':
                        # Handle unknown product IDs
                        if processed[col].iloc[0] not in encoder.classes_:
                            raise ValueError(f"Unknown product ID: {processed[col].iloc[0]}")
                        processed[f'ProductID_Encoded'] = encoder.transform(processed[col])
                    elif col == 'Weekday':
                        # Handle weekday encoding
                        weekday_map = encoders['Weekday']
                        weekday = str(processed[col].iloc[0])
                        if weekday in weekday_map:
                            processed['Weekday_Numeric'] = weekday_map[weekday]
                        else:
                            # Default to Wednesday (3) for unknown weekdays
                            processed['Weekday_Numeric'] = 3
                except Exception as e:
                    raise ValueError(f"Error encoding {col}: {str(e)}")
        
        # Basic price features
        processed['Price_to_Cost_Ratio'] = processed['Unit Price'] / processed['Unit Cost']
        processed['Margin_Per_Unit'] = processed['Unit Price'] - processed['Unit Cost']
        processed['Margin_Per_Unit_Pct'] = (processed['Margin_Per_Unit'] / processed['Unit Price']) * 100
        processed['Price_Squared'] = processed['Unit Price'] ** 2
        processed['Price_Log'] = np.log1p(processed['Unit Price'])
        
        # Add default values for more complex features
        # These would normally be calculated from group statistics in the full dataset
        # For prediction, we use reasonable defaults
        
        # Product price statistics
        processed['Product_Unit Price_mean'] = processed['Unit Price']
        processed['Product_Unit Price_std'] = 0
        processed['Product_Unit Price_min'] = processed['Unit Price'] * 0.8
        processed['Product_Unit Price_max'] = processed['Unit Price'] * 1.2
        
        # Product cost statistics
        processed['Product_Unit Cost_mean'] = processed['Unit Cost']
        
        # Product popularity (default to medium popularity)
        processed['Product_Popularity'] = 1000
        
        # Location price statistics
        processed['Location_Unit Price_mean'] = processed['Unit Price']
        processed['Location_Unit Price_std'] = 0
        processed['Location_Unit Price_min'] = processed['Unit Price'] * 0.8
        processed['Location_Unit Price_max'] = processed['Unit Price'] * 1.2
        
        # Location cost statistics
        processed['Location_Unit Cost_mean'] = processed['Unit Cost']
        
        # Product-Month interactions
        processed['Product_Month_Unit Price_mean'] = processed['Unit Price']
        
        # Product-Quarter interactions
        processed['Product_Quarter_Unit Price_mean'] = processed['Unit Price']
        
        # Location-Month interactions
        processed['Location_Month_Unit Price_mean'] = processed['Unit Price']
        
        # Weekend-Location interactions
        processed['Location_Weekend_Revenue_mean'] = 10000
        
        # Product-Weekend interactions
        processed['Product_Weekend_Revenue_mean'] = 10000
        
        # Price comparison features
        processed['Price_vs_Product_Avg'] = 1.0
        processed['Price_vs_Location_Avg'] = 1.0
        processed['Price_Seasonal_Deviation'] = 1.0
        
        # Feature interactions
        processed['Price_Popularity'] = processed['Unit Price'] * processed['Product_Popularity']
        processed['Price_Location'] = processed['Unit Price'] * processed['Location_Unit Price_mean']
        processed['Price_Month'] = processed['Unit Price'] * processed['Month']
        processed['Price_Quarter'] = processed['Unit Price'] * processed['Quarter']
        processed['Price_Holiday'] = processed['Unit Price'] * processed['Is_Holiday']
        processed['Price_Weekend'] = processed['Unit Price'] * processed['Is_Weekend']
        
        # Revenue seasonality ratio
        processed['Revenue_Month_Ratio'] = 1.0
        processed['Revenue_Weekday_Ratio'] = 1.0
        
        # Get model features
        model_features = model_data.get('features', [])
        if not model_features:
            raise ValueError("Model features not found in model data")
        
        # Initialize missing features to 0
        for feature in model_features:
            if feature not in processed.columns:
                processed[feature] = 0
        
        # Select and order features according to the model
        processed = processed[model_features]
        
        return processed
        
    except Exception as e:
        raise ValueError(f"Error in preprocessing: {str(e)}")

def predict_revenue(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict revenue for a single data point using the time-enhanced model.
    
    Parameters:
    - data: dict with input features (Unit Price, Unit Cost, Location, _ProductID, Month, Day, etc.)
    
    Returns:
    - dict with predicted revenue, estimated quantity, etc.
    """
    try:
        # Validate and convert input
        validated_data = validate_and_convert_input(data)
        
        # Check for extreme price values that might cause issues
        if validated_data['Unit Price'] > 100000:
            return {
                'error': 'Unit Price exceeds maximum allowed value (100000)'
            }
        
        # Load model and encoders
        model_data, encoders = load_model()
        model = model_data['model']
        
        # Preprocess data
        processed = preprocess(validated_data, model_data, encoders)
        
        # Make prediction
        if model_data.get('log_transform', False):
            # Use log transform for predictions
            log_pred = model.predict(processed)[0]
            predicted_revenue = np.expm1(log_pred)
        else:
            # Direct prediction
            predicted_revenue = model.predict(processed)[0]
        
        # Handle negative revenue predictions
        predicted_revenue = max(0, predicted_revenue)
        
        # Apply price elasticity adjustments for ALL price ranges
        unit_price = validated_data['Unit Price']
        avg_price = 5000  # Approximate average price in the dataset
        
        # Get product ID for more targeted price reference if available
        product_id = str(validated_data.get('_ProductID', ''))
        
        # Elasticity calculation based on deviation from average price
        # This creates more sensitivity even at normal price ranges
        if unit_price > 0:
            # Calculate price ratio (how many times higher/lower than average)
            price_ratio = unit_price / avg_price
            
            # Apply elasticity with varying strength based on price range
            if price_ratio > 2.0:  # Very high prices
                # Strong elasticity effect for very high prices
                elasticity = -1.8
                predicted_revenue = predicted_revenue * (price_ratio ** elasticity)
            elif price_ratio > 1.0:  # Above average prices
                # Moderate elasticity for above average prices
                elasticity = -0.8
                predicted_revenue = predicted_revenue * (price_ratio ** elasticity)
            elif price_ratio < 1.0:  # Below average prices
                # Milder elasticity for below average prices (increased demand)
                elasticity = -0.6
                predicted_revenue = predicted_revenue * (price_ratio ** elasticity)
        
        # Estimate quantity (revenue / unit price)
        if unit_price > 0:
            # Round to nearest integer for more realistic quantity variations
            estimated_quantity = max(0, round(predicted_revenue / unit_price))
        else:
            estimated_quantity = 0
        
        # Recalculate revenue based on estimated quantity to ensure consistency
        # This guarantees that if quantity is 0, revenue will be 0
        predicted_revenue = estimated_quantity * unit_price
        
        # Calculate derived metrics (no leakage here since it's post-prediction)
        unit_cost = validated_data['Unit Cost']
        total_cost = estimated_quantity * unit_cost
        profit = predicted_revenue - total_cost
        
        # Avoid division by zero
        if predicted_revenue > 0:
            profit_margin_pct = (profit / predicted_revenue * 100)
        else:
            profit_margin_pct = 0
        
        # Return results with time feature information
        month = validated_data['Month']
        day = validated_data['Day']
        weekday = validated_data['Weekday']
        
        # Extract season for better context
        season = 'Winter'
        if month in [3, 4, 5]:
            season = 'Spring'
        elif month in [6, 7, 8]:
            season = 'Summer'
        elif month in [9, 10, 11]:
            season = 'Fall'
            
        return {
            'predicted_revenue': round(predicted_revenue, 2),
            'revenue': round(predicted_revenue, 2),
            'estimated_quantity': estimated_quantity,
            'predicted_quantity': estimated_quantity,
            'total_cost': round(total_cost, 2),
            'profit': round(profit, 2),
            'profit_margin_pct': round(profit_margin_pct, 2),
            'unit_price': unit_price,
            'unit_cost': unit_cost,
            'month': month,
            'day': day,
            'weekday': weekday,
            'season': season,
            'time_features': {
                'month_sin': round(np.sin(2 * np.pi * month / 12), 4),
                'month_cos': round(np.cos(2 * np.pi * month / 12), 4),
                'is_weekend': 1 if (isinstance(weekday, str) and weekday in ['Saturday', 'Sunday']) 
                               else (1 if isinstance(weekday, int) and weekday >= 5 else 0),
                'season': season
            }
        }
        
    except ValueError as e:
        # Handle validation and preprocessing errors
        return {'error': str(e)}
    except Exception as e:
        # Handle unexpected errors
        import traceback
        traceback.print_exc()
        return {'error': f"Unexpected error: {str(e)}"}

# Simulate revenue at different price points
def simulate_price_variations(base_data, min_price_factor=0.5, max_price_factor=2.0, steps=7):
    """
    Simulate revenue at different price points using the time-enhanced model.
    
    Parameters:
    - base_data: dict with base input features
    - min_price_factor: minimum price factor (e.g., 0.5 = 50% of base price)
    - max_price_factor: maximum price factor (e.g., 2.0 = 200% of base price)
    - steps: number of price points to simulate
    
    Returns:
    - list of dicts with price, revenue, quantity, etc. at each price point
    """
    try:
        # Check for missing or null values in base_data and set defaults
        if base_data is None:
            base_data = {}
            
        # Remove any timestamp fields that could prevent caching
        if '_timestamp' in base_data:
            base_data.pop('_timestamp')
            
        # Set default values for missing or null fields
        if base_data.get('Unit Price') is None:
            base_data['Unit Price'] = 100.0
            
        if base_data.get('Unit Cost') is None:
            base_data['Unit Cost'] = 50.0
            
        if base_data.get('_ProductID') is None:
            base_data['_ProductID'] = 1  # Default product ID
            
        if base_data.get('Location') is None:
            base_data['Location'] = 'North'  # Default location
        
        # Ensure values are proper types
        base_price = float(base_data.get('Unit Price', 0))
        if base_price <= 0:
            return []
        
        # Generate price factors
        price_factors = np.linspace(min_price_factor, max_price_factor, steps)
        
        # Simulate at each price point
        variations = []
        max_revenue = 0
        max_quantity = 0
        
        # Log the simulation parameters for debugging
        print(f"Simulating price variations: Base price=${base_price}, Factors={min_price_factor}-{max_price_factor}, Steps={steps}")
        print(f"Base data: {base_data}")
        
        # First pass: collect simulations and find maximums
        for i, factor in enumerate(price_factors):
            try:
                # Create a copy of base data
                sim_data = base_data.copy()
                
                # Update price
                sim_price = base_price * factor
                sim_data['Unit Price'] = sim_price
                
                # Make prediction
                prediction = predict_revenue(sim_data)
                
                # Check if prediction failed with an error
                if 'error' in prediction:
                    print(f"Warning: Error in simulation at factor {factor}: {prediction['error']}")
                    continue
                
                # Get quantity as an integer to ensure it displays correctly
                quantity = int(prediction['estimated_quantity'])
                
                # Validate quantity for reasonableness
                if quantity > 100 and factor > 1.0:
                    print(f"WARNING: Unusually high quantity ({quantity}) for price factor {factor} - might be a calculation error")
                    # Apply price elasticity - quantity should decrease as price increases
                    base_quantity = 10  # Reasonable base quantity
                    elasticity = -1.2  # Standard price elasticity
                    quantity = max(0, round(base_quantity * (factor ** elasticity)))
                    print(f"Adjusted to more reasonable value: {quantity}")
                
                # Ensure revenue is based on actual quantity
                revenue = quantity * sim_price
                
                # Calculate profit
                profit = revenue - (quantity * float(sim_data.get('Unit Cost', 0)))
                
                # Keep track of maximums for scaling
                max_revenue = max(max_revenue, revenue)
                max_quantity = max(max_quantity, quantity)
                
                # Add time feature information
                time_info = prediction.get('time_features', {})
                
                # Build the variation
                scenario_name = "Current Price" if i == (steps // 2) else (
                    f"{int(factor * 100)}% of Price" if factor < 1 else 
                    f"{int(factor * 100)}% of Price"
                )
                
                # Include all possible field names for compatibility with different consumers
                variations.append({
                    'Scenario': scenario_name,
                    'scenario': scenario_name,
                    'Unit Price': sim_price,
                    'unit_price': sim_price,
                    'unitPrice': sim_price,
                    'Predicted Revenue': revenue,
                    'predicted_revenue': revenue,
                    'revenue': revenue,
                    'Predicted Quantity': quantity,
                    'predicted_quantity': quantity, 
                    'quantity': quantity,
                    'Profit': profit,
                    'profit': profit,
                    'price_factor': factor,
                    'raw_quantity': quantity,  # Keep the original quantity for reference
                    'month': prediction.get('month'),
                    'day': prediction.get('day'),
                    'weekday': prediction.get('weekday'),
                    'season': prediction.get('season'),
                    'time_features': time_info
                })
                
                # Log successful simulation
                print(f"Simulation at factor {factor}: Price=${sim_price}, Quantity={quantity}, Revenue=${revenue}")
                
            except Exception as e:
                print(f"Error in simulation at factor {factor}: {str(e)}")
                # Continue with next price point instead of failing entirely
                continue
        
        # Check if any simulations succeeded
        if len(variations) == 0:
            print("Warning: All simulations failed")
            return []
        
        # Sort variations by price factor
        variations.sort(key=lambda x: x['price_factor'])
        
        # Second pass: scale quantities for better visualization
        # Only if we have some non-zero quantities
        if max_quantity > 0:
            # Calculate a scale factor that makes quantity more visible
            # aiming for quantity to be about 1/3 of the highest revenue
            target_max_quantity = max_revenue / 3
            scale_factor = target_max_quantity / max_quantity if max_quantity > 0 else 1
            
            # Apply the scaling factor to quantity for visualization purposes only
            for variation in variations:
                # Scale for display, keeping original value in raw_quantity
                # Only show quantity in chart if it's non-zero
                if variation['raw_quantity'] > 0:
                    scaled_quantity = variation['raw_quantity'] * scale_factor
                    variation['quantity_for_chart'] = scaled_quantity
                else:
                    variation['quantity_for_chart'] = 0
                
                # Replace the chart's quantity value with the scaled version
                variation['quantity'] = variation['quantity_for_chart']
        
        return variations
    except Exception as e:
        print(f"Error in simulate_price_variations: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

# Find optimal price for revenue or profit
def optimize_price(base_data, metric='profit', min_price_factor=0.5, max_price_factor=2.0, steps=20):
    """
    Find optimal price for revenue or profit using the time-enhanced model.
    
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
    
    try:
        # Make prediction
        result = predict_revenue(test_data)
        print("\nPrediction for test data:")
        for key, value in result.items():
            if key != 'time_features':
                print(f"{key}: {value}")
            
        print("\nTime features:")
        for key, value in result.get('time_features', {}).items():
            print(f"  {key}: {value}")
        
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
        
        # Test time sensitivity - different months
        print("\nTime sensitivity test:")
        
        for month in [1, 4, 7, 10]:
            month_data = test_data.copy()
            month_data['Month'] = month
            month_result = predict_revenue(month_data)
            print(f"Month {month} ({month_result['season']}): Revenue = ${month_result['predicted_revenue']:.2f}, Quantity = {month_result['estimated_quantity']}")
        
        # Test weekend vs weekday
        print("\nWeekday vs Weekend test:")
        
        weekday_data = test_data.copy()
        weekday_data['Weekday'] = 'Wednesday'
        weekday_result = predict_revenue(weekday_data)
        
        weekend_data = test_data.copy()
        weekend_data['Weekday'] = 'Saturday'
        weekend_result = predict_revenue(weekend_data)
        
        print(f"Weekday (Wednesday): Revenue = ${weekday_result['predicted_revenue']:.2f}, Quantity = {weekday_result['estimated_quantity']}")
        print(f"Weekend (Saturday): Revenue = ${weekend_result['predicted_revenue']:.2f}, Quantity = {weekend_result['estimated_quantity']}")
        
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
        for v in variations:
            print(f"${v['unit_price']:<9.2f} {v['raw_quantity']:<10} ${v['revenue']:<14.2f} ${v['profit']:<14.2f}")
        
    except Exception as e:
        print(f"Error in testing: {str(e)}")
        import traceback
        traceback.print_exc() 