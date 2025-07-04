import os
import json
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from revenue_predictor_50_50 import predict_revenue, simulate_price_variations, optimize_price
from sales_forecast import forecast_sales, forecast_multiple_products
from flask_cors import CORS
import joblib
import glob
from datetime import datetime, timedelta
import werkzeug
import shutil
import traceback
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set data directory and model paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_PATH = os.path.join(BASE_DIR, 'revenue_model_50_50_split.pkl')
ENCODERS_PATH = os.path.join(BASE_DIR, 'revenue_encoders_50_50_split.pkl')

# Initialize global variables
# Instead of tracking a single current data file, we'll track all files
ALL_DATA_FILES = []
COMBINED_DATA = None
DEFAULT_LOCATION = "North"  # This will be updated when data is loaded
DEFAULT_PRODUCT_ID = 12     # This will be updated when data is loaded

def update_defaults_from_data():
    """Update default values from the data"""
    global DEFAULT_LOCATION, DEFAULT_PRODUCT_ID, COMBINED_DATA
    
    if COMBINED_DATA is None or COMBINED_DATA.empty:
        return
    
    # Get first location
    if 'Location' in COMBINED_DATA.columns:
        locations = COMBINED_DATA['Location'].unique()
        if len(locations) > 0:
            DEFAULT_LOCATION = locations[0]
    
    # Get first product ID
    product_column = None
    for col in ['_ProductID', 'ProductID', 'Product_ID', 'product_id']:
        if col in COMBINED_DATA.columns:
            product_column = col
            break
    
    if product_column:
        product_ids = COMBINED_DATA[product_column].unique()
        if len(product_ids) > 0:
            try:
                DEFAULT_PRODUCT_ID = int(product_ids[0])
            except (ValueError, TypeError):
                # Keep the default if we can't convert to int
                pass

def validate_api_input(data):
    """Validate API input data"""
    if not isinstance(data, dict):
        return False, "Input must be a JSON object"
        
    required_fields = [
        'Unit Price', 'Unit Cost', 'Month', 'Day',
        'Weekday', 'Location', '_ProductID', 'Year'
    ]
    
    # Check for missing fields and apply defaults where possible
    missing_fields = []
    for field in required_fields:
        if field not in data:
            if field == 'Location':
                data[field] = DEFAULT_LOCATION
            elif field == '_ProductID':
                data[field] = DEFAULT_PRODUCT_ID
            elif field in ['Month', 'Day', 'Year']:
                # Use current date for missing date fields
                current_date = datetime.now()
                if field == 'Month':
                    data[field] = current_date.month
                elif field == 'Day':
                    data[field] = current_date.day
                elif field == 'Year':
                    data[field] = current_date.year
            elif field == 'Weekday':
                # Use current weekday
                data[field] = datetime.now().strftime('%A')
            else:
                missing_fields.append(field)
    
    # Handle special "All" location value - convert to first available location for model prediction
    # The model doesn't understand "All" as a location, so we use a real location
    if 'Location' in data and data['Location'] == 'All':
        # For an individual prediction, we'll use the default location
        data['Location'] = DEFAULT_LOCATION
        # (The actual handling of "All" locations for aggregation happens in the endpoints)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
        
    return True, None

# Get available data files
@app.route('/data-files', methods=['GET'])
def get_data_files():
    """Get a list of available data files"""
    global ALL_DATA_FILES
    
    try:
        # Find all CSV files in the data directory
        csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
        
        # Extract just the filenames
        filenames = [os.path.basename(file) for file in csv_files]
        ALL_DATA_FILES = filenames
        
        return jsonify({
            'status': 'success',
            'files': filenames,
            'current_mode': 'combined',
            'message': f"Using combined data from {len(filenames)} files"
        })
    except Exception as e:
        print(f"Error getting data files: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': f"Failed to get data files: {str(e)}"
        }), 500

