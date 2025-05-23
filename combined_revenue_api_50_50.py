import os
import json
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from revenue_predictor_50_50 import predict_revenue, simulate_price_variations, optimize_price
from flask_cors import CORS
import joblib
import glob
from datetime import datetime
import werkzeug
import shutil

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables to track data files
DATA_DIR = "."  # Default to current directory
CURRENT_DATA_FILE = "trainingdataset.csv"  # Default data file

def validate_api_input(data):
    """Validate API input data"""
    if not isinstance(data, dict):
        return False, "Input must be a JSON object"
        
    required_fields = [
        'Unit Price', 'Unit Cost', 'Month', 'Day',
        'Weekday', 'Location', '_ProductID', 'Year'
    ]
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
        
    return True, None

# Get available data files
@app.route('/data-files', methods=['GET'])
def get_data_files():
    """Get a list of available data files"""
    try:
        # Find all CSV files in the data directory
        csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
        
        # Extract just the filenames
        filenames = [os.path.basename(file) for file in csv_files]
        
        return jsonify({
            'status': 'success',
            'files': filenames,
            'current_file': CURRENT_DATA_FILE
        })
    except Exception as e:
        print(f"Error getting data files: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f"Failed to get data files: {str(e)}"
        }), 500

# Select a data file to use
@app.route('/select-data-file', methods=['POST'])
def select_data_file():
    """Select a data file to use"""
    global CURRENT_DATA_FILE
    
    try:
        # Get filename from request
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({
                'status': 'error',
                'error': 'Missing filename parameter'
            }), 400
        
        # Check if file exists
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'error': f"File not found: {filename}"
            }), 404
        
        # Set current data file
        CURRENT_DATA_FILE = filename
        
        return jsonify({
            'status': 'success',
            'message': f"Selected data file: {filename}"
        })
    except Exception as e:
        print(f"Error selecting data file: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f"Failed to select data file: {str(e)}"
        }), 500

# Reload data files
@app.route('/reload', methods=['GET'])
def reload_data_files():
    """Reload data files from the data directory"""
    try:
        # Nothing to do here since we just scan for files when requested
        # This would be more meaningful if we had a file cache
        
        return jsonify({
            'status': 'success',
            'message': 'Data files reloaded'
        })
    except Exception as e:
        print(f"Error reloading data files: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f"Failed to reload data files: {str(e)}"
        }), 500

