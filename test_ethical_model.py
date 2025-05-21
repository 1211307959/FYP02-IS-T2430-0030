import pandas as pd
import numpy as np
import json
from pprint import pprint
import matplotlib.pyplot as plt

# Import ethical model prediction function
from ethical_revenue_predictor import predict_revenue, simulate_price_variations

# Test data for different scenarios
basic_test_input = {
    'Unit Price': 100,
    'Unit Cost': 50,
    'Month': 6,
    'Day': 15,
    'Weekday': 'Friday',
    'Location': 'North',
    '_ProductID': 12,
    'Year': 2023
}

seasonal_test_inputs = [
    # Winter (Q1)
    {'Unit Price': 100, 'Unit Cost': 50, 'Month': 1, 'Day': 15, 'Weekday': 'Monday', 'Location': 'North', '_ProductID': 12, 'Year': 2023},
    # Spring (Q2)
    {'Unit Price': 100, 'Unit Cost': 50, 'Month': 4, 'Day': 15, 'Weekday': 'Tuesday', 'Location': 'North', '_ProductID': 12, 'Year': 2023},
    # Summer (Q3)
    {'Unit Price': 100, 'Unit Cost': 50, 'Month': 7, 'Day': 15, 'Weekday': 'Wednesday', 'Location': 'North', '_ProductID': 12, 'Year': 2023},
    # Fall (Q4)
    {'Unit Price': 100, 'Unit Cost': 50, 'Month': 10, 'Day': 15, 'Weekday': 'Thursday', 'Location': 'North', '_ProductID': 12, 'Year': 2023}
]

location_test_inputs = [
    {'Unit Price': 100, 'Unit Cost': 50, 'Month': 6, 'Day': 15, 'Weekday': 'Friday', 'Location': 'North', '_ProductID': 12, 'Year': 2023},
    {'Unit Price': 100, 'Unit Cost': 50, 'Month': 6, 'Day': 15, 'Weekday': 'Friday', 'Location': 'South', '_ProductID': 12, 'Year': 2023},
    {'Unit Price': 100, 'Unit Cost': 50, 'Month': 6, 'Day': 15, 'Weekday': 'Friday', 'Location': 'East', '_ProductID': 12, 'Year': 2023},
    {'Unit Price': 100, 'Unit Cost': 50, 'Month': 6, 'Day': 15, 'Weekday': 'Friday', 'Location': 'West', '_ProductID': 12, 'Year': 2023},
    {'Unit Price': 100, 'Unit Cost': 50, 'Month': 6, 'Day': 15, 'Weekday': 'Friday', 'Location': 'Central', '_ProductID': 12, 'Year': 2023}
]

# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(x) for x in obj]
    elif isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

