import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from pprint import pprint
import os

# Import the 50/50 split model prediction functions
from revenue_predictor_50_50 import predict_revenue, simulate_price_variations, optimize_price

def test_basic_prediction():
    """Test basic revenue prediction functionality"""
    print("\n===== BASIC PREDICTION TEST =====\n")
    
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
    
    # Print formatted result
    print("Model prediction for a $100 product:")
    print(json.dumps(result, indent=2))
    
    # Validate result structure
    expected_keys = ['predicted_revenue', 'estimated_quantity', 'total_cost', 
                     'profit', 'profit_margin_pct', 'unit_price', 'unit_cost']
    missing_keys = [key for key in expected_keys if key not in result]
    
    if missing_keys:
        print(f"❌ Missing expected keys: {missing_keys}")
    else:
        print("✅ Result contains all expected properties")
    
    # Validate prediction values
    if result.get('predicted_revenue', 0) > 0:
        print("✅ Predicted revenue is positive")
    else:
        print("❌ Predicted revenue should be positive")
        
    if result.get('estimated_quantity', 0) >= 0:
        print("✅ Estimated quantity is non-negative")
    else:
        print("❌ Estimated quantity should be non-negative")
    
    return result

def test_price_sensitivity():
    """Test if the model shows appropriate price sensitivity"""
    print("\n===== PRICE SENSITIVITY TEST =====\n")
    
    # Base test data
    base_data = {
        'Unit Price': 100,
        'Unit Cost': 50,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': 12,
        'Year': 2023
    }
    
    # Test with different prices
    prices = [50, 75, 100, 125, 150, 175, 200]
    results = []
    
    print(f"{'Price':10} {'Quantity':10} {'Revenue':15} {'Profit':15}")
    print("-" * 55)
    
    for price in prices:
        test_data = base_data.copy()
        test_data['Unit Price'] = price
        
        result = predict_revenue(test_data)
        results.append(result)
        
        print(f"${price:9.2f} {result['estimated_quantity']:<10} ${result['predicted_revenue']:<14.2f} ${result['profit']:<14.2f}")
    
    # Check price sensitivity (quantity should decrease as price increases)
    low_price = results[0]['estimated_quantity']
    high_price = results[-1]['estimated_quantity']
    
    if low_price > high_price:
        print("\n✅ Model shows appropriate price sensitivity (quantity decreases as price increases)")
    else:
        print("\n❌ Warning: Model does not show expected price sensitivity")
    
    # Plot price sensitivity curves if matplotlib is available
    try:
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Revenue vs Price
        ax1.plot([r['unit_price'] for r in results], [r['predicted_revenue'] for r in results], marker='o', color='blue')
        ax1.set_xlabel('Unit Price ($)')
        ax1.set_ylabel('Predicted Revenue ($)')
        ax1.set_title('Revenue vs Price')
        ax1.grid(True)
        
        # Quantity vs Price
        ax2.plot([r['unit_price'] for r in results], [r['estimated_quantity'] for r in results], marker='o', color='green')
        ax2.set_xlabel('Unit Price ($)')
        ax2.set_ylabel('Estimated Quantity')
        ax2.set_title('Quantity vs Price')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('price_sensitivity_test.png')
        print(f"Price sensitivity graph saved to 'price_sensitivity_test.png'")
    except Exception as e:
        print(f"Couldn't generate plot: {e}")
    
    return results

def test_seasonal_variation():
    """Test if the model captures seasonal variations"""
    print("\n===== SEASONAL VARIATION TEST =====\n")
    
    # Test different seasons
    seasonal_test_data = []
    for month in [1, 4, 7, 10]:  # Winter, Spring, Summer, Fall
        seasonal_test_data.append({
            'Unit Price': 100,
            'Unit Cost': 50,
            'Month': month,
            'Day': 15,
            'Weekday': 'Monday',
            'Location': 'North',
            '_ProductID': 12,
            'Year': 2023
        })
    
    seasons = ["Winter", "Spring", "Summer", "Fall"]
    seasonal_results = []
    
    print(f"{'Season':10} {'Month':10} {'Revenue':15} {'Quantity':10}")
    print("-" * 50)
    
    for i, test_data in enumerate(seasonal_test_data):
        result = predict_revenue(test_data)
        seasonal_results.append(result)
        
        print(f"{seasons[i]:10} {test_data['Month']:<10} ${result['predicted_revenue']:<14.2f} {result['estimated_quantity']:<10}")
    
    # Calculate seasonal variation
    revenues = [r['predicted_revenue'] for r in seasonal_results]
    max_rev = max(revenues)
    min_rev = min(revenues)
    variation_pct = ((max_rev - min_rev) / max_rev) * 100
    
    print(f"\nSeasonal variation: {variation_pct:.2f}%")
    
    # Plot seasonal variations if matplotlib is available
    try:
        plt.figure(figsize=(8, 5))
        plt.bar(seasons, revenues, color='skyblue')
        plt.xlabel('Season')
        plt.ylabel('Predicted Revenue ($)')
        plt.title('Seasonal Variation in Revenue')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('seasonal_variation_test.png')
        print(f"Seasonal variation graph saved to 'seasonal_variation_test.png'")
    except Exception as e:
        print(f"Couldn't generate plot: {e}")
    
    return seasonal_results

