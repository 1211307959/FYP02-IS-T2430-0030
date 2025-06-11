#!/usr/bin/env python3
"""
Test script to verify that different products and locations produce different results.
This is a critical test to ensure the model is properly using product and location features.
"""

import requests
import json
from pprint import pprint

def test_location_variations():
    """Test that different locations produce different results with the same product."""
    print("\n===== Testing Location Variations =====")
    
    # Base test data
    base_data = {
        '_ProductID': '2',
        'Unit Price': 200.00,
        'Unit Cost': 100.00,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Year': 2023
    }
    
    # Test locations
    locations = ['North', 'South', 'East', 'West', 'Central']
    
    results = {}
    for location in locations:
        test_data = base_data.copy()
        test_data['Location'] = location
        
        print(f"\nTesting location: {location}")
        try:
            response = requests.post('http://localhost:5000/predict-revenue', json=test_data)
            if response.status_code == 200:
                result = response.json()
                revenue = result.get('predicted_revenue', 0)
                quantity = result.get('estimated_quantity', 0)
                results[location] = {'revenue': revenue, 'quantity': quantity}
                print(f"  Revenue: ${revenue:.2f}")
                print(f"  Quantity: {quantity}")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    # Check for variations
    revenues = [results[loc]['revenue'] for loc in locations if loc in results]
    quantities = [results[loc]['quantity'] for loc in locations if loc in results]
    
    if len(set(revenues)) > 1:
        print("\n✅ PASS: Different locations produce different revenue predictions")
    else:
        print("\n❌ FAIL: All locations produce the same revenue prediction")
    
    if len(set(quantities)) > 1:
        print("✅ PASS: Different locations produce different quantity predictions")
    else:
        print("❌ FAIL: All locations produce the same quantity prediction")
    
    return results

def test_product_variations():
    """Test that different products produce different results with the same location."""
    print("\n===== Testing Product Variations =====")
    
    # Base test data
    base_data = {
        'Location': 'North',
        'Unit Price': 200.00,
        'Unit Cost': 100.00,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Year': 2023
    }
    
    # Test products
    products = ['1', '2', '3', '10', '20', '30', '40']
    
    results = {}
    for product in products:
        test_data = base_data.copy()
        test_data['_ProductID'] = product
        
        print(f"\nTesting product: {product}")
        try:
            response = requests.post('http://localhost:5000/predict-revenue', json=test_data)
            if response.status_code == 200:
                result = response.json()
                revenue = result.get('predicted_revenue', 0)
                quantity = result.get('estimated_quantity', 0)
                results[product] = {'revenue': revenue, 'quantity': quantity}
                print(f"  Revenue: ${revenue:.2f}")
                print(f"  Quantity: {quantity}")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    # Check for variations
    revenues = [results[prod]['revenue'] for prod in products if prod in results]
    quantities = [results[prod]['quantity'] for prod in products if prod in results]
    
    if len(set(revenues)) > 1:
        print("\n✅ PASS: Different products produce different revenue predictions")
    else:
        print("\n❌ FAIL: All products produce the same revenue prediction")
    
    if len(set(quantities)) > 1:
        print("✅ PASS: Different products produce different quantity predictions")
    else:
        print("❌ FAIL: All products produce the same quantity prediction")
    
    return results

def test_all_location_aggregation():
    """Test that 'All' location properly aggregates results across locations."""
    print("\n===== Testing All Location Aggregation =====")
    
    # Base test data
    base_data = {
        '_ProductID': '2',
        'Unit Price': 200.00,
        'Unit Cost': 100.00,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Year': 2023
    }
    
    # Test with All location
    all_location_data = base_data.copy()
    all_location_data['Location'] = 'All'
    
    print("\nTesting location: All")
    try:
        response = requests.post('http://localhost:5000/predict-revenue', json=all_location_data)
        if response.status_code == 200:
            all_result = response.json()
            all_revenue = all_result.get('predicted_revenue', 0)
            all_quantity = all_result.get('estimated_quantity', 0)
            print(f"  Revenue: ${all_revenue:.2f}")
            print(f"  Quantity: {all_quantity}")
            print(f"  Locations aggregated: {all_result.get('locations_aggregated', False)}")
            print(f"  Location count: {all_result.get('location_count', 0)}")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  Error: {str(e)}")
        return None
    
    # Test with individual locations
    locations = ['North', 'South', 'East', 'West', 'Central']
    individual_results = {}
    
    total_revenue = 0
    total_quantity = 0
    
    for location in locations:
        test_data = base_data.copy()
        test_data['Location'] = location
        
        print(f"\nTesting individual location: {location}")
        try:
            response = requests.post('http://localhost:5000/predict-revenue', json=test_data)
            if response.status_code == 200:
                result = response.json()
                revenue = result.get('predicted_revenue', 0)
                quantity = result.get('estimated_quantity', 0)
                individual_results[location] = {'revenue': revenue, 'quantity': quantity}
                total_revenue += revenue
                total_quantity += quantity
                print(f"  Revenue: ${revenue:.2f}")
                print(f"  Quantity: {quantity}")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    print("\nComparison:")
    print(f"  'All' location revenue: ${all_revenue:.2f}")
    print(f"  Sum of individual location revenues: ${total_revenue:.2f}")
    print(f"  'All' location quantity: {all_quantity}")
    print(f"  Sum of individual location quantities: {total_quantity}")
    
    # The "All" aggregation should be close to the sum of individual locations
    revenue_ratio = all_revenue / total_revenue if total_revenue > 0 else 0
    
    if 0.9 <= revenue_ratio <= 1.1:
        print("\n✅ PASS: 'All' location correctly aggregates revenue from individual locations")
    else:
        print(f"\n❌ FAIL: 'All' location revenue (${all_revenue:.2f}) doesn't match sum of individual locations (${total_revenue:.2f})")
    
    if all_quantity == total_quantity:
        print("✅ PASS: 'All' location correctly aggregates quantities from individual locations")
    else:
        print(f"❌ FAIL: 'All' location quantity ({all_quantity}) doesn't match sum of individual locations ({total_quantity})")
    
    return {'all': {'revenue': all_revenue, 'quantity': all_quantity}, 'individual': individual_results}

def main():
    """Run all tests."""
    # Test location variations
    location_results = test_location_variations()
    
    # Test product variations
    product_results = test_product_variations()
    
    # Test All location aggregation
    aggregation_results = test_all_location_aggregation()
    
    print("\n===== Test Summary =====")
    if location_results and len(set([r['revenue'] for r in location_results.values()])) > 1:
        print("✅ PASS: Location variation test")
    else:
        print("❌ FAIL: Location variation test")
    
    if product_results and len(set([r['revenue'] for r in product_results.values()])) > 1:
        print("✅ PASS: Product variation test")
    else:
        print("❌ FAIL: Product variation test")
    
    if aggregation_results:
        all_revenue = aggregation_results['all']['revenue']
        total_revenue = sum([r['revenue'] for r in aggregation_results['individual'].values()])
        revenue_ratio = all_revenue / total_revenue if total_revenue > 0 else 0
        
        if 0.9 <= revenue_ratio <= 1.1:
            print("✅ PASS: All location aggregation test")
        else:
            print("❌ FAIL: All location aggregation test")
    else:
        print("❌ FAIL: All location aggregation test (test didn't complete)")

if __name__ == "__main__":
    main() 