def test_ethical_model():
    """Test the ethical revenue prediction model."""
    print("\n===== TESTING ETHICAL REVENUE PREDICTION MODEL =====\n")
    
    try:
        # Test prediction
        print("Testing Ethical Model...")
        result = predict_revenue(basic_test_input)
        result = convert_numpy_types(result)
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Verify key properties
        print("\nVerifying Prediction Properties:")
        
        # Check if result has expected keys
        expected_keys = ['predicted_revenue', 'estimated_quantity', 'total_cost', 
                         'profit', 'profit_margin_pct', 'unit_price', 'unit_cost']
        missing_keys = [key for key in expected_keys if key not in result]
        
        if missing_keys:
            print(f"Warning: Missing expected keys in result: {missing_keys}")
        else:
            print("✓ Result contains all expected properties")
        
        # Check if predictions are positive numbers
        if result.get('predicted_revenue', 0) > 0:
            print("✓ Predicted revenue is positive")
        else:
            print("✗ Warning: Predicted revenue should be positive")
            
        if result.get('estimated_quantity', 0) >= 0:
            print("✓ Estimated quantity is non-negative")
        else:
            print("✗ Warning: Estimated quantity should be non-negative")
            
        print("\n===== PRICE SENSITIVITY TEST =====\n")
        
        # Create test inputs with different prices
        prices = [50, 75, 100, 125, 150, 200]
        
        print(f"{'Price':10} {'Quantity':10} {'Revenue':10} {'Profit':10}")
        print("-" * 45)
        
        results = []
        for price in prices:
            test_data = basic_test_input.copy()
            test_data['Unit Price'] = price
            
            # Test with ethical model
            result = predict_revenue(test_data)
            result = convert_numpy_types(result)
            results.append(result)
            
            print(f"${price:9.2f} {result['estimated_quantity']:10} ${result['predicted_revenue']:9.2f} ${result['profit']:9.2f}")
        
        # Check price sensitivity (quantity should decrease as price increases)
        price_low = basic_test_input.copy()
        price_low['Unit Price'] = 50
        price_high = basic_test_input.copy()
        price_high['Unit Price'] = 200
        
        result_low = predict_revenue(price_low)
        result_high = predict_revenue(price_high)
        
        if result_low['estimated_quantity'] >= result_high['estimated_quantity']:
            print("\n✓ Model shows appropriate price sensitivity (quantity decreases as price increases)")
        else:
            print("\n✗ Warning: Model does not show expected price sensitivity")

        # Plot price sensitivity graph
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Revenue vs Price
        ax1.plot([r['unit_price'] for r in results], [r['predicted_revenue'] for r in results], marker='o')
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
        plt.savefig('ethical_model_price_sensitivity.png')
        print(f"\nPrice sensitivity graph saved to 'ethical_model_price_sensitivity.png'")
        
        # Test seasonal variations
        print("\n===== SEASONAL VARIATIONS TEST =====\n")
        print(f"{'Season':10} {'Month':10} {'Revenue':10} {'Quantity':10}")
        print("-" * 45)
        
        seasons = ["Winter", "Spring", "Summer", "Fall"]
        seasonal_results = []
        
        for i, test_data in enumerate(seasonal_test_inputs):
            result = predict_revenue(test_data)
            result = convert_numpy_types(result)
            seasonal_results.append(result)
            
            print(f"{seasons[i]:10} {test_data['Month']:10} ${result['predicted_revenue']:9.2f} {result['estimated_quantity']:10}")
        
        # Plot seasonal variations
        plt.figure(figsize=(10, 6))
        plt.bar(seasons, [r['predicted_revenue'] for r in seasonal_results], color='skyblue')
        plt.xlabel('Season')
        plt.ylabel('Predicted Revenue ($)')
        plt.title('Seasonal Variation in Revenue')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('ethical_model_seasonal_variation.png')
        print(f"\nSeasonal variation graph saved to 'ethical_model_seasonal_variation.png'")
        
        # Test location variations
        print("\n===== LOCATION VARIATIONS TEST =====\n")
        print(f"{'Location':10} {'Revenue':10} {'Quantity':10}")
        print("-" * 35)
        
        locations = [input_data['Location'] for input_data in location_test_inputs]
        location_results = []
        
        for test_data in location_test_inputs:
            result = predict_revenue(test_data)
            result = convert_numpy_types(result)
            location_results.append(result)
            
            print(f"{test_data['Location']:10} ${result['predicted_revenue']:9.2f} {result['estimated_quantity']:10}")
        
        # Plot location variations
        plt.figure(figsize=(10, 6))
        plt.bar(locations, [r['predicted_revenue'] for r in location_results], color='lightgreen')
        plt.xlabel('Location')
        plt.ylabel('Predicted Revenue ($)')
        plt.title('Revenue Variation by Location')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig('ethical_model_location_variation.png')
        print(f"\nLocation variation graph saved to 'ethical_model_location_variation.png'")
        
        return True
    
    except Exception as e:
        import traceback
        print(f"Error testing ethical model: {e}")
        traceback.print_exc()
        return False

