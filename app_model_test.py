import json
from revenue_predictor_50_50 import predict_revenue, simulate_price_variations, optimize_price
import requests
import pandas as pd
import time
import sys
from tabulate import tabulate

def verify_model():
    """Simple verification test for the 50/50 split model that can be used in your application.
    Returns True if the model is working properly, False otherwise.
    """
    print("Running model verification test...")
    
    try:
        # Test basic prediction
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
        
        # Basic prediction
        result = predict_revenue(test_data)
        
        # Verify result structure
        required_keys = ['predicted_revenue', 'estimated_quantity', 'total_cost', 
                         'profit', 'profit_margin_pct', 'unit_price', 'unit_cost']
        
        for key in required_keys:
            if key not in result:
                print(f"❌ Missing required key in prediction: {key}")
                return False
                
        # Verify price sensitivity
        low_price_test = test_data.copy()
        low_price_test['Unit Price'] = 50
        high_price_test = test_data.copy()
        high_price_test['Unit Price'] = 200
        
        low_result = predict_revenue(low_price_test)
        high_result = predict_revenue(high_price_test)
        
        if not (low_result['estimated_quantity'] > high_result['estimated_quantity']):
            print("❌ Model does not show proper price sensitivity")
            return False
            
        # Test price simulation
        sim_results = simulate_price_variations(test_data, steps=5)
        
        if len(sim_results) != 5:
            print(f"❌ Price simulation returned {len(sim_results)} results, expected 5")
            return False
            
        # Test optimization
        revenue_opt = optimize_price(test_data, metric="revenue", steps=10)
        profit_opt = optimize_price(test_data, metric="profit", steps=10)
        
        if not (revenue_opt and 'unit_price' in revenue_opt and 'revenue' in revenue_opt):
            print("❌ Revenue optimization failed")
            return False
            
        if not (profit_opt and 'unit_price' in profit_opt and 'profit' in profit_opt):
            print("❌ Profit optimization failed")
            return False
        
        print("✅ Model verification completed successfully!")
        print(f"Sample prediction for $100 product: ${result['predicted_revenue']:.2f} revenue")
        print(f"Optimal price for revenue: ${revenue_opt['unit_price']:.2f}")
        print(f"Optimal price for profit: ${profit_opt['unit_price']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model verification failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def sample_prediction():
    """Make a sample prediction with the 50/50 model and return the formatted result.
    Use this to test a specific scenario in your application.
    """
    # Test data
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
    
    # Return formatted result
    return {
        'status': 'success',
        'test_input': test_data,
        'prediction': result
    }

def sample_price_simulation():
    """Run a sample price simulation with the 50/50 model.
    Use this to test the price simulation functionality in your application.
    """
    # Test data
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
    
    # Simulate prices
    variations = simulate_price_variations(
        test_data,
        min_price_factor=0.5,
        max_price_factor=2.0,
        steps=7
    )
    
    # Return formatted result
    return {
        'status': 'success',
        'test_input': test_data,
        'price_variations': variations
    }

def sample_price_optimization():
    """Run a sample price optimization with the 50/50 model.
    Use this to test the price optimization functionality in your application.
    """
    # Test data
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
    
    # Optimize for both revenue and profit
    revenue_opt = optimize_price(test_data, metric="revenue")
    profit_opt = optimize_price(test_data, metric="profit")
    
    # Return formatted result
    return {
        'status': 'success',
        'test_input': test_data,
        'revenue_optimization': revenue_opt,
        'profit_optimization': profit_opt
    }

# API endpoint URLs
BASE_URL = "http://localhost:5000"
HEALTH_URL = f"{BASE_URL}/health"
LOCATIONS_URL = f"{BASE_URL}/locations"
PRODUCTS_URL = f"{BASE_URL}/products"
SIMULATE_URL = f"{BASE_URL}/simulate-revenue"

def print_section(title):
    """Print a section title with formatting"""
    print("\n" + "="*80)
    print(f" {title.upper()} ".center(80, "="))
    print("="*80 + "\n")

def test_api_health():
    """Test the API health endpoint"""
    print_section("Testing API Health")
    
    try:
        response = requests.get(HEALTH_URL, timeout=10)
        response.raise_for_status()
        health_data = response.json()
        
        if health_data.get('status') == 'healthy':
            print("✅ API is healthy")
            print(f"Message: {health_data.get('message')}")
            return True
        else:
            print("❌ API reports unhealthy status")
            print(f"Status: {health_data.get('status')}")
            print(f"Message: {health_data.get('message')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to API: {str(e)}")
        return False

def get_locations():
    """Get all available locations from the API"""
    try:
        response = requests.get(LOCATIONS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'locations' in data:
            return data['locations']
        else:
            print("❌ No locations found in API response")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get locations: {str(e)}")
        return []

def get_products():
    """Get all available products from the API"""
    try:
        response = requests.get(PRODUCTS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'products' in data:
            return data['products']
        else:
            print("❌ No products found in API response")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get products: {str(e)}")
        return []

def simulate_revenue(data):
    """Simulate revenue with the given data"""
    try:
        response = requests.post(SIMULATE_URL, json=data, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to simulate revenue: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {e.response.text}")
        return None

def test_scenario_simulation(products, locations):
    """Test scenario simulation with various test cases"""
    print_section("Testing Scenario Simulation")
    
    if not products or not locations:
        print("❌ Cannot test scenarios without products and locations")
        return False
    
    # Print available data for reference
    print(f"Available Products: {products[:5]}... (total: {len(products)})")
    print(f"Available Locations: {locations}")
    
    # Create test cases
    test_cases = []
    
    # Case 1: Normal price range
    product_id = products[0] if products else 1
    location = locations[0] if locations else "North"
    test_cases.append({
        "name": "Normal Price",
        "data": {
            "_ProductID": product_id,
            "Unit Price": 100,
            "Unit Cost": 50,
            "Location": location,
            "Month": 6,
            "Day": 15,
            "Weekday": "Friday",
            "Year": 2023
        }
    })
    
    # Case 2: Extreme high price
    test_cases.append({
        "name": "Extreme High Price",
        "data": {
            "_ProductID": product_id,
            "Unit Price": 99999,  # Just under 100k limit
            "Unit Cost": 50,
            "Location": location,
            "Month": 6,
            "Day": 15,
            "Weekday": "Friday",
            "Year": 2023
        }
    })
    
    # Case 3: Low price
    test_cases.append({
        "name": "Low Price",
        "data": {
            "_ProductID": product_id,
            "Unit Price": 10,
            "Unit Cost": 5,
            "Location": location,
            "Month": 6,
            "Day": 15,
            "Weekday": "Friday",
            "Year": 2023
        }
    })
    
    # Case 4: Different product (if available)
    if len(products) > 1:
        test_cases.append({
            "name": "Different Product",
            "data": {
                "_ProductID": products[1],
                "Unit Price": 100,
                "Unit Cost": 50,
                "Location": location,
                "Month": 6,
                "Day": 15,
                "Weekday": "Friday",
                "Year": 2023
            }
        })
    
    # Case 5: Different location (if available)
    if len(locations) > 1:
        test_cases.append({
            "name": "Different Location",
            "data": {
                "_ProductID": product_id,
                "Unit Price": 100,
                "Unit Cost": 50,
                "Location": locations[1],
                "Month": 6,
                "Day": 15,
                "Weekday": "Friday",
                "Year": 2023
            }
        })
    
    # Case 6: All locations
    test_cases.append({
        "name": "All Locations",
        "data": {
            "_ProductID": product_id,
            "Unit Price": 100,
            "Unit Cost": 50,
            "Location": "All",
            "Month": 6,
            "Day": 15,
            "Weekday": "Friday",
            "Year": 2023
        }
    })
    
    # Case 7: Null fields (test default handling)
    test_cases.append({
        "name": "Null Fields",
        "data": {
            "_ProductID": None,
            "Unit Price": None,
            "Unit Cost": None,
            "Location": location,
            "Month": 6,
            "Day": 15,
            "Weekday": "Friday",
            "Year": 2023
        }
    })
    
    # Case 8: Different month/day (seasonality test)
    test_cases.append({
        "name": "Different Season",
        "data": {
            "_ProductID": product_id,
            "Unit Price": 100,
            "Unit Cost": 50,
            "Location": location,
            "Month": 12,  # December
            "Day": 25,    # Christmas day
            "Weekday": "Monday",
            "Year": 2023
        }
    })
    
    # Run all test cases
    results = []
    all_simulations = []
    
    for case in test_cases:
        print(f"\nTesting case: {case['name']}")
        print(f"Input data: {json.dumps(case['data'], indent=2)}")
        
        result = simulate_revenue(case['data'])
        if result is None:
            print(f"❌ Test case failed: {case['name']}")
            results.append({
                "name": case['name'],
                "status": "FAILED",
                "error": "API request failed"
            })
            continue
        
        # Check for expected fields
        if 'status' not in result or 'simulations' not in result and 'results' not in result:
            print(f"❌ Invalid response format for {case['name']}")
            results.append({
                "name": case['name'],
                "status": "FAILED",
                "error": "Invalid response format"
            })
            continue
        
        # Get the simulations/results
        simulations = result.get('simulations') or result.get('results') or []
        if not simulations:
            print(f"⚠️ No simulations returned for {case['name']}")
            results.append({
                "name": case['name'],
                "status": "WARNING",
                "error": "No simulations returned"
            })
            continue
        
        # Add to all simulations for later analysis
        for sim in simulations:
            sim['test_case'] = case['name']
            all_simulations.append(sim)
        
        # Check price elasticity (first item should have lowest price, last should have highest)
        try:
            sorted_prices = sorted([sim.get('Unit Price', 0) for sim in simulations])
            min_price = sorted_prices[0]
            max_price = sorted_prices[-1]
            
            # Find the simulations with min and max prices
            min_price_sim = next((sim for sim in simulations if sim.get('Unit Price', 0) == min_price), None)
            max_price_sim = next((sim for sim in simulations if sim.get('Unit Price', 0) == max_price), None)
            
            if min_price_sim and max_price_sim:
                min_quantity = min_price_sim.get('Predicted Quantity', min_price_sim.get('quantity', 0))
                max_quantity = max_price_sim.get('Predicted Quantity', max_price_sim.get('quantity', 0))
                
                if min_quantity >= max_quantity:
                    print(f"✅ Price elasticity check passed: Lower price ({min_price}) has higher quantity ({min_quantity}) than higher price ({max_price}) with quantity ({max_quantity})")
                    elasticity_status = "PASSED"
                else:
                    print(f"❌ Price elasticity check failed: Lower price ({min_price}) has lower quantity ({min_quantity}) than higher price ({max_price}) with quantity ({max_quantity})")
                    elasticity_status = "FAILED"
            else:
                print("⚠️ Could not verify price elasticity (missing price data)")
                elasticity_status = "WARNING"
        except Exception as e:
            print(f"⚠️ Error checking price elasticity: {str(e)}")
            elasticity_status = "ERROR"
        
        # Print sample of simulations
        print("\nSample simulation results:")
        table_data = []
        table_headers = ["Scenario", "Price", "Quantity", "Revenue", "Profit"]
        
        for i, sim in enumerate(simulations[:3]):  # Show first 3 simulations
            scenario = sim.get('Scenario', f"Scenario {i+1}")
            price = sim.get('Unit Price', 0)
            quantity = sim.get('Predicted Quantity', sim.get('quantity', 0))
            revenue = sim.get('Predicted Revenue', sim.get('revenue', 0))
            profit = sim.get('Profit', sim.get('profit', 0))
            
            table_data.append([scenario, f"${price:.2f}", quantity, f"${revenue:.2f}", f"${profit:.2f}"])
        
        if len(simulations) > 3:
            table_data.append(["...", "...", "...", "...", "..."])
            # Also show the last simulation
            sim = simulations[-1]
            scenario = sim.get('Scenario', f"Scenario {len(simulations)}")
            price = sim.get('Unit Price', 0)
            quantity = sim.get('Predicted Quantity', sim.get('quantity', 0))
            revenue = sim.get('Predicted Revenue', sim.get('revenue', 0))
            profit = sim.get('Profit', sim.get('profit', 0))
            
            table_data.append([scenario, f"${price:.2f}", quantity, f"${revenue:.2f}", f"${profit:.2f}"])
        
        print(tabulate(table_data, headers=table_headers, tablefmt="grid"))
        
        # Check if note is present for "All Locations" case
        note = result.get('note', '')
        if case['name'] == "All Locations" and note and "default location" in note.lower():
            print(f"✅ 'All Locations' note check passed: {note}")
            all_locations_note = "PASSED"
        elif case['name'] == "All Locations" and (not note or "default location" not in note.lower()):
            print("⚠️ 'All Locations' note check warning: Expected note about default location not found")
            all_locations_note = "WARNING"
        else:
            all_locations_note = "N/A"
        
        results.append({
            "name": case['name'],
            "status": "PASSED",
            "simulations_count": len(simulations),
            "price_elasticity": elasticity_status,
            "all_locations_note": all_locations_note
        })
    
    # Analyze all simulations to check for consistent price elasticity
    print_section("Price Elasticity Analysis")
    
    if all_simulations:
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(all_simulations)
        
        # Group by test case and price, then calculate average quantity
        if 'Unit Price' in df.columns and ('quantity' in df.columns or 'Predicted Quantity' in df.columns):
            try:
                # Use the appropriate quantity column
                quantity_col = 'Predicted Quantity' if 'Predicted Quantity' in df.columns else 'quantity'
                
                # Group by test case and price
                grouped = df.groupby(['test_case', 'Unit Price'])[quantity_col].mean().reset_index()
                
                # For each test case, check if quantity decreases as price increases
                test_cases_list = grouped['test_case'].unique()
                
                elasticity_results = []
                for tc in test_cases_list:
                    tc_data = grouped[grouped['test_case'] == tc].sort_values('Unit Price')
                    
                    if len(tc_data) < 2:
                        elasticity_results.append({
                            'test_case': tc,
                            'status': 'SKIPPED',
                            'reason': 'Not enough price points'
                        })
                        continue
                    
                    # Calculate correlation between price and quantity
                    correlation = tc_data['Unit Price'].corr(tc_data[quantity_col])
                    
                    # If correlation is negative, price elasticity is working as expected
                    if correlation < 0:
                        elasticity_results.append({
                            'test_case': tc,
                            'status': 'PASSED',
                            'correlation': correlation
                        })
                    else:
                        elasticity_results.append({
                            'test_case': tc,
                            'status': 'FAILED',
                            'correlation': correlation
                        })
                
                # Print elasticity results
                print("Price elasticity results by test case:")
                for result in elasticity_results:
                    status_symbol = "✅" if result['status'] == 'PASSED' else "❌" if result['status'] == 'FAILED' else "⚠️"
                    if result['status'] == 'SKIPPED':
                        print(f"{status_symbol} {result['test_case']}: {result['status']} - {result['reason']}")
                    else:
                        corr = result.get('correlation', 0)
                        print(f"{status_symbol} {result['test_case']}: {result['status']} - Correlation: {corr:.4f}")
                        
                # Check overall elasticity
                overall_corr = df['Unit Price'].corr(df[quantity_col])
                if overall_corr < 0:
                    print(f"\n✅ OVERALL PRICE ELASTICITY: PASSED - Correlation: {overall_corr:.4f}")
                else:
                    print(f"\n❌ OVERALL PRICE ELASTICITY: FAILED - Correlation: {overall_corr:.4f}")
            except Exception as e:
                print(f"Error analyzing price elasticity: {str(e)}")
        else:
            print("❌ Cannot analyze price elasticity - missing required columns in response")
    else:
        print("❌ No simulation data available for price elasticity analysis")
    
    # Summary of test cases
    print_section("Test Results Summary")
    
    table_data = []
    table_headers = ["Test Case", "Status", "Simulations", "Price Elasticity", "All Locations Note"]
    
    for result in results:
        status_symbol = "✅" if result['status'] == 'PASSED' else "❌" if result['status'] == 'FAILED' else "⚠️"
        elasticity = result.get('price_elasticity', 'N/A')
        elasticity_symbol = "✅" if elasticity == 'PASSED' else "❌" if elasticity == 'FAILED' else "⚠️" if elasticity == 'WARNING' else ""
        
        all_locations = result.get('all_locations_note', 'N/A')
        all_locations_symbol = "✅" if all_locations == 'PASSED' else "❌" if all_locations == 'FAILED' else "⚠️" if all_locations == 'WARNING' else ""
        
        table_data.append([
            result['name'],
            f"{status_symbol} {result['status']}",
            result.get('simulations_count', 'N/A'),
            f"{elasticity_symbol} {elasticity}",
            f"{all_locations_symbol} {all_locations}"
        ])
    
    print(tabulate(table_data, headers=table_headers, tablefmt="grid"))
    
    # Overall status
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    warnings = sum(1 for r in results if r['status'] == 'WARNING')
    
    print(f"\nOVERALL RESULTS: {passed} passed, {failed} failed, {warnings} warnings out of {len(results)} test cases")
    
    return failed == 0

def main():
    """Main test function"""
    print_section("Scenario Planner Test Suite")
    print("Testing API functionality for the revenue prediction model")
    
    # Check if API is healthy
    if not test_api_health():
        print("\n❌ API health check failed. Cannot proceed with tests.")
        return False
    
    # Get available locations and products
    print("\nFetching available locations and products...")
    locations = get_locations()
    products = get_products()
    
    if not locations:
        print("❌ No locations available. Cannot proceed with location-specific tests.")
    
    if not products:
        print("❌ No products available. Cannot proceed with product-specific tests.")
    
    # Test scenario simulation
    return test_scenario_simulation(products, locations)

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Some tests failed. Check the output for details.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed successfully!")
        sys.exit(0) 