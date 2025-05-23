"""
Test script to validate dashboard data consistency
"""
import requests
import json
import sys
from pprint import pprint

def test_dashboard_data_consistency():
    """
    Test that products don't appear in both top and bottom rankings
    """
    print("Testing dashboard data consistency...")
    
    # Make request to the dashboard data endpoint
    try:
        # Add cache busting to ensure fresh data
        timestamp = int(__import__('time').time())
        print("Calling backend API at http://localhost:5000/dashboard-data...")
        response = requests.get(f'http://localhost:5000/dashboard-data?_={timestamp}', timeout=5)
        
        if not response.ok:
            print(f"HTTP Error from backend: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text[:1000]}")
            return False
            
        data = response.json()
        print("Successfully received response from backend API")
    except requests.RequestException as e:
        print(f"Error accessing backend API: {e}")
        print("Make sure the Flask backend server is running")
        return False
    except Exception as e:
        print(f"Unexpected error with backend API: {e}")
        return False
    
    # Check if the expected data is present
    if not data.get('top_products_data'):
        print("No product data found in response")
        return False
    
    # Get all products with their ranks
    products = data['top_products_data']
    
    # Analyze the product data
    print(f"Total products in response: {len(products)}")
    
    # Count products by rank
    top_products = [p for p in products if p.get('rank') == 'top']
    bottom_products = [p for p in products if p.get('rank') == 'bottom']
    unranked_products = [p for p in products if not p.get('rank')]
    
    print(f"Products with 'top' rank: {len(top_products)}")
    print(f"Products with 'bottom' rank: {len(bottom_products)}")
    print(f"Products without rank: {len(unranked_products)}")
    
    # Get IDs of top and bottom products
    top_ids = {p['id'] for p in top_products}
    bottom_ids = {p['id'] for p in bottom_products}
    
    print("Top product IDs:", sorted(list(top_ids)))
    print("Bottom product IDs:", sorted(list(bottom_ids)))
    
    # Check for overlaps
    overlaps = top_ids.intersection(bottom_ids)
    
    if overlaps:
        print(f"ERROR: Found {len(overlaps)} products that appear in both top and bottom rankings:")
        print(f"Overlapping IDs: {sorted(list(overlaps))}")
        
        # Get details of the overlapping products
        for product_id in overlaps:
            top_product = next((p for p in top_products if p['id'] == product_id), None)
            bottom_product = next((p for p in bottom_products if p['id'] == product_id), None)
            
            print(f"Product ID {product_id}:")
            if top_product:
                print(f"  As top product: {top_product['name']} with profit ${top_product['profit']}")
            if bottom_product:
                print(f"  As bottom product: {bottom_product['name']} with profit ${bottom_product['profit']}")
        
        return False
    
    # Verify profit ranking makes sense
    if top_products:
        top_profits = sorted([p['profit'] for p in top_products], reverse=True)
        print(f"Top products profit range: ${top_profits[-1]} to ${top_profits[0]}")
        
    if bottom_products:
        bottom_profits = sorted([p['profit'] for p in bottom_products])
        print(f"Bottom products profit range: ${bottom_profits[0]} to ${bottom_profits[-1]}")
    
    print("No data inconsistencies found in dashboard data!")
    return True

def verify_frontend_dashboard():
    """
    Test the frontend dashboard API for consistency
    """
    print("\nVerifying frontend dashboard API...")
    
    # Try both possible endpoints
    endpoints = [
        'http://localhost:3000/api/dashboard',
        'http://localhost:3000/api/dashboard-data'
    ]
    
    data = None
    successful_endpoint = None
    
    for endpoint in endpoints:
        try:
            print(f"Trying endpoint: {endpoint}...")
            response = requests.get(endpoint, 
                                headers={'Cache-Control': 'no-cache'}, 
                                timeout=5)
            
            if response.ok:
                data = response.json()
                successful_endpoint = endpoint
                print(f"Successfully received response from {endpoint}")
                break
            else:
                print(f"HTTP Error from {endpoint}: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error text: {response.text[:1000]}")  # Print first 1000 chars
        except requests.RequestException as e:
            print(f"Error accessing {endpoint}: {e}")
        except Exception as e:
            print(f"Unexpected error with {endpoint}: {e}")
    
    if not data:
        print("Failed to get data from any frontend API endpoint")
        print("Make sure Next.js development server is running (npm run dev)")
        return False
    
    # Check if the expected data is present
    if not data.get('top_products_data'):
        print("No product data found in frontend response")
        print(f"Available keys in response: {list(data.keys())}")
        
        # Print a sample of the response
        print(f"Response preview: {json.dumps(data, indent=2)[:500]}...")
        return False
    
    print(f"Using data from {successful_endpoint}")
    
    # Get all products with their ranks
    products = data['top_products_data']
    
    # Count products by rank
    top_products = [p for p in products if p.get('rank') == 'top']
    bottom_products = [p for p in products if p.get('rank') == 'bottom']
    
    print(f"Frontend products with 'top' rank: {len(top_products)}")
    print(f"Frontend products with 'bottom' rank: {len(bottom_products)}")
    
    # Get IDs of top and bottom products
    top_ids = {p['id'] for p in top_products}
    bottom_ids = {p['id'] for p in bottom_products}
    
    print("Frontend top product IDs:", sorted(list(top_ids)))
    print("Frontend bottom product IDs:", sorted(list(bottom_ids)))
    
    # Check for overlaps
    overlaps = top_ids.intersection(bottom_ids)
    
    if overlaps:
        print(f"ERROR in frontend API: Found {len(overlaps)} products that appear in both top and bottom rankings")
        print(f"Overlapping IDs: {sorted(list(overlaps))}")
        return False
    
    print("Frontend dashboard data is consistent!")
    return True

if __name__ == '__main__':
    backend_result = test_dashboard_data_consistency()
    frontend_result = verify_frontend_dashboard()
    
    # Show final result summary
    print("\n=== TEST SUMMARY ===")
    print(f"Backend API test: {'PASS' if backend_result else 'FAIL'}")
    print(f"Frontend API test: {'PASS' if frontend_result else 'FAIL'}")
    
    # Exit with appropriate status code
    if not backend_result or not frontend_result:
        print("\nERROR: At least one test failed! Data inconsistency may still exist.")
        sys.exit(1)
    else:
        print("\nSUCCESS: All tests passed. Data is consistent.")
        sys.exit(0) 