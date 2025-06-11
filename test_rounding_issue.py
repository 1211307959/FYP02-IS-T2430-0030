#!/usr/bin/env python3
"""
Test script to demonstrate the rounding issue causing identical results
"""

import numpy as np

def test_rounding_issue():
    """Test how rounding affects the ML predictions"""
    print("🔍 Testing Rounding Issue")
    print("=" * 40)
    
    # Raw ML predictions (log scale)
    predictions = [9.218286, 9.222939, 9.235399]
    
    print("1. Raw ML Predictions (log scale):")
    for i, pred in enumerate(predictions):
        print(f"   Case {i+1}: {pred:.6f}")
    
    print("\n2. After inverse log transformation:")
    revenues = [np.expm1(p) for p in predictions]
    for i, rev in enumerate(revenues):
        print(f"   Case {i+1}: ${rev:.2f}")
    
    print("\n3. Convert to quantities (revenue / $5000):")
    quantities = [r / 5000 for r in revenues]
    for i, qty in enumerate(quantities):
        print(f"   Case {i+1}: {qty:.4f}")
    
    print("\n4. After rounding (the problem!):")
    rounded_quantities = [round(q) for q in quantities]
    for i, qty in enumerate(rounded_quantities):
        print(f"   Case {i+1}: {qty}")
    
    print("\n5. Final revenues (rounded_qty * $5000):")
    final_revenues = [q * 5000 for q in rounded_quantities]
    for i, rev in enumerate(final_revenues):
        print(f"   Case {i+1}: ${rev:.2f}")
    
    print("\n📊 Analysis:")
    print(f"• ML model predictions vary: {len(set(predictions))} unique")
    print(f"• Raw revenues vary: {len(set([round(r) for r in revenues]))} unique")
    print(f"• Raw quantities vary: {len(set([round(q, 4) for q in quantities]))} unique")
    print(f"• Rounded quantities: {len(set(rounded_quantities))} unique")
    print(f"• Final revenues: {len(set(final_revenues))} unique")
    
    print("\n🎯 The Issue:")
    print("Raw quantities all round to 2.0, making final revenues identical!")
    
    print("\n✅ Potential Solutions:")
    print("1. Use more precise rounding (e.g., to 1 decimal place)")
    print("2. Scale the differences before rounding")
    print("3. Use direct revenue prediction without quantity conversion")

if __name__ == "__main__":
    test_rounding_issue() 