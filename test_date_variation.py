#!/usr/bin/env python3
"""
Test script to check if ML model produces different predictions for different dates
"""

from revenue_predictor_time_enhanced_ethical import predict_revenue

def test_date_variations():
    """Test if the model produces different results for different dates"""
    print("🔍 Testing Date Variation in ML Model")
    print("=" * 50)
    
    base_data = {
        '_ProductID': '1',
        'Location': 'North',
        'Unit Price': 5000,
        'Unit Cost': 2000,
        'Year': 2024
    }
    
    test_cases = [
        {'Month': 6, 'Day': 12, 'Weekday': 'Monday'},
        {'Month': 6, 'Day': 13, 'Weekday': 'Tuesday'},
        {'Month': 6, 'Day': 14, 'Weekday': 'Wednesday'},
        {'Month': 6, 'Day': 15, 'Weekday': 'Thursday'},
        {'Month': 6, 'Day': 16, 'Weekday': 'Friday'},
        {'Month': 7, 'Day': 12, 'Weekday': 'Friday'},
        {'Month': 7, 'Day': 13, 'Weekday': 'Saturday'}
    ]
    
    results = []
    
    for i, case in enumerate(test_cases):
        test_data = {**base_data, **case}
        try:
            prediction = predict_revenue(test_data)
            revenue = prediction.get('predicted_revenue', 0)
            quantity = prediction.get('estimated_quantity', 0)
            
            results.append({
                'month': case['Month'],
                'day': case['Day'],
                'weekday': case['Weekday'],
                'revenue': revenue,
                'quantity': quantity
            })
            
            print(f"{i+1}. Month {case['Month']}, Day {case['Day']} ({case['Weekday']}): ${revenue:,.2f} revenue, {quantity:.1f} quantity")
        
        except Exception as e:
            print(f"{i+1}. Month {case['Month']}, Day {case['Day']} ({case['Weekday']}): ERROR - {str(e)}")
    
    # Analysis
    print("\n📊 Analysis:")
    revenues = [r['revenue'] for r in results if r.get('revenue', 0) > 0]
    quantities = [r['quantity'] for r in results if r.get('quantity', 0) > 0]
    
    if revenues:
        unique_revenues = set(revenues)
        unique_quantities = set(quantities)
        
        print(f"• Total test cases: {len(results)}")
        print(f"• Successful predictions: {len(revenues)}")
        print(f"• Unique revenue values: {len(unique_revenues)}")
        print(f"• Unique quantity values: {len(unique_quantities)}")
        print(f"• Revenue range: ${min(revenues):,.2f} - ${max(revenues):,.2f}")
        print(f"• Quantity range: {min(quantities):.1f} - {max(quantities):.1f}")
        
        if len(unique_revenues) == 1:
            print("❌ PROBLEM: All revenues are identical!")
            print(f"   All predictions return: ${revenues[0]:,.2f}")
        else:
            print("✅ GOOD: Model produces different revenues for different dates")
            
        if len(unique_quantities) == 1:
            print("❌ PROBLEM: All quantities are identical!")
            print(f"   All predictions return: {quantities[0]:.1f}")
        else:
            print("✅ GOOD: Model produces different quantities for different dates")
    else:
        print("❌ ERROR: No successful predictions generated")

if __name__ == "__main__":
    test_date_variations() 