#!/usr/bin/env python3

from revenue_predictor_time_enhanced_ethical import simulate_annual_revenue

def test_scenario_exact():
    """Test exact scenario planner conditions"""
    
    print("Testing exact scenario planner conditions...")
    
    # Test with low base price (exactly like scenario planner)
    test_low = {
        '_ProductID': 2,
        'Location': 'All',  # All Locations like in scenario planner
        'Unit Price': 5051.98,
        'Unit Cost': 2100,
        'Month': 6,
        'Day': 15,
        'Year': 2024,
        'Weekday': 'Saturday'
    }
    
    # Test with high base price
    test_high = {
        '_ProductID': 2,
        'Location': 'All',  # All Locations like in scenario planner
        'Unit Price': 15051.98,  # 3x higher
        'Unit Cost': 2100,
        'Month': 6,
        'Day': 15,
        'Year': 2024,
        'Weekday': 'Saturday'
    }
    
    print(f"\\n1. Low base price test (${test_low['Unit Price']:,.2f}):")
    results_low = simulate_annual_revenue(test_low, min_price_factor=0.5, max_price_factor=2.0, steps=5)
    
    if results_low:
        for r in results_low:
            print(f"  {r['name']}: Price ${r['unit_price']:,.0f}, Qty {r['predicted_quantity']}, Rev ${r['predicted_revenue']:,.0f}")
        
        # Find the 50% lower scenario
        fifty_lower = [r for r in results_low if '50%' in r['name'] and 'Lower' in r['name']]
        if fifty_lower:
            print(f"\\n  >>> 50% Lower scenario: Qty = {fifty_lower[0]['predicted_quantity']}")
    
    print(f"\\n2. High base price test (${test_high['Unit Price']:,.2f}):")
    results_high = simulate_annual_revenue(test_high, min_price_factor=0.5, max_price_factor=2.0, steps=5)
    
    if results_high:
        for r in results_high:
            print(f"  {r['name']}: Price ${r['unit_price']:,.0f}, Qty {r['predicted_quantity']}, Rev ${r['predicted_revenue']:,.0f}")
        
        # Find the 50% lower scenario
        fifty_lower = [r for r in results_high if '50%' in r['name'] and 'Lower' in r['name']]
        if fifty_lower:
            print(f"\\n  >>> 50% Lower scenario: Qty = {fifty_lower[0]['predicted_quantity']}")
    
    print("\\n3. Comparison:")
    if results_low and results_high:
        low_50 = [r for r in results_low if '50%' in r['name'] and 'Lower' in r['name']]
        high_50 = [r for r in results_high if '50%' in r['name'] and 'Lower' in r['name']]
        
        if low_50 and high_50:
            print(f"  Low base 50% scenario:  ${low_50[0]['unit_price']:,.0f} → Qty {low_50[0]['predicted_quantity']}")
            print(f"  High base 50% scenario: ${high_50[0]['unit_price']:,.0f} → Qty {high_50[0]['predicted_quantity']}")
            
            if low_50[0]['predicted_quantity'] == high_50[0]['predicted_quantity']:
                print("  ❌ PROBLEM: Same quantity despite different prices!")
                print(f"     Low base effective price: ${low_50[0]['unit_price']:,.0f}")
                print(f"     High base effective price: ${high_50[0]['unit_price']:,.0f}")
                print(f"     Price difference: {high_50[0]['unit_price'] / low_50[0]['unit_price']:.1f}x")
            else:
                print(f"  ✅ OK: Different quantities ({low_50[0]['predicted_quantity']} vs {high_50[0]['predicted_quantity']})")

if __name__ == "__main__":
    test_scenario_exact() 