import os
import json
import random
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from revenue_predictor_time_enhanced import predict_revenue, simulate_price_variations, optimize_price
from sales_forecast_enhanced import forecast_sales, forecast_multiple_products, analyze_price_trend

app = Flask(__name__)
CORS(app)

# Default values
DEFAULT_PRODUCT_ID = 1
DEFAULT_LOCATION = "North"
DEFAULT_UNIT_PRICE = 100.0
DEFAULT_UNIT_COST = 50.0

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model': 'Time-Enhanced Revenue Prediction Model',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

def validate_api_input(data):
    """Validate API input data"""
    required_fields = ['Unit Price', 'Unit Cost', 'Location', '_ProductID']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate numeric fields
    numeric_fields = ['Unit Price', 'Unit Cost']
    for field in numeric_fields:
        try:
            value = float(data[field])
            if value < 0:
                return False, f"{field} cannot be negative"
        except:
            return False, f"Invalid {field}: {data[field]}"
    
    return True, ""

@app.route('/predict-revenue', methods=['POST'])
def api_predict_revenue():
    """Predict revenue based on input parameters"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate input
        is_valid, error_message = validate_api_input(data)
        if not is_valid:
            return jsonify({
                'error': error_message
            }), 400
        
        # Add current year if not provided
        if 'Year' not in data:
            data['Year'] = datetime.now().year
        
        # Make prediction
        result = predict_revenue(data)
        
        # Check for errors in prediction
        if 'error' in result:
            return jsonify({
                'error': result['error']
            }), 400
        
        # Return prediction result
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

@app.route('/simulate-revenue', methods=['POST'])
def api_simulate_revenue():
    """Simulate revenue at different price points"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Generate a unique request ID for tracking
        request_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
        
        # Print the incoming request for debugging
        print(f"Received simulate-revenue request ({request_id}): {json.dumps(data, indent=2)}")
        
        # Remove any timestamp or cache-busting fields
        for field in list(data.keys()):
            if field.startswith('_') and field not in ['_ProductID']:
                data.pop(field)
        
        # Handle null values in required fields
        if data.get('_ProductID') is None:
            data['_ProductID'] = DEFAULT_PRODUCT_ID
            
        if data.get('Unit Price') is None:
            data['Unit Price'] = DEFAULT_UNIT_PRICE
            
        if data.get('Unit Cost') is None:
            data['Unit Cost'] = DEFAULT_UNIT_COST
        
        # Check for "All" location - special case
        is_all_locations = False
        original_location = data.get('Location')
        if original_location == 'All':
            is_all_locations = True
            # We'll use the default location for the simulation
            data['Location'] = DEFAULT_LOCATION
            print(f"Using default location ({DEFAULT_LOCATION}) for 'All Locations' request")
        
        # Validate input
        is_valid, error_message = validate_api_input(data)
        if not is_valid:
            return jsonify({
                'error': error_message
            }), 400
            
        # Check for extreme values
        unit_price = float(data.get('Unit Price', 0))
        if unit_price > 100000:
            return jsonify({
                'error': 'Unit Price exceeds maximum allowed value (100000)'
            }), 400
            
        # Get optional parameters from JSON body or query params
        min_price_factor = data.get('min_price_factor', float(request.args.get('min_price_factor', 0.5)))
        max_price_factor = data.get('max_price_factor', float(request.args.get('max_price_factor', 2.0)))
        steps = data.get('steps', int(request.args.get('steps', 7)))
        
        # Remove these parameters from data if they exist
        data.pop('min_price_factor', None)
        data.pop('max_price_factor', None)
        data.pop('steps', None)
        
        # Validate parameters
        if min_price_factor < 0 or max_price_factor < min_price_factor:
            return jsonify({
                'error': 'Invalid price factors'
            }), 400
            
        if steps < 2 or steps > 50:
            return jsonify({
                'error': 'Steps must be between 2 and 50'
            }), 400
        
        # Add current year if not provided
        if 'Year' not in data:
            data['Year'] = datetime.now().year
        
        # Log parameters being used for simulation
        print(f"Simulation parameters ({request_id}): Price=${unit_price}, " + 
              f"Product={data.get('_ProductID')}, Location={original_location}, " +
              f"Factors: {min_price_factor}-{max_price_factor}, Steps: {steps}")
        
        # Simulate price variations
        variations = simulate_price_variations(
            data,
            min_price_factor=min_price_factor,
            max_price_factor=max_price_factor,
            steps=steps
        )
        
        # Check if simulation failed
        if not variations:
            print(f"WARNING: Simulation returned no results - generating fallback data")
            
            # Generate fallback data with realistic elasticity
            base_price = float(data.get('Unit Price', DEFAULT_UNIT_PRICE))
            base_cost = float(data.get('Unit Cost', DEFAULT_UNIT_COST))
            
            # Use exponential decay to generate realistic fallback values
            fallback_variations = generate_fallback_variations(base_price, base_cost)
            
            return jsonify({
                'base_data': data,
                'variations': fallback_variations,
                'note': f"Using fallback data due to simulation error. This is an approximation.",
                'status': 'fallback'
            })
            
        # For "All Locations" case, add a note
        note = None
        if is_all_locations:
            note = f"Using default location ({DEFAULT_LOCATION}) for 'All Locations' simulation"
        
        # Return results
        return jsonify({
            'base_data': data,
            'variations': variations,
            'note': note
        })
        
    except Exception as e:
        print(f"Error in simulate-revenue: {str(e)}")
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

