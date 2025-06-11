#!/usr/bin/env python3
"""
Test script to verify that frequency and location aggregation fixes are working
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta

# Flask API base URL
API_BASE = "http://localhost:5000"

# Load real product prices from dataset
df = pd.read_csv('trainingdataset.csv')
product_stats = df.groupby('_ProductID')[['Unit Price', 'Unit Cost']].mean()

def get_real_product_data(product_id):
    """Get real average price and cost for a product from the dataset"""
    try:
        price = round(product_stats.loc[product_id, 'Unit Price'])
        cost = round(product_stats.loc[product_id, 'Unit Cost'])
        return price, cost
    except KeyError:
        # Fallback for products not in dataset
        return 5000, 2000

def test_frequency_differences():
    """Test that frequency produces different numbers of periods"""
    print("🧪 Testing Sales Forecasting Fixes")
    print("=" * 50)
    
    # Check if Flask API is running
    try:
        health_response = requests.get(f"{API_BASE}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Flask API is not responding correctly")
            return False
        print("✅ Flask API is running")
    except Exception as e:
        print(f"❌ Flask API is not accessible: {str(e)}")
        return False
    
    print("\n" + "=" * 50)
    print("=== Testing Frequency Support ===")
    print()
    
    # Use real product data
    price, cost = get_real_product_data(1)
    
    test_data = {
        '_ProductID': 1,
        'Location': 'North', 
        'Unit Price': price,
        'Unit Cost': cost,
        'start_date': '2024-01-01',
        'end_date': '2024-01-14'
    }
    
    frequency_results = {}
    
    for freq in ['D', 'W', 'M']:
        print(f"Testing frequency: {freq}")
        try:
            test_data['frequency'] = freq
            response = requests.post(f"{API_BASE}/forecast-sales", json=test_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                periods = len(data.get('forecast', []))
                total_revenue = data.get('summary', {}).get('total_revenue', 0)
                frequency_results[freq] = {
                    'periods': periods,
                    'revenue': total_revenue,
                    'status': 'success'
                }
                print(f"  ✅ {freq}: {periods} periods, ${total_revenue:,.0f} total revenue")
            else:
                print(f"  ❌ {freq}: HTTP {response.status_code}")
                frequency_results[freq] = {'status': 'error', 'code': response.status_code}
                
        except Exception as e:
            print(f"  ❌ {freq}: Exception - {str(e)}")
            frequency_results[freq] = {'status': 'exception', 'error': str(e)}
    
    # Analyze frequency results
    successful_tests = [f for f, r in frequency_results.items() if r.get('status') == 'success']
    
    if len(successful_tests) >= 2:
        daily_periods = frequency_results.get('D', {}).get('periods', 0)
        weekly_periods = frequency_results.get('W', {}).get('periods', 0)
        
        print(f"  📊 Daily periods: {daily_periods}")
        print(f"  📊 Weekly periods: {weekly_periods}")
        
        if daily_periods > 0 and weekly_periods > 0 and daily_periods > weekly_periods:
            print("  ✅ Frequency is working correctly!")
            return True
        else:
            print("  ❌ Frequency may not be working - periods don't vary as expected")
            return False
    else:
        print("  ❌ Not enough successful frequency tests to compare")
        return False

def test_location_aggregation():
    """Test that 'All Locations' aggregates properly"""
    print("\n" + "=" * 50)
    print("=== Testing Location Aggregation ===")
    print()
    
    # Use real product data
    price, cost = get_real_product_data(1)
    
    base_data = {
        '_ProductID': 1,
        'Unit Price': price,
        'Unit Cost': cost,
        'start_date': '2024-01-01',
        'end_date': '2024-01-07',
        'frequency': 'D'
    }
    
    locations_to_test = ['All', 'North', 'Central']
    location_results = {}
    
    for location in locations_to_test:
        print(f"Testing {location} Location{'s' if location == 'All' else ''}")
        try:
            test_data = base_data.copy()
            test_data['Location'] = location
            
            response = requests.post(f"{API_BASE}/forecast-sales", json=test_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                total_revenue = data.get('summary', {}).get('total_revenue', 0)
                location_results[location] = total_revenue
                print(f"  ✅ {location} Location{'s' if location == 'All' else ''}: Total revenue = ${total_revenue:,.0f}")
            else:
                print(f"  ❌ {location} Location{'s' if location == 'All' else ''}: HTTP {response.status_code}")
                location_results[location] = 0
                
        except Exception as e:
            print(f"  ❌ {location} Location{'s' if location == 'All' else ''}: Exception - {str(e)}")
            location_results[location] = 0
    
    # Compare results
    all_locations_revenue = location_results.get('All', 0)
    individual_revenues = [location_results.get(loc, 0) for loc in ['North', 'Central'] if location_results.get(loc, 0) > 0]
    
    print(f"  📊 All Locations revenue: ${all_locations_revenue:,.0f}")
    if individual_revenues:
        max_individual = max(individual_revenues)
        print(f"  📊 Highest individual location: ${max_individual:,.0f}")
        
        if all_locations_revenue > max_individual * 1.2:  # 20% higher threshold
            print("  ✅ Location aggregation is working - All Locations shows proper aggregation!")
            return True
        else:
            print("  ❌ Location aggregation showing similar results - needs improvement")
            return False
    else:
        print("  ❌ Could not compare location results")
        return False

def test_multiple_products():
    """Test that multiple products show higher aggregated results"""
    print("\n" + "=" * 50)
    print("=== Testing Overall vs Single Product ===")
    print()
    
    # Create test with realistic prices
    products_data = []
    for i in range(1, 4):  # Test with 3 products
        price, cost = get_real_product_data(i)
        products_data.append({
            '_ProductID': i,
            'Location': 'All',
            'Unit Price': price,
            'Unit Cost': cost
        })
    
    # Test single product
    print("Testing Single Product Forecast")
    try:
        single_response = requests.post(f"{API_BASE}/forecast-multiple", json={
            "products": [products_data[0]],  # Just first product
            "start_date": '2024-01-01',
            "end_date": '2024-01-07',
            "frequency": 'D'
        }, timeout=15)
        
        if single_response.status_code == 200:
            single_data = single_response.json()
            single_revenue = single_data.get('summary', {}).get('total_revenue', 0)
            print(f"  ✅ Single product: ${single_revenue:,.0f} total revenue")
        else:
            print(f"  ❌ Single product failed: HTTP {single_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Single product failed: {str(e)}")
        return False
    
    # Test multiple products
    print("Testing Overall Business Forecast (all products)")
    try:
        multiple_response = requests.post(f"{API_BASE}/forecast-multiple", json={
            "products": products_data,  # All 3 products
            "start_date": '2024-01-01',
            "end_date": '2024-01-07',
            "frequency": 'D'
        }, timeout=15)
        
        if multiple_response.status_code == 200:
            multiple_data = multiple_response.json()
            multiple_revenue = multiple_data.get('summary', {}).get('total_revenue', 0)
            print(f"  ✅ Multiple products: ${multiple_revenue:,.0f} total revenue")
            
            # Compare results
            if multiple_revenue > single_revenue * 2:  # Should be at least 2x higher
                print(f"  ✅ Multiple products forecast is {multiple_revenue/single_revenue:.1f}x higher - proper SUM aggregation!")
                return True
            else:
                print(f"  ❌ Multiple products only {multiple_revenue/single_revenue:.1f}x higher - should be 3x+ different")
                return False
        else:
            print(f"  ❌ Overall forecast failed: HTTP {multiple_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Overall forecast failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Using REAL product prices from training dataset:")
    for i in range(1, 4):
        price, cost = get_real_product_data(i)
        print(f"  Product {i}: ${price:,} price, ${cost:,} cost")
    print()
    
    # Run all tests
    frequency_pass = test_frequency_differences()
    location_pass = test_location_aggregation()
    products_pass = test_multiple_products()
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    print(f"  {'✅' if frequency_pass else '❌'} {'PASS' if frequency_pass else 'FAIL'}: Frequency Support")
    print(f"  {'✅' if location_pass else '❌'} {'PASS' if location_pass else 'FAIL'}: Location Aggregation")
    print(f"  {'✅' if products_pass else '❌'} {'PASS' if products_pass else 'FAIL'}: Overall vs Single Product")
    
    total_passed = sum([frequency_pass, location_pass, products_pass])
    print(f"\nOverall: {total_passed}/3 tests passed")
    
    if total_passed == 3:
        print("🎉 All tests passed! Sales forecasting fixes are working correctly!")
    else:
        print("⚠️  Some tests failed. Issues may still exist.")

if __name__ == "__main__":
    main() 