# Dashboard data
@app.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data from the current data file"""
    try:
        # Load the current data file
        file_path = os.path.join(DATA_DIR, CURRENT_DATA_FILE)
        if not os.path.exists(file_path):
            return jsonify({
                'status': 'error',
                'error': f"Current data file not found: {CURRENT_DATA_FILE}"
            }), 404
        
        # Load the data
        df = pd.read_csv(file_path)
        
        # Perform initial validation of required columns
        required_columns = ['_ProductID', 'Unit Price', 'Unit Cost', 'Total Revenue']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Warning: Missing columns for proper calculations: {missing_columns}")
        
        # Generate revenue over time data (monthly aggregation)
        # Add month-year field if not present
        if 'Month' in df.columns and 'Year' in df.columns:
            df['MonthYear'] = df.apply(lambda x: f"{int(x['Month'])}/{int(x['Year'])}", axis=1)
        else:
            # If no month/year columns, use the current date
            current_date = datetime.now()
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            df['MonthYear'] = f"{months[current_date.month-1]}/{current_date.year}"
        
        # Revenue by month
        revenue_data = []
        if 'Total Revenue' in df.columns:
            # Check for columns needed for proper profit calculation
            has_profit_data = all(col in df.columns for col in ['Unit Price', 'Unit Cost', 'Quantity'])
            
            # Debug statement
            print(f"Has all columns for profit calculation: {has_profit_data}")
            print(f"Columns in DataFrame: {df.columns.tolist()}")
            
            # Calculate profit if possible, otherwise estimate
            if has_profit_data:
                df['Profit'] = (df['Unit Price'] - df['Unit Cost']) * df['Quantity']
                # Verify profit is calculated
                print(f"Sample profit values: {df['Profit'].head(3).tolist()}")
            elif all(col in df.columns for col in ['Unit Price', 'Unit Cost']):
                # If we have price and cost but no quantity, assume quantity of 1
                df['Profit'] = (df['Unit Price'] - df['Unit Cost']) * 1
                print("Using assumed quantity of 1 for profit calculation")
            
            # Group by month and calculate total revenue and profit
            if 'Profit' in df.columns:
                monthly_data = df.groupby('MonthYear').agg({
                    'Total Revenue': 'sum',
                    'Profit': 'sum'
                }).reset_index()
            else:
                monthly_data = df.groupby('MonthYear')['Total Revenue'].sum().reset_index()
            
            # Convert to list of dicts for the chart
            for _, row in monthly_data.iterrows():
                data_point = {
                    'month': row['MonthYear'],
                    'revenue': round(float(row['Total Revenue']), 2)
                }
                
                # Add profit if available from actual data or estimate it as 40% of revenue
                if 'Profit' in df.columns:
                    data_point['profit'] = round(float(row['Profit']), 2)
                else:
                    # Estimate profit as 40% of revenue if we don't have the actual profit data
                    data_point['profit'] = round(float(row['Total Revenue']) * 0.4, 2)
                
                revenue_data.append(data_point)
        else:
            # Sample data if no Total Revenue column
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            for i, month in enumerate(months):
                revenue = round(10000 + i * 1000 + np.random.randint(1000), 2)
                profit = round(revenue * 0.4, 2)  # Sample profit calculation (40% of revenue)
                revenue_data.append({
                    'month': month,
                    'revenue': revenue,
                    'profit': profit
                })
        
        # After creating all revenue_data points, log some samples
        print(f"Sample revenue data points (first 3): {revenue_data[:3]}")
        
        # Revenue by product
        product_revenue_data = []
        if '_ProductID' in df.columns and 'Total Revenue' in df.columns:
            # Group by product and calculate total revenue
            product_revenue = df.groupby('_ProductID').agg({
                'Total Revenue': 'sum'
            }).reset_index()
            
            # Convert to list of dicts for the chart
            for _, row in product_revenue.iterrows():
                product_id = row['_ProductID']
                product_revenue_data.append({
                    'id': int(product_id),
                    'product': f"Product {product_id}",
                    'name': f"Product {product_id}",
                    'revenue': round(float(row['Total Revenue']), 2)
                })
        else:
            # Sample data if no required columns
            for i in range(1, 6):
                product_revenue_data.append({
                    'id': i,
                    'product': f"Product {i}",
                    'name': f"Product {i}",
                    'revenue': round(5000 + i * 2000 + np.random.randint(1000), 2)
                })
        
        # Revenue by customer (location)
        customer_revenue_data = []
        location_col = 'Location' if 'Location' in df.columns else 'CustomerID'
        if location_col in df.columns and 'Total Revenue' in df.columns:
            # Group by location and calculate total revenue
            customer_revenue = df.groupby(location_col)['Total Revenue'].sum().reset_index()
            
            # Convert to list of dicts for the chart
            for _, row in customer_revenue.iterrows():
                customer_revenue_data.append({
                    'name': str(row[location_col]),
                    'revenue': round(float(row['Total Revenue']), 2)
                })
        else:
            # Sample data if no required columns
            locations = ['North', 'South', 'East', 'West', 'Central']
            for location in locations:
                customer_revenue_data.append({
                    'name': location,
                    'revenue': round(7000 + np.random.randint(5000), 2)
                })
        
        # Top profitable products - FIXED implementation
        top_products_data = []
        bottom_products_data = []
        
        # Check if we have all required columns for profit calculation
        if all(col in df.columns for col in ['_ProductID', 'Unit Price', 'Unit Cost']):
            # Ensure quantity is available or default to 1
            if 'Quantity' not in df.columns:
                df['Quantity'] = 1
                print("Using default quantity of 1 for all products")
            
            # Calculate profit for each row
            df['Profit'] = (df['Unit Price'] - df['Unit Cost']) * df['Quantity']
            
            # Group by product and calculate aggregates
            product_profit = df.groupby('_ProductID').agg({
                'Profit': 'sum',
                'Quantity': 'sum',
                'Total Revenue': 'sum'  # For margin calculation
            }).reset_index()
            
            # Add profit margin calculation if possible
            if 'Total Revenue' in product_profit.columns:
                product_profit['Margin'] = product_profit.apply(
                    lambda x: x['Profit'] / x['Total Revenue'] if x['Total Revenue'] > 0 else 0, 
                    axis=1
                )
            
            # Get top 10 products by profit (fetch more to ensure we have enough non-overlapping products)
            top_products = product_profit.sort_values('Profit', ascending=False).head(10)
            
            # Get bottom 10 products by profit - separate query to ensure different products
            bottom_products = product_profit.sort_values('Profit', ascending=True).head(10)
            
            # Log product counts for debugging
            print(f"Total unique products: {len(product_profit)}")
            print(f"Top products count: {len(top_products)}")
            print(f"Bottom products count: {len(bottom_products)}")
            
            # Extract product IDs for comparison
            top_product_ids = set(top_products['_ProductID'].tolist())
            bottom_product_ids = set(bottom_products['_ProductID'].tolist())
            
            # Log for debugging
            print(f"Top product IDs: {top_product_ids}")
            print(f"Bottom product IDs: {bottom_product_ids}")
            print(f"Overlap in IDs: {top_product_ids.intersection(bottom_product_ids)}")
            
            # Instead of limiting to just a few products, rank ALL products
            # Sort the entire product_profit dataframe by profit
            all_products_sorted = product_profit.sort_values('Profit', ascending=False)
            
            # Use the full sorted data to create the products data
            all_products_data = []
            for i, (idx, row) in enumerate(all_products_sorted.iterrows()):
                product_id = int(row['_ProductID'])
                profit_value = float(row['Profit'])
                margin_value = float(row['Margin']) if 'Margin' in row else 0
                
                # Determine rank based on position: top 10 are 'top', bottom 5 are 'bottom'
                rank = 'top' if i < 10 else ('bottom' if i >= len(all_products_sorted) - 5 else 'middle')
                
                all_products_data.append({
                    'id': product_id,
                    'name': f"Product {product_id}",
                    'product': f"Product {product_id}",  # For backward compatibility
                    'profit': round(profit_value, 2),
                    'quantity': int(row['Quantity']),
                    'revenue': float(row['Total Revenue']) if 'Total Revenue' in row else 0,
                    'margin': round(margin_value * 100, 2),  # Convert to percentage
                    'rank': rank
                })
            
            # Use our complete products list
            top_products_data = all_products_data
            
            # Log the count of products we're sending
            print(f"Sending {len(top_products_data)} products to frontend")
            
        else:
            # Sample data if no required columns - use more realistic values
            print("Creating sample product profit data due to missing columns")
            for i in range(1, 6):
                # Top products have higher profits
                top_products_data.append({
                    'id': i,
                    'name': f"Product {i}",
                    'product': f"Product {i}",  # For backward compatibility
                    'profit': round(1000000 + i * 500000 + np.random.randint(500000), 2),
                    'quantity': 5000 + i * 1000,
                    'revenue': round(2500000 + i * 1000000, 2),
                    'margin': round(40 + i * 2, 2),  # Percentage
                    'rank': 'top' if i > 2 else 'bottom'
                })
        
        # Calculate summary metrics
        total_revenue = df['Total Revenue'].sum() if 'Total Revenue' in df.columns else sum(item['revenue'] for item in revenue_data)
        total_sales = df.shape[0]
        avg_revenue = total_revenue / total_sales if total_sales > 0 else 0
        
        # Also rename product revenue data keys for consistency
        product_revenue_data_fixed = []
        for item in product_revenue_data:
            product_revenue_data_fixed.append({
                'name': item['name'],
                'revenue': item['revenue'],
                'id': item.get('id', 0)
            })
        product_revenue_data = product_revenue_data_fixed
        
        # Return the dashboard data
        return jsonify({
            'status': 'success',
            'revenue_data': revenue_data,
            'product_revenue_data': product_revenue_data,
            'customer_revenue_data': customer_revenue_data,
            'location_revenue_data': customer_revenue_data,  # Add this for compatibility
            'top_products_data': top_products_data,
            'total_revenue': round(total_revenue, 2),
            'total_sales': total_sales,
            'avg_revenue_per_sale': round(avg_revenue, 2)
        })
    except Exception as e:
        print(f"Error getting dashboard data: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full stack trace for better debugging
        return jsonify({
            'status': 'error',
            'error': f"Failed to get dashboard data: {str(e)}"
        }), 500

# Check if model files exist
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test prediction with sample data
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
        
        result = predict_revenue(test_data)
        
        if 'error' in result:
            return jsonify({
                'status': 'error',
                'message': f"Model test failed: {result['error']}"
            }), 500
            
        return jsonify({
            'status': 'healthy',
            'message': 'Model is working correctly',
            'test_prediction': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Health check failed: {str(e)}"
        }), 500

# Get all unique locations
@app.route('/locations', methods=['GET'])
def get_locations():
    """Return all unique locations from the training data."""
    try:
        # Load encoders
        encoders = joblib.load('revenue_encoders_50_50_split.pkl')
        
        # Get location encoder
        if 'Location' in encoders:
            location_encoder = encoders['Location']
            locations = location_encoder.classes_.tolist()
            return jsonify({'locations': locations})
        else:
            return jsonify({'error': 'Location encoder not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all unique products
@app.route('/products', methods=['GET'])
def get_products():
    """Return all unique products from the training data."""
    try:
        # Load encoders
        encoders = joblib.load('revenue_encoders_50_50_split.pkl')
        
        # Get product encoder
        if '_ProductID' in encoders:
            product_encoder = encoders['_ProductID']
            products = product_encoder.classes_.tolist()
            return jsonify({'products': products})
        else:
            return jsonify({'error': 'Product encoder not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Predict revenue
@app.route('/predict-revenue', methods=['POST'])
def api_predict_revenue():
    """Predict revenue using the 50/50 split model."""
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
        
        # Make prediction
        result = predict_revenue(data)
        
        # Check for prediction errors
        if 'error' in result:
            return jsonify({
                'error': result['error']
            }), 400
            
        # Return prediction
        return jsonify({
            'status': 'success',
            'prediction': result
        })
        
    except json.JSONDecodeError:
        return jsonify({
            'error': 'Invalid JSON in request body'
        }), 400
    except Exception as e:
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

# Simulate revenue at different price points
@app.route('/simulate-revenue', methods=['POST'])
def api_simulate_revenue():
    """Simulate revenue at different price points."""
    try:
        # Parse JSON input
        if not request.is_json:
            return jsonify({
                'error': 'Request must be JSON'
            }), 400
            
        data = request.get_json()
        
        # Log the incoming request for debugging
        print(f"Received simulate-revenue request: {json.dumps(data, indent=2)}")
        
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
        
        # Simulate prices
        variations = simulate_price_variations(
            data,
            min_price_factor=min_price_factor,
            max_price_factor=max_price_factor,
            steps=steps
        )
        
        if not variations:
            print(f"Warning: No variations generated for input: {json.dumps(data, indent=2)}")
            # Return fallback data instead of error
            base_price = unit_price
            base_cost = float(data.get('Unit Cost', 0))
            
            # Create more realistic fallback data
            # High price = low quantity, low price = high quantity
            fallback_variations = []
            
            # Calculate reasonable quantities based on price
            if base_price > 10000:  # Very high price
                # Almost no sales at very high prices
                fallback_variations = [
                    {
                        'Scenario': '50% of Price',
                        'Unit Price': base_price * 0.5,
                        'Predicted Revenue': base_price * 0.5 * 2,
                        'Predicted Quantity': 2,
                        'Profit': (base_price * 0.5 * 2) - (base_cost * 2),
                        'revenue': base_price * 0.5 * 2,
                        'quantity': 2,
                        'profit': (base_price * 0.5 * 2) - (base_cost * 2)
                    },
                    {
                        'Scenario': '75% of Price',
                        'Unit Price': base_price * 0.75,
                        'Predicted Revenue': base_price * 0.75 * 1,
                        'Predicted Quantity': 1,
                        'Profit': (base_price * 0.75) - base_cost,
                        'revenue': base_price * 0.75,
                        'quantity': 1,
                        'profit': (base_price * 0.75) - base_cost
                    },
                    {
                        'Scenario': '100% of Price',
                        'Unit Price': base_price,
                        'Predicted Revenue': 0,
                        'Predicted Quantity': 0,
                        'Profit': 0,
                        'revenue': 0,
                        'quantity': 0,
                        'profit': 0
                    },
                    {
                        'Scenario': '125% of Price',
                        'Unit Price': base_price * 1.25,
                        'Predicted Revenue': 0,
                        'Predicted Quantity': 0,
                        'Profit': 0,
                        'revenue': 0,
                        'quantity': 0,
                        'profit': 0
                    },
                    {
                        'Scenario': '150% of Price',
                        'Unit Price': base_price * 1.5,
                        'Predicted Revenue': 0,
                        'Predicted Quantity': 0,
                        'Profit': 0,
                        'revenue': 0,
                        'quantity': 0,
                        'profit': 0
                    },
                    {
                        'Scenario': '175% of Price',
                        'Unit Price': base_price * 1.75,
                        'Predicted Revenue': 0,
                        'Predicted Quantity': 0,
                        'Profit': 0,
                        'revenue': 0,
                        'quantity': 0,
                        'profit': 0
                    },
                    {
                        'Scenario': '200% of Price',
                        'Unit Price': base_price * 2.0,
                        'Predicted Revenue': 0,
                        'Predicted Quantity': 0,
                        'Profit': 0,
                        'revenue': 0,
                        'quantity': 0,
                        'profit': 0
                    }
                ]
            else:
                # More normal price range - create a proper price elasticity curve
                for i, factor in enumerate([0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]):
                    # Price elasticity curve: quantity decreases as price increases
                    # Formula: quantity = base_quantity * (price_factor^elasticity)
                    # Where elasticity is negative (typically -1 to -3 for most products)
                    price = base_price * factor
                    
                    # Vary elasticity based on price range for more realistic behavior
                    if base_price < 2000:
                        # Low-priced products usually have higher elasticity
                        elasticity = -1.8
                        base_quantity = 15
                    elif base_price < 5000:
                        # Mid-priced products have moderate elasticity
                        elasticity = -1.5
                        base_quantity = 10
                    else:
                        # High-priced products have lower elasticity
                        elasticity = -1.2
                        base_quantity = 5
                    
                    # Calculate quantity based on elasticity formula
                    quantity = max(0, round(base_quantity * (factor ** elasticity)))
                    
                    # Calculate revenue and profit
                    revenue = price * quantity
                    profit = revenue - (base_cost * quantity)
                    
                    # Calculate scaled quantity for chart display
                    max_revenue = base_price * base_quantity * 0.5  # Rough estimate of max possible revenue
                    target_quantity = max_revenue / 3  # Target quantity for visualization
                    scale_factor = target_quantity / base_quantity if base_quantity > 0 else 1
                    quantity_for_chart = quantity * scale_factor if quantity > 0 else 0
                    
                    scenario_name = "Current Price" if factor == 1.0 else f"{int(factor * 100)}% of Price"
                    
                    fallback_variations.append({
                        'Scenario': scenario_name,
                        'Unit Price': price,
                        'Predicted Revenue': revenue,
                        'Predicted Quantity': quantity,
                        'Profit': profit,
                        'revenue': revenue,
                        'quantity': quantity_for_chart,  # Use scaled quantity for chart
                        'profit': profit,
                        'raw_quantity': quantity  # Store original quantity
                    })
            
            # Return fallback simulations
            return jsonify({
                'status': 'success',
                'results': fallback_variations,
                'simulations': fallback_variations,
                'note': 'Fallback data generated due to simulation failure'
            })
            
        # Return results with multiple field names for compatibility
        return jsonify({
            'status': 'success',
            'results': variations,
            'simulations': variations
        })
        
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in request body")
        return jsonify({
            'error': 'Invalid JSON in request body'
        }), 400
    except ValueError as e:
        print(f"ValueError in simulate-revenue: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 400
    except Exception as e:
        import traceback
        print(f"Unexpected error in simulate-revenue: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

# Optimize price for revenue or profit
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
            }), 400
            
        # Return results
        return jsonify({
            'status': 'success',
            'optimization': {
                'metric': metric,
                'result': result
            }
        })
        
    except json.JSONDecodeError:
        return jsonify({
            'error': 'Invalid JSON in request body'
        }), 400
    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

# Upload a new data file
@app.route('/upload-file', methods=['POST'])
def upload_file():
    """Handle file upload for new datasets"""
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'error': 'No file part in the request'
            }), 400
        
        file = request.files['file']
        
        # If user does not select file, browser submits an empty file
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'error': 'No file selected'
            }), 400
        
        # Check if the file is a CSV
        if not file.filename.endswith('.csv'):
            return jsonify({
                'status': 'error',
                'error': 'Only CSV files are allowed'
            }), 400
        
        # Save the file to the data directory
        file_path = os.path.join(DATA_DIR, file.filename)
        file.save(file_path)
        
        # Also save to a fixed location for backward compatibility
        if not os.path.exists('data'):
            os.makedirs('data')
        shutil.copy(file_path, os.path.join('data', file.filename))
        
        return jsonify({
            'status': 'success',
            'filename': file.filename,
            'message': f'File uploaded successfully: {file.filename}'
        })
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f"Failed to upload file: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Check if model files exist before starting
    model_path = 'revenue_model_50_50_split.pkl'
    encoders_path = 'revenue_encoders_50_50_split.pkl'
    
    if not os.path.exists(model_path) or not os.path.exists(encoders_path):
        print("Error: Model files not found. Please run train_model_50_50_split.py first.")
        exit(1)
    
    app.run(host='0.0.0.0', port=5000, debug=True) 