def generate_fallback_variations(base_price, base_cost):
    """Generate fallback price variation data with realistic elasticity"""
    # Generate a reasonable quantity baseline
    base_quantity = max(5, int(1000 / base_price))
    
    # Elasticity factor (negative value means quantity decreases as price increases)
    elasticity = -1.2
    
    variations = []
    
    # Generate variations for different price points
    price_factors = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5, 1.75, 2.0]
    
    for factor in price_factors:
        price = base_price * factor
        
        # Calculate quantity using elasticity formula: Q2 = Q1 * (P2/P1)^elasticity
        quantity = int(base_quantity * (factor ** elasticity))
        
        # For very high prices, ensure quantity approaches zero
        if factor > 1.5:
            quantity = max(0, quantity - int((factor - 1.5) * 20))
            
        # Ensure zero quantity for extreme prices
        if factor >= 10:
            quantity = 0
            
        # Calculate revenue and profit
        revenue = price * quantity
        profit = revenue - (base_cost * quantity)
        
        # Create variation
        scenario_name = "Current Price" if factor == 1.0 else f"{int(factor * 100)}% of Price"
        
        variations.append({
            'Scenario': scenario_name,
            'scenario': scenario_name,
            'Unit Price': price,
            'unit_price': price,
            'unitPrice': price,
            'Predicted Revenue': revenue,
            'predicted_revenue': revenue,
            'revenue': revenue,
            'Predicted Quantity': quantity,
            'predicted_quantity': quantity,
            'quantity': quantity,
            'Profit': profit,
            'profit': profit,
            'price_factor': factor
        })
    
    return variations

@app.route('/optimize-price', methods=['POST'])
def api_optimize_price():
    """Find optimal price for revenue or profit."""
    try:
        # Parse JSON input
        if not request.is_json:
            return jsonify({
                'error': 'Request must be JSON'
            }), 400
            
        data = request.get_json()
        
        # Validate input
        is_valid, error_message = validate_api_input(data)
        if not is_valid:
            return jsonify({
                'error': error_message
            }), 400
            
        # Get optional parameters from JSON body or query params
        metric = data.get('metric', request.args.get('metric', 'profit'))
        if metric not in ['revenue', 'profit']:
            return jsonify({
                'error': 'Metric must be either "revenue" or "profit"'
            }), 400
            
        min_price_factor = data.get('min_price_factor', float(request.args.get('min_price_factor', 0.5)))
        max_price_factor = data.get('max_price_factor', float(request.args.get('max_price_factor', 2.0)))
        steps = data.get('steps', int(request.args.get('steps', 20)))
        
        # Remove these parameters from data if they exist
        data.pop('metric', None)
        data.pop('min_price_factor', None)
        data.pop('max_price_factor', None)
        data.pop('steps', None)
        
        # Validate parameters
        if min_price_factor < 0 or max_price_factor < min_price_factor:
            return jsonify({
                'error': 'Invalid price factors'
            }), 400
            
        if steps < 2 or steps > 50:
            return jsonify({
                'error': 'Steps must be between 2 and 50'
            }), 400
            
        # Add current year if not provided
        if 'Year' not in data:
            data['Year'] = datetime.now().year
        
        # Optimize price
        result = optimize_price(
            data,
            metric=metric,
            min_price_factor=min_price_factor,
            max_price_factor=max_price_factor,
            steps=steps
        )
        
        if not result:
            return jsonify({
                'error': 'Failed to optimize price'
            }), 500
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