# Load combined data from all CSV files
def load_combined_data():
    """Load and combine data from all CSV files in the data directory"""
    global COMBINED_DATA, ALL_DATA_FILES
    
    try:
        # Find all CSV files in the data directory
        csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
        
        # Extract just the filenames for tracking
        ALL_DATA_FILES = [os.path.basename(file) for file in csv_files]
        
        if not csv_files:
            print("No CSV files found in data directory")
            COMBINED_DATA = pd.DataFrame()
            return False
        
        # Load and combine all CSV files
        dataframes = []
        for file_path in csv_files:
            try:
                df = pd.read_csv(file_path)
                # Add source file column for tracking
                df['_source_file'] = os.path.basename(file_path)
                dataframes.append(df)
                print(f"Loaded {file_path} with {len(df)} rows")
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
                continue
        
        if not dataframes:
            print("No valid data loaded from CSV files")
            COMBINED_DATA = pd.DataFrame()
            return False
        
        # Combine all dataframes
        # First, get common columns to ensure compatibility
        if len(dataframes) > 1:
            # Find common columns across all dataframes
            common_columns = set(dataframes[0].columns)
            for df in dataframes[1:]:
                common_columns &= set(df.columns)
            
            # If needed, subset dataframes to common columns
            if len(common_columns) < len(dataframes[0].columns):
                print(f"Using {len(common_columns)} common columns across all files")
                for i in range(len(dataframes)):
                    dataframes[i] = dataframes[i][list(common_columns)]
            
            # Add the source file column back if it was removed
            if '_source_file' not in common_columns:
                for i in range(len(dataframes)):
                    dataframes[i]['_source_file'] = os.path.basename(csv_files[i])
        
        # Combine all dataframes
        COMBINED_DATA = pd.concat(dataframes, ignore_index=True)
        print(f"Combined data has {len(COMBINED_DATA)} rows and {len(COMBINED_DATA.columns)} columns")
        
        # Update default values from the loaded data
        update_defaults_from_data()
        
        return True
    except Exception as e:
        print(f"Error loading combined data: {str(e)}")
        COMBINED_DATA = pd.DataFrame()
        return False

