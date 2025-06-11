import json
from revenue_predictor_50_50 import predict_revenue, simulate_price_variations, optimize_price

def test_model():
    # Example input
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
    print("Testing revenue prediction...")
    result = predict_revenue(test_data)
    
    # Format and print result
    print(json.dumps(result, indent=2))
    
    # Test price simulation
    print("\nTesting price simulation...")
    variations = simulate_price_variations(test_data)
    
    # Print price simulation results
    print(f"{'Price':<10} {'Quantity':<10} {'Revenue':<15} {'Profit':<15}")
    print(f"{'-'*50}")
    for v in variations:
        print(f"${v['unit_price']:<9.2f} {v['quantity']:<10} ${v['revenue']:<14.2f} ${v['profit']:<14.2f}")
    
    # Test optimization
    print("\nTesting price optimization...")
    
    # Optimize for revenue
    rev_opt = optimize_price(test_data, metric="revenue")
    print(f"Optimal price for revenue: ${rev_opt['unit_price']:.2f}")
    print(f"Expected revenue: ${rev_opt['revenue']:.2f}")
    
    # Optimize for profit
    profit_opt = optimize_price(test_data, metric="profit")
    print(f"Optimal price for profit: ${profit_opt['unit_price']:.2f}")
    print(f"Expected profit: ${profit_opt['profit']:.2f}")
    
    print("\nModel testing complete!")

if __name__ == "__main__":
    test_model() 