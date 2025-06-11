#!/usr/bin/env python3
"""
Test script to check how 'All' location is handled in predictions
"""

from revenue_predictor_time_enhanced_ethical import predict_revenue

def test_all_location_handling():
    """Test how 'All' location is handled vs individual locations"""
    print("🔍 Testing 'All' Location Handling")
    print("=" * 50)
    
    base_data = {
        '_ProductID': '1',
        'Unit Price': 5000,
        'Unit Cost': 2000,
        'Year': 2024,
        'Month': 6,
        'Day': 12,
        'Weekday': 'Monday'
    }
    
    # Test individual locations
    individual_locations = ['North', 'South', 'East', 'West', 'Central']
    individual_results = {}
    
    print("📍 Testing Individual Locations:")
    for location in individual_locations:
        test_data = base_data.copy()
        test_data['Location'] = location
        
        try:
            prediction = predict_revenue(test_data)
            revenue = prediction.get('predicted_revenue', 0)
            quantity = prediction.get('estimated_quantity', 0)
            
            individual_results[location] = {
                'revenue': revenue,
                'quantity': quantity
            }
            
            print(f"• {location}: ${revenue:,.2f} revenue, {quantity:.1f} quantity")
        
        except Exception as e:
            print(f"• {location}: ERROR - {str(e)}")
            individual_results[location] = {'revenue': 0, 'quantity': 0}
    
    # Test 'All' location
    print("\\n🌐 Testing 'All' Location:")
    test_data = base_data.copy()
    test_data['Location'] = 'All'
    
    try:
        prediction = predict_revenue(test_data)
        all_revenue = prediction.get('predicted_revenue', 0)
        all_quantity = prediction.get('estimated_quantity', 0)
        locations_aggregated = prediction.get('locations_aggregated', False)
        location_count = prediction.get('location_count', 0)
        
        print(f"• All Locations: ${all_revenue:,.2f} revenue, {all_quantity:.1f} quantity")
        print(f"• Locations aggregated: {locations_aggregated}")
        print(f"• Location count: {location_count}")
        
    except Exception as e:
        print(f"• All Locations: ERROR - {str(e)}")
        all_revenue = 0
        all_quantity = 0
        locations_aggregated = False
        location_count = 0
    
    # Analysis
    print("\\n📊 Analysis:")
    
    # Calculate sum of individual locations
    individual_revenues = [r['revenue'] for r in individual_results.values() if r['revenue'] > 0]
    individual_quantities = [r['quantity'] for r in individual_results.values() if r['quantity'] > 0]
    
    if individual_revenues:
        total_individual_revenue = sum(individual_revenues)
        total_individual_quantity = sum(individual_quantities)
        
        print(f"• Individual locations working: {len(individual_revenues)}/{len(individual_locations)}")
        print(f"• Sum of individual revenues: ${total_individual_revenue:,.2f}")
        print(f"• Sum of individual quantities: {total_individual_quantity:.1f}")
        print(f"• 'All' location revenue: ${all_revenue:,.2f}")
        print(f"• 'All' location quantity: {all_quantity:.1f}")
        
        # Check if aggregation is working
        revenue_ratio = all_revenue / total_individual_revenue if total_individual_revenue > 0 else 0
        quantity_ratio = all_quantity / total_individual_quantity if total_individual_quantity > 0 else 0
        
        print(f"• Revenue ratio (All/Sum): {revenue_ratio:.2f}")
        print(f"• Quantity ratio (All/Sum): {quantity_ratio:.2f}")
        
        if locations_aggregated:
            if 0.9 <= revenue_ratio <= 1.1:
                print("✅ GOOD: 'All' properly aggregates individual location revenues")
            else:
                print("❌ PROBLEM: 'All' doesn't properly aggregate revenues")
        else:
            print("❌ PROBLEM: 'All' location not using aggregation (using fallback location)")
            
        # Check for identical values across locations
        unique_individual_revenues = set(individual_revenues)
        if len(unique_individual_revenues) == 1:
            print("❌ PROBLEM: All individual locations return identical revenue!")
            print(f"   All locations return: ${individual_revenues[0]:,.2f}")
        else:
            print("✅ GOOD: Individual locations return different revenues")
    
    else:
        print("❌ ERROR: No successful individual location predictions")

if __name__ == "__main__":
    test_all_location_handling() 