def test_location_variation():
    """Test if the model captures location variations"""
    print("\n===== LOCATION VARIATION TEST =====\n")
    
    # Test different locations
    locations = ['North', 'South', 'East', 'West', 'Central']
    location_results = []
    
    print(f"{'Location':10} {'Revenue':15} {'Quantity':10}")
    print("-" * 40)
    
    for location in locations:
        test_data = {
            'Unit Price': 100,
            'Unit Cost': 50,
            'Month': 6,
            'Day': 15,
            'Weekday': 'Friday',
            'Location': location,
            '_ProductID': 12,
            'Year': 2023
        }
        
        result = predict_revenue(test_data)
        location_results.append(result)
        
        print(f"{location:10} ${result['predicted_revenue']:<14.2f} {result['estimated_quantity']:<10}")
    
    # Plot location variations if matplotlib is available
    try:
        plt.figure(figsize=(8, 5))
        plt.bar(locations, [r['predicted_revenue'] for r in location_results], color='lightgreen')
        plt.xlabel('Location')
        plt.ylabel('Predicted Revenue ($)')
        plt.title('Revenue Variation by Location')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('location_variation_test.png')
        print(f"Location variation graph saved to 'location_variation_test.png'")
    except Exception as e:
        print(f"Couldn't generate plot: {e}")
    
    return location_results

def test_price_optimization():
    """Test price optimization functionality"""
    print("\n===== PRICE OPTIMIZATION TEST =====\n")
    
    # Base test data
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
    
    # Test price simulation with more granular steps
    print("Simulating prices from $50 to $200...")
    variations = simulate_price_variations(test_data, min_price_factor=0.5, max_price_factor=2.0, steps=11)
    
    print(f"\n{'Price':10} {'Quantity':10} {'Revenue':15} {'Profit':15}")
    print("-" * 55)
    for v in variations:
        print(f"${v['unit_price']:<9.2f} {v['quantity']:<10} ${v['revenue']:<14.2f} ${v['profit']:<14.2f}")
    
    # Test optimization for revenue
    print("\nOptimizing for REVENUE:")
    rev_opt = optimize_price(test_data, metric="revenue", min_price_factor=0.5, max_price_factor=2.0, steps=30)
    print(f"Optimal price: ${rev_opt['unit_price']:.2f}")
    print(f"Max revenue: ${rev_opt['revenue']:.2f}")
    print(f"Expected quantity: {rev_opt['quantity']}")
    print(f"Expected profit: ${rev_opt['profit']:.2f}")
    
    # Test optimization for profit
    print("\nOptimizing for PROFIT:")
    profit_opt = optimize_price(test_data, metric="profit", min_price_factor=0.5, max_price_factor=2.0, steps=30)
    print(f"Optimal price: ${profit_opt['unit_price']:.2f}")
    print(f"Max profit: ${profit_opt['profit']:.2f}")
    print(f"Expected revenue: ${profit_opt['revenue']:.2f}")
    print(f"Expected quantity: {profit_opt['quantity']}")
    
    return {'revenue_opt': rev_opt, 'profit_opt': profit_opt}

def test_product_variation():
    """Test if the model captures product variations"""
    print("\n===== PRODUCT VARIATION TEST =====\n")
    
    # Test different products
    products = [10, 11, 12, 13, 14]
    product_results = []
    
    print(f"{'Product ID':12} {'Revenue':15} {'Quantity':10}")
    print("-" * 42)
    
    for product_id in products:
        test_data = {
            'Unit Price': 100,
            'Unit Cost': 50,
            'Month': 6,
            'Day': 15,
            'Weekday': 'Friday',
            'Location': 'North',
            '_ProductID': product_id,
            'Year': 2023
        }
        
        result = predict_revenue(test_data)
        product_results.append(result)
        
        print(f"{product_id:<12} ${result['predicted_revenue']:<14.2f} {result['estimated_quantity']:<10}")
    
    return product_results

def test_edge_cases():
    """Test model behavior with edge cases"""
    print("\n===== EDGE CASE TESTS =====\n")
    
    # Base test data
    base_data = {
        'Unit Price': 100,
        'Unit Cost': 50,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': 12,
        'Year': 2023
    }
    
    # Test cases
    edge_cases = [
        {"name": "Very high price", "Unit Price": 1000},
        {"name": "Zero price", "Unit Price": 0},
        {"name": "Price = Cost", "Unit Price": 50},
        {"name": "Holiday season", "Month": 12, "Day": 24},
        {"name": "Weekend", "Weekday": "Saturday"},
    ]
    
    for case in edge_cases:
        test_data = base_data.copy()
        for k, v in case.items():
            if k != "name":
                test_data[k] = v
        
        result = predict_revenue(test_data)
        
        print(f"Test: {case['name']}")
        print(f"  Unit Price: ${test_data['Unit Price']:.2f}")
        print(f"  Predicted Revenue: ${result['predicted_revenue']:.2f}")
        print(f"  Estimated Quantity: {result['estimated_quantity']}")
        print(f"  Profit: ${result['profit']:.2f}")
        print()
    
    # Verify zero quantity with extreme price
    extreme_price_data = base_data.copy()
    extreme_price_data['Unit Price'] = 10000
    extreme_result = predict_revenue(extreme_price_data)
    
    if extreme_result['estimated_quantity'] == 0:
        print("✅ Model correctly predicts zero quantity for extreme price ($10,000)")
    else:
        print(f"❌ Model predicts non-zero quantity ({extreme_result['estimated_quantity']}) for extreme price")
    
    return extreme_result

def run_all_tests():
    """Run all tests and return the results"""
    print("=" * 80)
    print("RUNNING COMPREHENSIVE MODEL TESTS FOR 50/50 SPLIT MODEL")
    print("=" * 80)
    
    results = {}
    
    try:
        # Run all tests
        results['basic_prediction'] = test_basic_prediction()
        results['price_sensitivity'] = test_price_sensitivity() 
        results['seasonal_variation'] = test_seasonal_variation()
        results['location_variation'] = test_location_variation()
        results['product_variation'] = test_product_variation()
        results['price_optimization'] = test_price_optimization()
        results['edge_cases'] = test_edge_cases()
        
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return results

if __name__ == "__main__":
    run_all_tests() 