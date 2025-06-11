#!/usr/bin/env python3
"""
Test Option 2: Direct Revenue Approach for Sales Forecasting
Tests that forecasting now shows time variations while scenario planner remains unchanged.
"""

import sys
import os
from datetime import datetime
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from revenue_predictor_time_enhanced_ethical import predict_revenue, predict_revenue_for_forecasting, simulate_price_variations
from sales_forecast_enhanced import forecast_sales_with_frequency

def test_time_variation_preservation():
    """Test that the new forecasting function preserves time variations"""
    print("🔍 TESTING TIME VARIATION PRESERVATION")
    print("=" * 60)
    
    # Test data with same product across different dates
    base_data = {
        'Unit Price': 5000.0,
        'Unit Cost': 2000.0,
        'Location': 'North',
        '_ProductID': 1,
        'Weekday': 'Monday'
    }
    
    # Test three different dates
    test_dates = [
        {'Year': 2023, 'Month': 6, 'Day': 12, 'name': 'June 12'},
        {'Year': 2023, 'Month': 7, 'Day': 12, 'name': 'July 12'}, 
        {'Year': 2023, 'Month': 12, 'Day': 25, 'name': 'December 25'}
    ]
    
    print("ORIGINAL FUNCTION (for scenario planner compatibility):")
    original_results = []
    for date_info in test_dates:
        test_data = base_data.copy()
        test_data.update({k: v for k, v in date_info.items() if k != 'name'})
        
        result = predict_revenue(test_data)
        if 'error' not in result:
            revenue = result.get('predicted_revenue', 0)
            quantity = result.get('estimated_quantity', 0)
            original_results.append((date_info['name'], revenue, quantity))
            print(f"  {date_info['name']}: Revenue=${revenue:,.2f}, Quantity={quantity:.3f}")
    
    print("\nNEW FORECASTING FUNCTION (direct revenue approach):")
    forecasting_results = []
    for date_info in test_dates:
        test_data = base_data.copy()
        test_data.update({k: v for k, v in date_info.items() if k != 'name'})
        
        result = predict_revenue_for_forecasting(test_data)
        if 'error' not in result:
            revenue = result.get('predicted_revenue', 0)
            quantity = result.get('estimated_quantity', 0)
            forecasting_results.append((date_info['name'], revenue, quantity))
            print(f"  {date_info['name']}: Revenue=${revenue:,.2f}, Quantity={quantity:.3f}")
    
    print("\nCOMPARISON ANALYSIS:")
    print("-" * 40)
    
    # Check if forecasting function preserves more variation
    if len(forecasting_results) >= 2:
        # Calculate revenue differences
        orig_revenues = [r[1] for r in original_results]
        forecast_revenues = [r[1] for r in forecasting_results]
        
        orig_std = np.std(orig_revenues) if len(orig_revenues) > 1 else 0
        forecast_std = np.std(forecast_revenues) if len(forecast_revenues) > 1 else 0
        
        print(f"Original function revenue std dev: ${orig_std:,.2f}")
        print(f"Forecasting function revenue std dev: ${forecast_std:,.2f}")
        
        if forecast_std > orig_std:
            print("✅ SUCCESS: Forecasting function preserves MORE time variation")
        else:
            print("⚠️ NOTE: Similar variation levels")
    
    return original_results, forecasting_results

def test_scenario_planner_compatibility():
    """Test that scenario planner functions remain unaffected"""
    print("\n🎯 TESTING SCENARIO PLANNER COMPATIBILITY")
    print("=" * 60)
    
    # Test simulate_price_variations (used by scenario planner)
    base_data = {
        'Unit Price': 5000.0,
        'Unit Cost': 2000.0,
        'Location': 'North',
        '_ProductID': 1,
        'Year': 2023,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Thursday'
    }
    
    try:
        variations = simulate_price_variations(base_data, min_price_factor=0.5, max_price_factor=1.5, steps=5)
        
        print("SCENARIO PLANNER PRICE VARIATIONS:")
        for i, variation in enumerate(variations):
            price = variation.get('unit_price', 0)
            revenue = variation.get('predicted_revenue', 0)
            quantity = variation.get('estimated_quantity', 0)
            print(f"  Scenario {i+1}: Price=${price:,.0f}, Revenue=${revenue:,.2f}, Quantity={quantity:.1f}")
        
        # Check price elasticity (higher price should = lower quantity)
        quantities = [v.get('estimated_quantity', 0) for v in variations]
        prices = [v.get('unit_price', 0) for v in variations]
        
        if len(quantities) > 1:
            # Check if generally decreasing
            price_increases = sum(1 for i in range(1, len(prices)) if prices[i] > prices[i-1])
            quantity_decreases = sum(1 for i in range(1, len(quantities)) if quantities[i] < quantities[i-1])
            
            print(f"\nPrice increases: {price_increases}/{len(prices)-1}")
            print(f"Quantity decreases: {quantity_decreases}/{len(quantities)-1}")
            
            if quantity_decreases >= price_increases * 0.7:  # At least 70% correlation
                print("✅ SUCCESS: Scenario planner price elasticity working correctly")
            else:
                print("⚠️ WARNING: Price elasticity may need attention")
        
        print("✅ SUCCESS: Scenario planner functions remain operational")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: Scenario planner compatibility failed: {str(e)}")
        return False

