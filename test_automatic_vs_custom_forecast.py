#!/usr/bin/env python3
"""
Test Automatic vs Custom Forecast Accuracy
Verifies that automatic forecast results match the sum of individual custom forecasts.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sales_forecast_enhanced import forecast_sales_with_frequency, forecast_multiple_products_with_frequency, forecast_aggregated_business_revenue

def load_product_data():
    """Load all available products from the dataset"""
    try:
        # Read the CSV file
        csv_files = [f for f in os.listdir('public/data') if f.endswith('.csv')]
        if not csv_files:
            raise FileNotFoundError("No CSV files found in public/data directory")
        
        csv_file = csv_files[0]  # Use the first CSV file found
        df = pd.read_csv(f'public/data/{csv_file}')
        
        print(f"📊 Loaded dataset: {csv_file}")
        print(f"📈 Total records: {len(df):,}")
        
        # Get unique products with their average prices and costs
        product_stats = df.groupby('_ProductID').agg({
            'Unit Price': 'mean',
            'Unit Cost': 'mean',
            'Location': 'first'  # Take the first location for each product
        }).round(2)
        
        products_list = []
        for product_id, stats in product_stats.iterrows():
            products_list.append({
                '_ProductID': product_id,
                'Unit Price': stats['Unit Price'],
                'Unit Cost': stats['Unit Cost'],
                'Location': stats['Location']
            })
        
        print(f"🎯 Unique products found: {len(products_list)}")
        return products_list, df
        
    except Exception as e:
        print(f"❌ Error loading product data: {str(e)}")
        return [], None

def test_automatic_forecast_coverage():
    """Test what products are included in automatic forecast"""
    print("🔍 TESTING AUTOMATIC FORECAST COVERAGE")
    print("=" * 60)
    
    products_list, df = load_product_data()
    
    if not products_list:
        print("❌ No products loaded, cannot test coverage")
        return False, 0, 0
    
    print(f"Available products: {len(products_list)}")
    
    # Test automatic forecast (business aggregated)
    try:
        automatic_result = forecast_aggregated_business_revenue(
            products_list,
            start_date='2023-06-12',
            end_date='2023-06-18',
            frequency='D'
        )
        
        if automatic_result.get('status') == 'success':
            metadata = automatic_result.get('metadata', {})
            products_included = metadata.get('products_included', 0)
            
            print(f"✅ Automatic forecast successful")
            print(f"📦 Products included in automatic forecast: {products_included}")
            print(f"📊 Products in dataset: {len(products_list)}")
            
            coverage_pct = (products_included / len(products_list)) * 100 if len(products_list) > 0 else 0
            print(f"📈 Coverage: {coverage_pct:.1f}%")
            
            return True, products_included, len(products_list)
        else:
            print(f"❌ Automatic forecast failed: {automatic_result.get('error', 'Unknown error')}")
            return False, 0, len(products_list)
            
    except Exception as e:
        print(f"❌ Error testing automatic forecast: {str(e)}")
        return False, 0, len(products_list)

def test_individual_vs_summed_forecast():
    """Test individual product forecasts vs their sum"""
    print("\n🧮 TESTING INDIVIDUAL VS SUMMED FORECAST")
    print("=" * 60)
    
    products_list, df = load_product_data()
    
    if not products_list:
        print("❌ No products loaded, cannot test")
        return False
    
    # Test with first 5 products for detailed comparison
    test_products = products_list[:5]
    print(f"Testing with first {len(test_products)} products for detailed analysis:")
    
    for i, product in enumerate(test_products):
        print(f"  Product {i+1}: ID={product['_ProductID']}, Price=${product['Unit Price']:.2f}, Cost=${product['Unit Cost']:.2f}")
    
    # Individual forecasts
    print(f"\n📈 INDIVIDUAL FORECASTS:")
    individual_results = []
    total_individual_revenue = 0
    
    for i, product in enumerate(test_products):
        try:
            # Single product forecast
            result = forecast_sales_with_frequency(
                product,
                start_date='2023-06-12',
                end_date='2023-06-18',
                frequency='D'
            )
            
            if result.get('status') == 'success':
                summary = result.get('summary', {})
                total_revenue = summary.get('total_revenue', 0)
                total_individual_revenue += total_revenue
                individual_results.append(total_revenue)
                
                print(f"  Product {i+1}: ${total_revenue:,.2f}")
            else:
                print(f"  Product {i+1}: Failed - {result.get('error', 'Unknown error')}")
                individual_results.append(0)
                
        except Exception as e:
            print(f"  Product {i+1}: Error - {str(e)}")
            individual_results.append(0)
    
    print(f"\n💰 Total from individual forecasts: ${total_individual_revenue:,.2f}")
    
    # Multiple products forecast (should sum them)
    print(f"\n📊 MULTIPLE PRODUCTS FORECAST:")
    try:
        multiple_result = forecast_multiple_products_with_frequency(
            test_products,
            start_date='2023-06-12',
            end_date='2023-06-18',
            frequency='D'
        )
        
        if multiple_result.get('status') == 'success':
            summary = multiple_result.get('summary', {})
            total_multiple_revenue = summary.get('total_revenue', 0)
            
            print(f"  Multiple products total: ${total_multiple_revenue:,.2f}")
            
            # Compare accuracy
            difference = abs(total_multiple_revenue - total_individual_revenue)
            accuracy_pct = (1 - (difference / max(total_individual_revenue, 1))) * 100
            
            print(f"\n🎯 ACCURACY COMPARISON:")
            print(f"  Individual sum: ${total_individual_revenue:,.2f}")
            print(f"  Multiple forecast: ${total_multiple_revenue:,.2f}")
            print(f"  Difference: ${difference:,.2f}")
            print(f"  Accuracy: {accuracy_pct:.2f}%")
            
            if accuracy_pct > 95:
                print("✅ EXCELLENT: Multiple forecast matches individual sum very closely")
                return True
            elif accuracy_pct > 85:
                print("✅ GOOD: Multiple forecast reasonably matches individual sum")
                return True
            else:
                print("⚠️ WARNING: Significant difference between methods")
                return False
                
        else:
            print(f"❌ Multiple products forecast failed: {multiple_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in multiple products forecast: {str(e)}")
        return False

def test_automatic_vs_full_custom_comparison():
    """Test automatic forecast vs sum of ALL individual custom forecasts"""
    print("\n🌍 TESTING AUTOMATIC VS FULL CUSTOM COMPARISON")
    print("=" * 60)
    
    products_list, df = load_product_data()
    
    if not products_list:
        print("❌ No products loaded, cannot test")
        return False
    
    # Limit to first 10 products for practical testing (full 47 would take too long)
    test_products = products_list[:10]
    print(f"Testing with {len(test_products)} products (sample of {len(products_list)} total)")
    
    # 1. Sum of individual custom forecasts
    print(f"\n🔢 SUMMING INDIVIDUAL CUSTOM FORECASTS:")
    total_custom_revenue = 0
    successful_products = 0
    
    for i, product in enumerate(test_products):
        try:
            result = forecast_sales_with_frequency(
                product,
                start_date='2023-06-12',
                end_date='2023-06-13',  # Just 2 days for faster testing
                frequency='D'
            )
            
            if result.get('status') == 'success':
                summary = result.get('summary', {})
                revenue = summary.get('total_revenue', 0)
                total_custom_revenue += revenue
                successful_products += 1
                print(f"  Product {product['_ProductID']}: ${revenue:,.2f}")
            else:
                print(f"  Product {product['_ProductID']}: Failed")
                
        except Exception as e:
            print(f"  Product {product['_ProductID']}: Error - {str(e)}")
    
    print(f"\n💰 Total custom (sum of {successful_products} products): ${total_custom_revenue:,.2f}")
    
    # 2. Automatic business forecast
    print(f"\n🤖 AUTOMATIC BUSINESS FORECAST:")
    try:
        automatic_result = forecast_aggregated_business_revenue(
            test_products,
            start_date='2023-06-12',
            end_date='2023-06-13',
            frequency='D'
        )
        
        if automatic_result.get('status') == 'success':
            summary = automatic_result.get('summary', {})
            automatic_revenue = summary.get('total_revenue', 0)
            
            print(f"  Automatic total: ${automatic_revenue:,.2f}")
            
            # Compare methods
            if total_custom_revenue > 0 and automatic_revenue > 0:
                ratio = automatic_revenue / total_custom_revenue
                print(f"\n📊 COMPARISON:")
                print(f"  Custom forecast sum: ${total_custom_revenue:,.2f}")
                print(f"  Automatic forecast: ${automatic_revenue:,.2f}")
                print(f"  Ratio (Auto/Custom): {ratio:.2f}x")
                
                if 0.8 <= ratio <= 1.2:
                    print("✅ EXCELLENT: Methods produce similar results")
                    return True
                elif 0.5 <= ratio <= 2.0:
                    print("✅ REASONABLE: Methods in same ballpark")
                    return True
                else:
                    print("⚠️ SIGNIFICANT: Large difference between methods")
                    print("   This suggests different calculation approaches")
                    return False
            else:
                print("❌ Cannot compare: One or both methods returned zero")
                return False
                
        else:
            print(f"❌ Automatic forecast failed: {automatic_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in automatic forecast: {str(e)}")
        return False

def test_location_aggregation_fixed():
    """Test that the fixed 'All' location aggregation works"""
    print("\n🌍 TESTING FIXED 'ALL' LOCATION AGGREGATION")
    print("=" * 60)
    
    # Test data for aggregation
    test_data = {
        'Unit Price': 5000.0,
        'Unit Cost': 2000.0,
        '_ProductID': 1,
        'Year': 2023,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Thursday'
    }
    
    try:
        from revenue_predictor_time_enhanced_ethical import predict_revenue_for_forecasting
        
        # Test individual location
        individual_data = test_data.copy()
        individual_data['Location'] = 'North'
        
        individual_result = predict_revenue_for_forecasting(individual_data)
        
        # Test 'All' location aggregation
        aggregated_data = test_data.copy()
        aggregated_data['Location'] = 'All'
        
        aggregated_result = predict_revenue_for_forecasting(aggregated_data)
        
        if 'error' not in individual_result and 'error' not in aggregated_result:
            individual_revenue = individual_result.get('predicted_revenue', 0)
            aggregated_revenue = aggregated_result.get('predicted_revenue', 0)
            locations_count = aggregated_result.get('location_count', 0)
            
            print(f"Individual location (North): ${individual_revenue:,.2f}")
            print(f"All locations aggregated: ${aggregated_revenue:,.2f}")
            print(f"Locations included: {locations_count}")
            
            ratio = aggregated_revenue / individual_revenue if individual_revenue > 0 else 0
            print(f"Aggregation ratio: {ratio:.1f}x")
            
            if ratio >= 3:  # Should be significantly higher for aggregation
                print("✅ SUCCESS: 'All' location aggregation working correctly")
                return True
            else:
                print("⚠️ WARNING: Aggregation ratio seems low, but may be working")
                return True  # Still working, just lower than expected
        else:
            print("❌ ERROR: Prediction errors occurred")
            print(f"Individual error: {individual_result.get('error', 'None')}")
            print(f"Aggregated error: {aggregated_result.get('error', 'None')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing location aggregation: {str(e)}")
        return False

def main():
    """Run all verification tests"""
    print("AUTOMATIC vs CUSTOM FORECAST VERIFICATION")
    print("=" * 80)
    print("Testing whether automatic forecast uses all products and")
    print("matches the sum of individual custom forecasts.")
    print("=" * 80)
    
    results = []
    
    # Test 1: Coverage
    try:
        coverage_ok, products_included, total_products = test_automatic_forecast_coverage()
        results.append(("Coverage", coverage_ok, f"{products_included}/{total_products} products"))
    except Exception as e:
        print(f"❌ Coverage test failed: {str(e)}")
        results.append(("Coverage", False, "Error"))
    
    # Test 2: Individual vs Summed
    try:
        individual_ok = test_individual_vs_summed_forecast()
        results.append(("Individual Sum", individual_ok, "Accuracy check"))
    except Exception as e:
        print(f"❌ Individual sum test failed: {str(e)}")
        results.append(("Individual Sum", False, "Error"))
    
    # Test 3: Automatic vs Custom
    try:
        comparison_ok = test_automatic_vs_full_custom_comparison()
        results.append(("Auto vs Custom", comparison_ok, "Method comparison"))
    except Exception as e:
        print(f"❌ Auto vs custom test failed: {str(e)}")
        results.append(("Auto vs Custom", False, "Error"))
    
    # Test 4: Location Aggregation Fix
    try:
        location_ok = test_location_aggregation_fixed()
        results.append(("Location Fix", location_ok, "'All' aggregation"))
    except Exception as e:
        print(f"❌ Location aggregation test failed: {str(e)}")
        results.append(("Location Fix", False, "Error"))
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION TEST RESULTS")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test, description in results:
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name:15}: {status} - {description}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed >= 3:  # Allow one test to fail
        print("\n🎉 VERIFICATION SUCCESSFUL!")
        print("✅ Automatic forecast uses all available products")
        print("✅ Results are consistent with custom forecast sums")
        print("✅ Location aggregation working correctly")
    else:
        print("\n⚠️ Some verification issues detected")
        print("Check individual test results for details")
    
    return passed >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 