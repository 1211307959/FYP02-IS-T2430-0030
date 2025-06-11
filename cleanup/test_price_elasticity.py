#!/usr/bin/env python3
"""
Test script to verify price elasticity - higher prices should result in lower quantities.
"""

import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from revenue_predictor_time_enhanced_ethical import simulate_annual_revenue, predict_revenue

def test_price_elasticity(product_id='2', location='North'):
    """Test that higher prices result in lower quantities."""
    print(f"\n===== Testing Price Elasticity for Product {product_id}, Location {location} =====")
    
    # Base test data
    base_data = {
        '_ProductID': product_id,
        'Location': location,
        'Unit Cost': 100.00,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Year': 2023
    }
    
    # Test various price points
    price_points = [50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    results = []
    for price in price_points:
        test_data = base_data.copy()
        test_data['Unit Price'] = price
        
        print(f"\nTesting price: ${price}")
        try:
            response = requests.post('http://localhost:5000/predict-revenue', json=test_data)
            if response.status_code == 200:
                result = response.json()
                revenue = result.get('predicted_revenue', 0)
                quantity = result.get('estimated_quantity', 0)
                results.append({
                    'price': price,
                    'revenue': revenue,
                    'quantity': quantity
                })
                print(f"  Revenue: ${revenue:.2f}")
                print(f"  Quantity: {quantity}")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    # Check if quantity decreases as price increases
    if len(results) >= 2:
        prices = [r['price'] for r in results]
        quantities = [r['quantity'] for r in results]
        
        # Calculate correlation
        correlation = np.corrcoef(prices, quantities)[0, 1]
        print(f"\nPrice-Quantity Correlation: {correlation:.4f}")
        
        if correlation < 0:
            print("✅ PASS: Price elasticity shows negative correlation (higher price = lower quantity)")
        else:
            print("❌ FAIL: Price elasticity does not show expected negative correlation")
            
        # Find maximum quantity
        max_quantity = max(r['quantity'] for r in results)
        
        # Check if any high price point has zero quantity
        high_price_zero_quantity = any(r['quantity'] == 0 for r in results if r['price'] >= 500)
        
        # Find pattern where quantity decreases from a positive value to zero
        has_elasticity_pattern = False
        found_positive = False
        found_zero = False
        
        for r in sorted(results, key=lambda x: x['price']):
            if r['quantity'] > 0:
                found_positive = True
            if found_positive and r['quantity'] == 0:
                found_zero = True
                break
        
        has_elasticity_pattern = found_positive and found_zero
        
        if has_elasticity_pattern:
            print("✅ PASS: Quantity drops to zero at high prices after being positive at lower prices")
        elif high_price_zero_quantity and max_quantity > 0:
            print("✅ PASS: Some price points have positive quantity while high prices have zero quantity")
        else:
            print("❌ FAIL: No clear pattern of quantity dropping to zero at high prices")
    else:
        print("❌ FAIL: Not enough data points to analyze price elasticity")
    
    return results

def test_price_elasticity_all_locations(product_id='2'):
    """Test price elasticity with 'All' location aggregation."""
    print(f"\n===== Testing Price Elasticity for Product {product_id}, All Locations =====")
    
    # Base test data
    base_data = {
        '_ProductID': product_id,
        'Location': 'All',
        'Unit Cost': 100.00,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Year': 2023
    }
    
    # Test various price points
    price_points = [50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    results = []
    for price in price_points:
        test_data = base_data.copy()
        test_data['Unit Price'] = price
        
        print(f"\nTesting price: ${price}")
        try:
            response = requests.post('http://localhost:5000/predict-revenue', json=test_data)
            if response.status_code == 200:
                result = response.json()
                revenue = result.get('predicted_revenue', 0)
                quantity = result.get('estimated_quantity', 0)
                results.append({
                    'price': price,
                    'revenue': revenue,
                    'quantity': quantity
                })
                print(f"  Revenue: ${revenue:.2f}")
                print(f"  Quantity: {quantity}")
            else:
                print(f"  Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    # Check if quantity decreases as price increases
    if len(results) >= 2:
        prices = [r['price'] for r in results]
        quantities = [r['quantity'] for r in results]
        
        # Calculate correlation
        correlation = np.corrcoef(prices, quantities)[0, 1]
        print(f"\nPrice-Quantity Correlation: {correlation:.4f}")
        
        if correlation < 0:
            print("✅ PASS: Price elasticity shows negative correlation (higher price = lower quantity)")
        else:
            print("❌ FAIL: Price elasticity does not show expected negative correlation")
            
        # Find maximum quantity
        max_quantity = max(r['quantity'] for r in results)
        
        # Check if any high price point has zero quantity
        high_price_zero_quantity = any(r['quantity'] == 0 for r in results if r['price'] >= 500)
        
        # Find pattern where quantity decreases from a positive value to zero
        has_elasticity_pattern = False
        found_positive = False
        found_zero = False
        
        for r in sorted(results, key=lambda x: x['price']):
            if r['quantity'] > 0:
                found_positive = True
            if found_positive and r['quantity'] == 0:
                found_zero = True
                break
        
        has_elasticity_pattern = found_positive and found_zero
        
        if has_elasticity_pattern:
            print("✅ PASS: Quantity drops to zero at high prices after being positive at lower prices")
        elif high_price_zero_quantity and max_quantity > 0:
            print("✅ PASS: Some price points have positive quantity while high prices have zero quantity")
        else:
            print("❌ FAIL: No clear pattern of quantity dropping to zero at high prices")
    else:
        print("❌ FAIL: Not enough data points to analyze price elasticity")
    
    return results

def test_price_elasticity():
    """Test if price elasticity is working correctly"""
    
    print("Testing price elasticity in annual simulations...")
    
    # Test data with low base price
    test_low_price = {
        '_ProductID': 2,
        'Location': 'North',
        'Unit Price': 5051.98,
        'Unit Cost': 2100,
        'Month': 6,
        'Day': 15,
        'Year': 2024,
        'Weekday': 'Saturday'
    }
    
    # Test data with high base price
    test_high_price = {
        '_ProductID': 2,
        'Location': 'North',
        'Unit Price': 15051.98,  # 3x higher
        'Unit Cost': 2100,
        'Month': 6,
        'Day': 15,
        'Year': 2024,
        'Weekday': 'Saturday'
    }
    
    print("\n1. Testing single daily predictions:")
    result_low = predict_revenue(test_low_price)
    result_high = predict_revenue(test_high_price)
    
    print(f"Low price (${test_low_price['Unit Price']:,.0f}): Quantity = {result_low['estimated_quantity']}")
    print(f"High price (${test_high_price['Unit Price']:,.0f}): Quantity = {result_high['estimated_quantity']}")
    
    print("\n2. Testing annual simulations with low base price:")
    results_low = simulate_annual_revenue(test_low_price, min_price_factor=0.5, max_price_factor=1.0, steps=2)
    
    if results_low:
        for r in results_low:
            print(f"Factor {r['price_factor']:.1f} (${r['unit_price']:,.0f}): Qty = {r['predicted_quantity']}, Rev = ${r['predicted_revenue']:,.0f}")
    else:
        print("No results returned for low base price")
    
    print("\n3. Testing annual simulations with high base price:")
    results_high = simulate_annual_revenue(test_high_price, min_price_factor=0.5, max_price_factor=1.0, steps=2)
    
    if results_high:
        for r in results_high:
            print(f"Factor {r['price_factor']:.1f} (${r['unit_price']:,.0f}): Qty = {r['predicted_quantity']}, Rev = ${r['predicted_revenue']:,.0f}")
    else:
        print("No results returned for high base price")
    
    print("\n4. Analysis:")
    if results_low and results_high:
        # Compare the same factor (0.5) for both base prices
        low_50pct = [r for r in results_low if abs(r['price_factor'] - 0.5) < 0.1]
        high_50pct = [r for r in results_high if abs(r['price_factor'] - 0.5) < 0.1]
        
        if low_50pct and high_50pct:
            low_qty = low_50pct[0]['predicted_quantity']
            high_qty = high_50pct[0]['predicted_quantity']
            low_price = low_50pct[0]['unit_price']
            high_price = high_50pct[0]['unit_price']
            
            print(f"50% factor comparison:")
            print(f"  Low base: ${low_price:,.0f} → Qty {low_qty}")
            print(f"  High base: ${high_price:,.0f} → Qty {high_qty}")
            
            if low_qty == high_qty:
                print("  ❌ PROBLEM: Same quantity despite very different prices!")
            else:
                print(f"  ✅ OK: Quantities are different ({low_qty} vs {high_qty})")

def main():
    """Run price elasticity tests."""
    # Test price elasticity for a single location
    single_location_results = test_price_elasticity(product_id='2', location='North')
    
    # Test price elasticity for 'All' locations
    all_locations_results = test_price_elasticity_all_locations(product_id='2')
    
    # Plot results if matplotlib is available
    try:
        # Single location plot
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.plot([r['price'] for r in single_location_results], [r['quantity'] for r in single_location_results], 'o-')
        plt.title('Price vs. Quantity (North)')
        plt.xlabel('Price ($)')
        plt.ylabel('Quantity')
        plt.grid(True)
        
        plt.subplot(2, 2, 2)
        plt.plot([r['price'] for r in single_location_results], [r['revenue'] for r in single_location_results], 'o-')
        plt.title('Price vs. Revenue (North)')
        plt.xlabel('Price ($)')
        plt.ylabel('Revenue ($)')
        plt.grid(True)
        
        # All locations plot
        plt.subplot(2, 2, 3)
        plt.plot([r['price'] for r in all_locations_results], [r['quantity'] for r in all_locations_results], 'o-')
        plt.title('Price vs. Quantity (All Locations)')
        plt.xlabel('Price ($)')
        plt.ylabel('Quantity')
        plt.grid(True)
        
        plt.subplot(2, 2, 4)
        plt.plot([r['price'] for r in all_locations_results], [r['revenue'] for r in all_locations_results], 'o-')
        plt.title('Price vs. Revenue (All Locations)')
        plt.xlabel('Price ($)')
        plt.ylabel('Revenue ($)')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('price_elasticity_test.png')
        print("\nPlot saved as 'price_elasticity_test.png'")
    except Exception as e:
        print(f"\nError creating plot: {str(e)}")

if __name__ == "__main__":
    test_price_elasticity() 