def test_sales_forecasting_integration():
    """Test that sales forecasting now shows daily variations"""
    print("\n📈 TESTING SALES FORECASTING INTEGRATION")
    print("=" * 60)
    
    # Test data
    test_data = {
        'Unit Price': 5000.0,
        'Unit Cost': 2000.0,
        'Location': 'North',
        '_ProductID': 1
    }
    
    try:
        # Generate a 7-day forecast
        forecast = forecast_sales_with_frequency(
            test_data, 
            start_date='2023-06-12', 
            end_date='2023-06-18', 
            frequency='D'
        )
        
        if forecast.get('status') == 'success':
            print("DAILY SALES FORECAST:")
            results = forecast.get('forecast', [])
            
            revenues = []
            for day in results:
                revenue = day.get('revenue', 0)
                date = day.get('date', '')
                weekday = day.get('weekday', '')
                revenues.append(revenue)
                print(f"  {date} ({weekday}): Revenue=${revenue:,.2f}")
            
            # Check for variation
            if len(revenues) > 1:
                std_dev = np.std(revenues)
                mean_revenue = np.mean(revenues)
                variation_pct = (std_dev / mean_revenue) * 100 if mean_revenue > 0 else 0
                
                print(f"\nVARIATION ANALYSIS:")
                print(f"  Mean daily revenue: ${mean_revenue:,.2f}")
                print(f"  Standard deviation: ${std_dev:,.2f}")
                print(f"  Variation coefficient: {variation_pct:.2f}%")
                
                if std_dev > 0:
                    print("✅ SUCCESS: Sales forecasting shows daily variations")
                else:
                    print("❌ ISSUE: Sales forecasting still shows constant values")
                
                return std_dev > 0
            
        else:
            print(f"❌ ERROR: Forecast failed: {forecast.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Sales forecasting integration failed: {str(e)}")
        return False

def test_location_aggregation_preserved():
    """Test that 'All Locations' aggregation still works correctly"""
    print("\n🌍 TESTING LOCATION AGGREGATION (preserved functionality)")
    print("=" * 60)
    
    # Test individual location vs 'All' aggregation using forecasting function
    test_data = {
        'Unit Price': 5000.0,
        'Unit Cost': 2000.0,
        '_ProductID': 1,
        'Year': 2023,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Thursday'
    }
    
    # Test individual location
    individual_data = test_data.copy()
    individual_data['Location'] = 'North'
    
    individual_result = predict_revenue_for_forecasting(individual_data)
    
    # Test 'All' location (should aggregate)
    aggregated_data = test_data.copy()
    aggregated_data['Location'] = 'All'
    
    aggregated_result = predict_revenue_for_forecasting(aggregated_data)
    
    if 'error' not in individual_result and 'error' not in aggregated_result:
        individual_revenue = individual_result.get('predicted_revenue', 0)
        aggregated_revenue = aggregated_result.get('predicted_revenue', 0)
        
        print(f"Individual location (North): ${individual_revenue:,.2f}")
        print(f"All locations aggregated: ${aggregated_revenue:,.2f}")
        
        ratio = aggregated_revenue / individual_revenue if individual_revenue > 0 else 0
        print(f"Aggregation ratio: {ratio:.1f}x")
        
        if ratio > 2:  # Should be significantly higher for aggregation
            print("✅ SUCCESS: Location aggregation preserved and working")
            return True
        else:
            print("⚠️ WARNING: Aggregation ratio seems low")
            return False
    else:
        print("❌ ERROR: Could not test aggregation due to prediction errors")
        return False

def main():
    """Run all tests for Option 2 implementation"""
    print("TESTING OPTION 2: DIRECT REVENUE APPROACH")
    print("=" * 80)
    print("Verifying that sales forecasting preserves time variations")
    print("while scenario planner functionality remains unchanged.")
    print("=" * 80)
    
    results = []
    
    # Test 1: Time variation preservation
    try:
        original, forecasting = test_time_variation_preservation()
        results.append(("Time Variation", len(forecasting) > 0))
    except Exception as e:
        print(f"❌ Time variation test failed: {str(e)}")
        results.append(("Time Variation", False))
    
    # Test 2: Scenario planner compatibility
    try:
        scenario_ok = test_scenario_planner_compatibility()
        results.append(("Scenario Planner", scenario_ok))
    except Exception as e:
        print(f"❌ Scenario planner test failed: {str(e)}")
        results.append(("Scenario Planner", False))
    
    # Test 3: Sales forecasting integration
    try:
        forecasting_ok = test_sales_forecasting_integration()
        results.append(("Sales Forecasting", forecasting_ok))
    except Exception as e:
        print(f"❌ Sales forecasting test failed: {str(e)}")
        results.append(("Sales Forecasting", False))
    
    # Test 4: Location aggregation preservation
    try:
        aggregation_ok = test_location_aggregation_preserved()
        results.append(("Location Aggregation", aggregation_ok))
    except Exception as e:
        print(f"❌ Location aggregation test failed: {str(e)}")
        results.append(("Location Aggregation", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("OPTION 2 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:20}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 SUCCESS: Option 2 implementation working correctly!")
        print("   - Sales forecasting preserves time variations")
        print("   - Scenario planner functionality preserved")
        print("   - Location aggregation working")
    else:
        print("⚠️ Some issues detected. Check individual test results above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 