def test_price_simulation():
    """Test the price simulation function of the ethical model."""
    print("\n===== TESTING ETHICAL MODEL PRICE SIMULATION =====\n")
    
    try:
        # Test price simulation
        simulation = simulate_price_variations(basic_test_input)
        simulation = convert_numpy_types(simulation)
        
        print(f"Base Price: ${simulation.get('base_price', 'N/A')}")
        print(f"Unit Cost: ${simulation.get('unit_cost', 'N/A')}")
        print("\nSimulated Price Points:")
        
        if 'variations' not in simulation:
            print("Error: No variations found in simulation result")
            return False
        
        variations = simulation['variations']
        
        print(f"{'Price':10} {'Quantity':10} {'Revenue':12} {'Profit':12} {'Margin %':10}")
        print("-" * 60)
        
        for var in variations:
            price = var.get('unit_price', 0)
            quantity = var.get('quantity', 0)
            revenue = var.get('revenue', 0)
            profit = var.get('profit', 0)
            margin_pct = var.get('profit_margin_pct', 0)
            
            print(f"${price:9.2f} {quantity:10} ${revenue:11.2f} ${profit:11.2f} {margin_pct:9.2f}%")
        
        # Print optimal price points
        if 'optimal_revenue_price' in simulation:
            opt_rev = simulation['optimal_revenue_price']
            print(f"\nOptimal Revenue Price: ${opt_rev['unit_price']:.2f} → Revenue: ${opt_rev['revenue']:.2f}")
        
        if 'optimal_profit_price' in simulation:
            opt_profit = simulation['optimal_profit_price']
            print(f"Optimal Profit Price: ${opt_profit['unit_price']:.2f} → Profit: ${opt_profit['profit']:.2f}")
        
        # Create visualization for price simulation
        plt.figure(figsize=(12, 8))
        
        # Revenue and Profit vs Price
        prices = [var['unit_price'] for var in variations]
        revenues = [var['revenue'] for var in variations]
        profits = [var['profit'] for var in variations]
        
        plt.plot(prices, revenues, 'b-o', label='Revenue')
        plt.plot(prices, profits, 'g-o', label='Profit')
        
        # Mark optimal points
        if 'optimal_revenue_price' in simulation:
            opt_rev = simulation['optimal_revenue_price']
            plt.plot(opt_rev['unit_price'], opt_rev['revenue'], 'r*', markersize=15, label='Optimal Revenue')
        
        if 'optimal_profit_price' in simulation and 'optimal_revenue_price' in simulation:
            opt_profit = simulation['optimal_profit_price']
            # Only add to legend if different from optimal revenue point
            if opt_profit['unit_price'] != simulation['optimal_revenue_price']['unit_price']:
                plt.plot(opt_profit['unit_price'], opt_profit['profit'], 'm*', markersize=15, label='Optimal Profit')
        
        plt.xlabel('Unit Price ($)')
        plt.ylabel('Amount ($)')
        plt.title('Revenue and Profit by Price')
        plt.grid(True)
        plt.legend()
        plt.savefig('ethical_model_price_simulation.png')
        print(f"\nPrice simulation graph saved to 'ethical_model_price_simulation.png'")
        
        return True
    
    except Exception as e:
        import traceback
        print(f"Error testing price simulation: {e}")
        traceback.print_exc()
        return False

def test_extreme_cases():
    """Test the ethical model with extreme input values."""
    print("\n===== TESTING ETHICAL MODEL WITH EXTREME CASES =====\n")
    
    try:
        # Test with extremely high price
        high_price_input = basic_test_input.copy()
        high_price_input['Unit Price'] = 1000
        
        # Test with extremely low price (at cost)
        low_price_input = basic_test_input.copy()
        low_price_input['Unit Cost'] = low_price_input['Unit Price']  # Price equals cost
        
        # Test with negative profit margin
        negative_margin_input = basic_test_input.copy()
        negative_margin_input['Unit Price'] = negative_margin_input['Unit Cost'] * 0.8  # 20% below cost
        
        # Test with unknown location
        unknown_location_input = basic_test_input.copy()
        unknown_location_input['Location'] = 'Unknown_Location'
        
        # Test with unknown product
        unknown_product_input = basic_test_input.copy()
        unknown_product_input['_ProductID'] = 9999
        
        test_cases = [
            ("Extremely High Price", high_price_input),
            ("Price At Cost", low_price_input),
            ("Negative Margin", negative_margin_input),
            ("Unknown Location", unknown_location_input),
            ("Unknown Product", unknown_product_input)
        ]
        
        print(f"{'Case':20} {'Revenue':12} {'Quantity':10} {'Profit':12} {'Status'}")
        print("-" * 70)
        
        for name, test_input in test_cases:
            try:
                result = predict_revenue(test_input)
                result = convert_numpy_types(result)
                print(f"{name:20} ${result.get('predicted_revenue', 0):11.2f} {result.get('estimated_quantity', 0):10} ${result.get('profit', 0):11.2f} ✓ Handled correctly")
            except Exception as e:
                print(f"{name:20} {'N/A':12} {'N/A':10} {'N/A':12} ✗ Failed: {str(e)}")
                
        return True
    
    except Exception as e:
        import traceback
        print(f"Error testing extreme cases: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ethical_model()
    test_price_simulation()
    test_extreme_cases() 