@app.route('/forecast-sales', methods=['POST'])
def api_forecast_sales():
    """Forecast sales for a product over a period"""
    try:
        # Parse JSON input
        if not request.is_json:
            return jsonify({
                'error': 'Request must be JSON'
            }), 400
            
        data = request.get_json()
        
        # Validate input
        is_valid, error_message = validate_api_input(data)
        if not is_valid:
            return jsonify({
                'error': error_message
            }), 400
        
        # Get optional parameters
        days = data.get('days', int(request.args.get('days', 30)))
        confidence_interval = data.get('confidence_interval', 
                                     request.args.get('confidence_interval', 'true').lower() == 'true')
        ci_level = data.get('ci_level', float(request.args.get('ci_level', 0.9)))
        
        # Add current year if not provided
        if 'Year' not in data:
            data['Year'] = datetime.now().year
            
        # Set current month and day if not provided
        today = datetime.now()
        if 'Month' not in data:
            data['Month'] = today.month
        if 'Day' not in data:
            data['Day'] = today.day
        if 'Weekday' not in data:
            data['Weekday'] = today.strftime('%A')
        
        # Forecast sales
        forecast = forecast_sales(
            data,
            days=days,
            confidence_interval=confidence_interval,
            ci_level=ci_level
        )
        
        if 'error' in forecast:
            return jsonify({
                'error': forecast['error']
            }), 400
            
        # Transform date objects to strings for JSON serialization
        if 'forecast' in forecast:
            for day in forecast['forecast']:
                if isinstance(day.get('date'), datetime):
                    day['date'] = day['date'].strftime('%Y-%m-%d')
        
        return jsonify(forecast)
        
    except Exception as e:
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

@app.route('/forecast-multiple', methods=['POST'])
def api_forecast_multiple_products():
    """Forecast sales for multiple products over a period"""
    try:
        # Parse JSON input
        if not request.is_json:
            return jsonify({
                'error': 'Request must be JSON'
            }), 400
            
        data = request.get_json()
        
        # Check if products array is provided
        if 'products' not in data or not isinstance(data['products'], list) or not data['products']:
            return jsonify({
                'error': 'Request must include a non-empty products array'
            }), 400
        
        # Get optional parameters
        days = data.get('days', int(request.args.get('days', 30)))
        
        # Add current year to each product if not provided
        current_year = datetime.now().year
        for product in data['products']:
            if 'Year' not in product:
                product['Year'] = current_year
        
        # Forecast sales for multiple products
        forecast = forecast_multiple_products(
            data['products'],
            days=days
        )
        
        if 'error' in forecast:
            return jsonify({
                'error': forecast['error']
            }), 400
            
        # Transform date objects to strings for JSON serialization
        if 'forecast' in forecast:
            for day in forecast['forecast']:
                if isinstance(day.get('date'), datetime):
                    day['date'] = day['date'].strftime('%Y-%m-%d')
        
        return jsonify(forecast)
        
    except Exception as e:
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

@app.route('/forecast-trend', methods=['POST'])
def api_forecast_trend():
    """Analyze price trend impact on forecasts"""
    try:
        # Parse JSON input
        if not request.is_json:
            return jsonify({
                'error': 'Request must be JSON'
            }), 400
            
        data = request.get_json()
        
        # Validate input
        is_valid, error_message = validate_api_input(data)
        if not is_valid:
            return jsonify({
                'error': error_message
            }), 400
        
        # Get optional parameters
        days = data.get('days', int(request.args.get('days', 30)))
        price_points = data.get('price_points', int(request.args.get('price_points', 5)))
        
        # Add current year if not provided
        if 'Year' not in data:
            data['Year'] = datetime.now().year
        
        # Analyze price trend
        trend = analyze_price_trend(
            data,
            days=days,
            price_points=price_points
        )
        
        if 'error' in trend:
            return jsonify({
                'error': trend['error']
            }), 400
            
        return jsonify(trend)
        
    except Exception as e:
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 