#!/usr/bin/env python3

import requests
import json

def test_simulate_revenue_api():
    """Test the Flask API simulate-revenue endpoint directly"""
    
    url = "http://localhost:5000/simulate-revenue"
    
    # Test data matching what the frontend sends
    test_data = {
        '_ProductID': 2,
        'Location': 'All',
        'Unit Price': 5051.98,
        'Unit Cost': 2100,
        'Month': 6,
        'Day': 15,
        'Year': 2024,
        'Weekday': 'Saturday'
    }
    
    print("Testing Flask API simulate-revenue endpoint...")
    print(f"URL: {url}")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Make the request with a longer timeout for annual simulations
        response = requests.post(url, json=test_data, timeout=60)
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse data type: {type(data)}")
            
            if isinstance(data, list):
                print(f"Response is a list with {len(data)} items")
                for i, item in enumerate(data[:3]):  # Show first 3 items
                    print(f"  Item {i}: {json.dumps(item, indent=4)}")
                if len(data) > 3:
                    print(f"  ... and {len(data) - 3} more items")
            else:
                print(f"Response data: {json.dumps(data, indent=2)}")
            
            # Check if this looks like annual data
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                revenue = first_item.get('predicted_revenue', first_item.get('revenue', 0))
                quantity = first_item.get('predicted_quantity', first_item.get('quantity', 0))
                
                print(f"\nAnalysis:")
                print(f"  Revenue: ${revenue:,.2f}")
                print(f"  Quantity: {quantity}")
                
                if revenue > 10000:
                    print("  ✅ This looks like annual data (high revenue)")
                else:
                    print("  ❌ This looks like daily data (low revenue)")
                    
                if quantity > 100:
                    print("  ✅ This looks like annual data (high quantity)")
                else:
                    print("  ❌ This looks like daily data (low quantity)")
        else:
            print(f"\nError response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {e}")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_simulate_revenue_api() 