# Reload data files
@app.route('/reload', methods=['GET'])
def reload_data_files():
    """Reload data files from the data directory"""
    try:
        # Reload combined data
        success = load_combined_data()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Combined data loaded from {len(ALL_DATA_FILES)} files with {len(COMBINED_DATA)} total rows',
                'files': ALL_DATA_FILES
            })
        else:
            return jsonify({
                'status': 'warning',
                'message': 'No valid data files found or error loading data',
                'files': ALL_DATA_FILES
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
    """Get dashboard data from all data files combined"""
    global COMBINED_DATA
    
    try:
        # If combined data not loaded yet, load it
        if COMBINED_DATA is None or COMBINED_DATA.empty:
            success = load_combined_data()
            if not success:
                return jsonify({
                    'status': 'error',
                    'error': 'No valid data available'
                }), 404
        
        # Use the combined dataframe
        df = COMBINED_DATA
        
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
                product_id = int(row['_ProductID'])
                product_revenue_data.append({
                    'id': product_id,
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
        
        # Revenue by location (previously customer)
        location_data = []
        location_col = 'Location' if 'Location' in df.columns else 'CustomerID'
        if location_col in df.columns and 'Total Revenue' in df.columns:
            # Group by location and calculate total revenue
            location_revenue = df.groupby(location_col)['Total Revenue'].sum().reset_index()
            
            # Convert to list of dicts for the chart
            for _, row in location_revenue.iterrows():
                location_data.append({
                    'name': str(row[location_col]),
                    'revenue': round(float(row['Total Revenue']), 2)
                })
        else:
            # Sample data if no required columns
            locations = ['North', 'South', 'East', 'West', 'Central']
            for location in locations:
                location_data.append({
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
        
        # Update the variable name if it exists
        if 'customer_data' in locals():
            location_data = customer_data
        
        # Return the dashboard data
        return jsonify({
            'status': 'success',
            'revenue_data': revenue_data,
            'product_revenue_data': product_revenue_data,
            'location_revenue_data': location_data,  # Changed from customer_revenue_data
            'top_products_data': top_products_data,
            'total_revenue': round(total_revenue, 2),
            'total_sales': total_sales,
            'avg_revenue_per_sale': round(avg_revenue, 2)
        })
    except Exception as e:
        print(f"Error getting dashboard data: {str(e)}")
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
        # First try to get locations from the actual data files
        global COMBINED_DATA
        
        if COMBINED_DATA is None or COMBINED_DATA.empty:
            success = load_combined_data()
            if not success:
                # Fall back to encoders if data loading fails
                pass
            else:
                # Get unique locations from the loaded data
                if 'Location' in COMBINED_DATA.columns:
                    locations = COMBINED_DATA['Location'].unique().tolist()
                    # Return non-empty locations
                    locations = [loc for loc in locations if loc and not pd.isna(loc)]
                    return jsonify({'locations': locations})
        
        # Fallback to encoders if we can't get from data or there's no Location column
        encoders = joblib.load(ENCODERS_PATH)
        
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
        # First try to get products from the actual data files
        global COMBINED_DATA
        
        if COMBINED_DATA is None or COMBINED_DATA.empty:
            success = load_combined_data()
            if not success:
                # Fall back to encoders if data loading fails
                pass
            else:
                # Get unique products from the loaded data
                product_column = None
                for col in ['_ProductID', 'ProductID', 'Product_ID', 'product_id']:
                    if col in COMBINED_DATA.columns:
                        product_column = col
                        break
                
                if product_column:
                    products = COMBINED_DATA[product_column].unique().tolist()
                    # Return non-empty products, and convert to integers if possible
                    products = [int(prod) if not pd.isna(prod) and str(prod).isdigit() else prod 
                               for prod in products if prod and not pd.isna(prod)]
                    # Sort products
                    products.sort()
                    return jsonify({'products': products})
        
        # Fallback to encoders if we can't get from data
        encoders = joblib.load(ENCODERS_PATH)
        
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
        
        # Check for "All" location - special case
        is_all_locations = False
        if data.get('Location') == 'All':
            is_all_locations = True
            # The validate_api_input function already set a default location
        
        # Make prediction
        result = predict_revenue(data)
        
        # Check for prediction errors
        if 'error' in result:
            return jsonify({
                'error': result['error']
            }), 400
        
        # If "All" locations was selected, add a note in the response
        if is_all_locations:
            result['note'] = "Used default location for prediction. For location-specific predictions, select a specific location."
            
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
            data['Unit Price'] = 100.0  # Default price if none provided
            
        if data.get('Unit Cost') is None:
            data['Unit Cost'] = 50.0  # Default cost if none provided
        
        # Check for "All" location - special case
        is_all_locations = False
        original_location = data.get('Location')
        if original_location == 'All':
            is_all_locations = True
            # We'll handle this specially below
        
        # Validate input (except for All locations case which we'll handle separately)
        if not is_all_locations:
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
        
        # Log parameters being used for simulation
        print(f"Simulation parameters ({request_id}): Price=${unit_price}, " + 
              f"Product={data.get('_ProductID')}, Location={original_location}, " +
              f"Factors: {min_price_factor}-{max_price_factor}, Steps: {steps}")
        
        # Special handling for "All Locations"
        if is_all_locations:
            # Get all available locations
            try:
                encoders = joblib.load(ENCODERS_PATH)
                if 'Location' in encoders:
                    if isinstance(encoders['Location'], list):
                        available_locations = encoders['Location']
                    else:
                        available_locations = encoders['Location'].classes_.tolist()
                else:
                    # Fallback to just using the default location
                    available_locations = [DEFAULT_LOCATION]
            except Exception as e:
                print(f"Error loading location encoders: {str(e)}")
                available_locations = [DEFAULT_LOCATION]
            
            # Maximum number of locations to process to avoid overload
            max_locations = min(5, len(available_locations))
            selected_locations = available_locations[:max_locations]
            
            print(f"Processing {len(selected_locations)} locations for 'All Locations' request: {selected_locations}")
            
            # Initialize combined results
            all_variations_by_factor = {}
            default_note = f"Using combined data from {len(selected_locations)} locations: {', '.join(selected_locations[:3])}"
            if len(selected_locations) > 3:
                default_note += f" and {len(selected_locations) - 3} more"
            default_note += ". Values represent the SUM across all regions."
            
            # Process each location
            location_predictions = {}  # Store predictions by location for debugging
            
            for location in selected_locations:
                # Create a copy of the data for this location
                location_data = data.copy()
                location_data['Location'] = location
                
                # Validate the location-specific data
                is_valid, error_message = validate_api_input(location_data)
                if not is_valid:
                    print(f"Skipping invalid location data for {location}: {error_message}")
                    continue
                
                # Simulate for this location
                try:
                    variations = simulate_price_variations(
                        location_data,
                        min_price_factor=min_price_factor,
                        max_price_factor=max_price_factor,
                        steps=steps
                    )
                    
                    # Store location predictions for debugging
                    location_predictions[location] = {}
                    for var in variations:
                        factor = var.get('price_factor', 0)
                        if factor not in location_predictions[location]:
                            location_predictions[location][factor] = {
                                'quantity': var.get('quantity', 0),
                                'revenue': var.get('revenue', 0),
                                'profit': var.get('profit', 0)
                            }
                    
                    # Group by price factor
                    for var in variations:
                        factor = var.get('price_factor')
                        if factor not in all_variations_by_factor:
                            all_variations_by_factor[factor] = []
                        
                        # Make sure to store the raw quantities from the prediction
                        if 'raw_quantity' not in var and 'quantity' in var:
                            var['raw_quantity'] = var['quantity']
                        
                        all_variations_by_factor[factor].append(var)
                except Exception as e:
                    print(f"Error simulating for location {location}: {str(e)}")
                    # Continue with other locations
            
            # Debug: Print quantities by location to diagnose the issue
            print("\n=== QUANTITY DEBUGGING FOR ALL LOCATIONS ===")
            if location_predictions:
                factors = sorted(list(next(iter(location_predictions.values())).keys()))
                for factor in factors:
                    print(f"\nPrice factor: {factor}")
                    total_qty = 0
                    for location, predictions in location_predictions.items():
                        if factor in predictions:
                            qty = predictions[factor]['quantity']
                            print(f"  {location}: quantity={qty}")
                            total_qty += qty
                    print(f"  TOTAL: {total_qty}")
            print("============================================\n")
            
            # Combine results by SUMMING each metric for each price point
            combined_variations = []
            
            for factor, variations in sorted(all_variations_by_factor.items()):
                if not variations:
                    continue
                    
                # Calculate total values for each metric
                scenario_name = variations[0].get('Scenario', f"{int(factor * 100)}% of Price")
                unit_price = variations[0].get('Unit Price', 0)
                
                # Sum raw quantities (not scaled quantities) across locations
                # First check if raw_quantity exists, otherwise use quantity
                total_raw_quantity = sum(var.get('raw_quantity', var.get('quantity', 0)) for var in variations)
                total_revenue = sum(var.get('revenue', 0) for var in variations)
                total_profit = sum(var.get('profit', 0) for var in variations)
                
                # Log for debugging
                print(f"Factor {factor}: Using raw quantities - Total: {total_raw_quantity}")
                
                # Create the combined variation - use SUMS rather than averages
                combined_var = {
                    'Scenario': scenario_name,
                    'scenario': scenario_name,
                    'Unit Price': unit_price,
                    'unit_price': unit_price,
                    'unitPrice': unit_price,
                    'Predicted Revenue': total_revenue,
                    'predicted_revenue': total_revenue,
                    'revenue': total_revenue,
                    'Predicted Quantity': total_raw_quantity,
                    'predicted_quantity': total_raw_quantity,
                    'raw_quantity': total_raw_quantity,  # Store raw quantity for frontend
                    'quantity': total_raw_quantity,      # Set display quantity to raw quantity
                    'Profit': total_profit,
                    'profit': total_profit,
                    'price_factor': factor,
                    'locations_aggregated': len(variations)
                }
                
                combined_variations.append(combined_var)
            
            # Sort the combined variations by price factor
            combined_variations.sort(key=lambda x: x.get('price_factor', 0))
            
            # Check if we have any results
            if not combined_variations:
                # Return fallback data
                print(f"No valid variations for any location in 'All Locations' request")
                # Generate fallback data (similar to the existing fallback code)
                fallback_variations = generate_fallback_variations(unit_price, data.get('Unit Cost', 50.0))
                
                return jsonify({
                    'status': 'success',
                    'results': fallback_variations,
                    'simulations': fallback_variations,
                    'note': 'Fallback data generated for All Locations. No valid data from any location.',
                    'request_id': request_id
                })
            
            # Return the combined results
            return jsonify({
                'status': 'success',
                'results': combined_variations,
                'simulations': combined_variations,
                'note': default_note,
                'request_id': request_id
            })
        
        # Normal case - single location
        variations = simulate_price_variations(
            data,
            min_price_factor=min_price_factor,
            max_price_factor=max_price_factor,
            steps=steps
        )
        
        # Log the simulation results
        print(f"Simulation results ({request_id}): Generated {len(variations)} variations")
        
        if not variations:
            print(f"Warning: No variations generated for input ({request_id}): {json.dumps(data, indent=2)}")
            # Return fallback data instead of error
            fallback_variations = generate_fallback_variations(unit_price, data.get('Unit Cost', 50.0))
            
            # Return fallback simulations
            print(f"Returning fallback data ({request_id}) with {len(fallback_variations)} variations")
            return jsonify({
                'status': 'success',
                'results': fallback_variations,
                'simulations': fallback_variations,
                'note': 'Fallback data generated due to simulation failure',
                'request_id': request_id
            })
            
        # Return results with multiple field names for compatibility
        return jsonify({
            'status': 'success',
            'results': variations,
            'simulations': variations,
            'request_id': request_id
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
        print(f"Unexpected error in simulate-revenue: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': f"Unexpected error: {str(e)}"
        }), 500

# Helper function to generate fallback variations for extreme price cases
def generate_fallback_variations(base_price, base_cost):
    """Generate fallback price variation data with realistic elasticity"""
    fallback_variations = []
    
    # Check if this is a very high price
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
    
    return fallback_variations

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

# Sales forecasting endpoints
@app.route('/forecast-sales', methods=['POST'])
def api_forecast_sales():
    """
    Forecast sales for a single product over a date range.
    
    Expected JSON input:
    {
        "product_id": "1",
        "location": "North",
        "unit_price": 100.0,
        "unit_cost": 60.0,
        "start_date": "2023-10-01",
        "end_date": "2023-10-31",
        "frequency": "D"  // D=daily, W=weekly, M=monthly
    }
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Missing input data'
            }), 400
        
        # Extract forecast parameters
        product_id = data.get('product_id')
        location = data.get('location')
        unit_price = data.get('unit_price')
        unit_cost = data.get('unit_cost')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        frequency = data.get('frequency', 'D')
        include_confidence = data.get('include_confidence', True)
        
        # Validate required parameters
        if not all([product_id, location, unit_price, unit_cost, start_date, end_date]):
            return jsonify({
                'status': 'error',
                'error': 'Missing required parameters'
            }), 400
        
        # Validate numeric values
        try:
            unit_price = float(unit_price)
            unit_cost = float(unit_cost)
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'error': 'Unit price and unit cost must be numeric'
            }), 400
        
        # Validate dates
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'status': 'error',
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Create base data for forecast
        base_data = {
            '_ProductID': str(product_id),
            'Location': location,
            'Unit Price': unit_price,
            'Unit Cost': unit_cost,
            # Date components will be filled by forecast_sales
            'Year': 2023,  # Will be overridden
            'Month': 1,    # Will be overridden
            'Day': 1,      # Will be overridden
            'Weekday': 'Monday'  # Will be overridden
        }
        
        # Make forecast
        result = forecast_sales(
            base_data=base_data,
            start_date=start_date,
            end_date=end_date,
            freq=frequency,
            include_confidence=include_confidence
        )
        
        # Return forecast results
        return jsonify(result)
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': f"Failed to forecast sales: {str(e)}"
        }), 500

@app.route('/forecast-multiple', methods=['POST'])
def api_forecast_multiple():
    """
    Forecast sales for multiple products over a date range.
    
    Expected JSON input:
    {
        "products": [
            {
                "product_id": "1",
                "location": "North",
                "unit_price": 100.0,
                "unit_cost": 60.0
            },
            // More products...
        ],
        "start_date": "2023-10-01",
        "end_date": "2023-10-31",
        "frequency": "D"  // D=daily, W=weekly, M=monthly
    }
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Missing input data'
            }), 400
        
        # Extract forecast parameters
        products = data.get('products', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        frequency = data.get('frequency', 'D')
        
        # Validate required parameters
        if not all([products, start_date, end_date]):
            return jsonify({
                'status': 'error',
                'error': 'Missing required parameters'
            }), 400
        
        # Validate dates
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'status': 'error',
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Prepare product data
        product_list = []
        for p in products:
            try:
                product_data = {
                    '_ProductID': str(p.get('product_id')),
                    'Location': p.get('location'),
                    'Unit Price': float(p.get('unit_price')),
                    'Unit Cost': float(p.get('unit_cost')),
                    # Date components will be filled by forecast_sales
                    'Year': 2023,  # Will be overridden
                    'Month': 1,    # Will be overridden
                    'Day': 1,      # Will be overridden
                    'Weekday': 'Monday'  # Will be overridden
                }
                product_list.append(product_data)
            except (ValueError, TypeError):
                # Skip invalid products
                continue
        
        # Make forecast for multiple products
        result = forecast_multiple_products(
            product_list=product_list,
            start_date=start_date,
            end_date=end_date,
            freq=frequency
        )
        
        # Return forecast results
        return jsonify(result)
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': f"Failed to forecast multiple products: {str(e)}"
        }), 500

@app.route('/forecast-product-trend', methods=['POST'])
def api_forecast_product_trend():
    """
    Forecast trend for a single product with varying prices.
    
    Expected JSON input:
    {
        "product_id": "1",
        "location": "North",
        "base_price": 100.0,
        "unit_cost": 60.0,
        "price_variations": [0.8, 0.9, 1.0, 1.1, 1.2],  // Price multipliers
        "start_date": "2023-10-01",
        "end_date": "2023-10-31",
        "frequency": "D"  // D=daily, W=weekly, M=monthly
    }
    """
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'error': 'Missing input data'
            }), 400
        
        # Extract parameters
        product_id = data.get('product_id')
        location = data.get('location')
        base_price = data.get('base_price')
        unit_cost = data.get('unit_cost')
        price_variations = data.get('price_variations', [0.8, 0.9, 1.0, 1.1, 1.2])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        frequency = data.get('frequency', 'D')
        
        # Validate required parameters
        if not all([product_id, location, base_price, unit_cost, start_date, end_date]):
            return jsonify({
                'status': 'error',
                'error': 'Missing required parameters'
            }), 400
        
        # Validate numeric values
        try:
            base_price = float(base_price)
            unit_cost = float(unit_cost)
        except (ValueError, TypeError):
            return jsonify({
                'status': 'error',
                'error': 'Base price and unit cost must be numeric'
            }), 400
        
        # Prepare forecasts for each price variation
        forecasts = []
        
        for variation in price_variations:
            # Calculate price for this variation
            price = base_price * variation
            
            # Prepare base data
            base_data = {
                '_ProductID': str(product_id),
                'Location': location,
                'Unit Price': price,
                'Unit Cost': unit_cost,
                # Date components will be filled by forecast_sales
                'Year': 2023,  # Will be overridden
                'Month': 1,    # Will be overridden
                'Day': 1,      # Will be overridden
                'Weekday': 'Monday'  # Will be overridden
            }
            
            # Make forecast
            forecast = forecast_sales(
                base_data=base_data,
                start_date=start_date,
                end_date=end_date,
                freq=frequency,
                include_confidence=False
            )
            
            # Add to results if successful
            if forecast.get('status') == 'success':
                forecasts.append({
                    'price_factor': variation,
                    'unit_price': price,
                    'summary': forecast.get('summary', {}),
                    'forecast': forecast.get('forecast', [])
                })
        
        # Return trend results
        return jsonify({
            'status': 'success',
            'price_variations': forecasts,
            'metadata': {
                'product_id': product_id,
                'location': location,
                'base_price': base_price,
                'unit_cost': unit_cost,
                'start_date': start_date,
                'end_date': end_date,
                'frequency': frequency
            }
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': f"Failed to forecast product trend: {str(e)}"
        }), 500

# Initialize on startup: load combined data
load_combined_data()

if __name__ == '__main__':
    # Check if model files exist before starting
    if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODERS_PATH):
        print("Error: Model files not found. Please run train_model_50_50_split.py first.")
        exit(1)
    
    app.run(host='0.0.0.0', port=5000, debug=True) 