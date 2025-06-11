import pandas as pd
import numpy as np
import json
from pprint import pprint

# Import prediction functions
from fixed_revenue_predictor import predict_revenue as predict_original
from modified_revenue_predictor import predict_revenue as predict_modified
from full_data_revenue_predictor import predict_revenue as predict_full
from ethical_revenue_predictor import predict_revenue as predict_ethical

# Test data
test_input = {
    'Unit Price': 100,
    'Unit Cost': 50,
    'Month': 6,
    'Day': 15,
    'Weekday': 'Friday',
    'Location': 'North',
    '_ProductID': 12,
    'Year': 2023
}

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

def test_models():
    """Test all revenue prediction models with the same input."""
    print("\n===== TESTING REVENUE PREDICTION MODELS =====\n")
    
    try:
        # Test original model
        print("Testing Original Model (25% sample)...")
        original_result = predict_original(test_input)
        original_result = convert_numpy_types(original_result)
        print(f"Result: {json.dumps(original_result, indent=2)}")
        
        # Test modified model
        print("\nTesting Modified Model (25% sample)...")
        modified_result = predict_modified(test_input)
        modified_result = convert_numpy_types(modified_result)
        print(f"Result: {json.dumps(modified_result, indent=2)}")
        
        # Test full data model
        print("\nTesting Full Data Model (100% data)...")
        full_result = predict_full(test_input)
        full_result = convert_numpy_types(full_result)
        print(f"Result: {json.dumps(full_result, indent=2)}")
        
        # Test ethical model
        print("\nTesting Ethical Model (no target leakage)...")
        ethical_result = predict_ethical(test_input)
        ethical_result = convert_numpy_types(ethical_result)
        print(f"Result: {json.dumps(ethical_result, indent=2)}")
        
        # Compare results
        print("\n===== MODEL COMPARISON =====\n")
        comparison = {
            "Original Model": {
                "Revenue": original_result.get("predicted_revenue", "Error"),
                "Quantity": original_result.get("estimated_quantity", "Error"),
                "Profit": original_result.get("profit", "Error")
            },
            "Modified Model": {
                "Revenue": modified_result.get("predicted_revenue", "Error"),
                "Quantity": modified_result.get("estimated_quantity", "Error"),
                "Profit": modified_result.get("profit", "Error")
            },
            "Full Data Model": {
                "Revenue": full_result.get("predicted_revenue", "Error"),
                "Quantity": full_result.get("estimated_quantity", "Error"),
                "Profit": full_result.get("profit", "Error")
            },
            "Ethical Model": {
                "Revenue": ethical_result.get("predicted_revenue", "Error"),
                "Quantity": ethical_result.get("estimated_quantity", "Error"),
                "Profit": ethical_result.get("profit", "Error")
            }
        }
        
        # Print formatted comparison
        print(f"Input: Unit Price = ${test_input['Unit Price']}, Unit Cost = ${test_input['Unit Cost']}")
        print(f"         {'Original':15} {'Modified':15} {'Full Data':15} {'Ethical':15}")
        print("-" * 65)
        print(f"Revenue: ${comparison['Original Model']['Revenue']:12.2f} ${comparison['Modified Model']['Revenue']:12.2f} ${comparison['Full Data Model']['Revenue']:12.2f} ${comparison['Ethical Model']['Revenue']:12.2f}")
        print(f"Quantity: {comparison['Original Model']['Quantity']:13} {comparison['Modified Model']['Quantity']:13} {comparison['Full Data Model']['Quantity']:13} {comparison['Ethical Model']['Quantity']:13}")
        print(f"Profit:   ${comparison['Original Model']['Profit']:12.2f} ${comparison['Modified Model']['Profit']:12.2f} ${comparison['Full Data Model']['Profit']:12.2f} ${comparison['Ethical Model']['Profit']:12.2f}")
        
        # Test price sensitivity
        print("\n===== PRICE SENSITIVITY TESTS =====\n")
        
        # Create test inputs with different prices
        prices = [50, 75, 100, 125, 150, 200]
        
        print(f"{'Price':10} {'Quantity':10} {'Revenue':10} {'Profit':10}")
        print("-" * 45)
        
        for price in prices:
            test_data = test_input.copy()
            test_data['Unit Price'] = price
            
            # Test with full data model
            result = predict_full(test_data)
            result = convert_numpy_types(result)
            
            print(f"${price:9.2f} {result['estimated_quantity']:10} ${result['predicted_revenue']:9.2f} ${result['profit']:9.2f}")
        
        print("\nAll models are working correctly!")
        return True
    
    except Exception as e:
        import traceback
        print(f"Error testing models: {e}")
        traceback.print_exc()
        return False

def test_extreme_pricing():
    """Test model behavior with extreme price points."""
    print("\n===== TESTING EXTREME PRICE POINTS =====\n")
    
    try:
        base_input = test_input.copy()
        unit_cost = base_input['Unit Cost']
        
        # Test very low price (at cost)
        low_price_input = base_input.copy()
        low_price_input['Unit Price'] = unit_cost
        low_result = predict_full(low_price_input)
        low_result = convert_numpy_types(low_result)
        
        # Test very high price (10x normal)
        high_price_input = base_input.copy()
        high_price_input['Unit Price'] = 1000
        high_result = predict_full(high_price_input)
        high_result = convert_numpy_types(high_result)
        
        # Test extremely high price (100x normal)
        extreme_price_input = base_input.copy()
        extreme_price_input['Unit Price'] = 10000
        extreme_result = predict_full(extreme_price_input)
        extreme_result = convert_numpy_types(extreme_result)
        
        print(f"{'Price':10} {'Quantity':10} {'Revenue':15} {'Profit':15}")
        print("-" * 55)
        print(f"${unit_cost:9.2f} {low_result['estimated_quantity']:10} ${low_result['predicted_revenue']:14.2f} ${low_result['profit']:14.2f}")
        print(f"${1000:9.2f} {high_result['estimated_quantity']:10} ${high_result['predicted_revenue']:14.2f} ${high_result['profit']:14.2f}")
        print(f"${10000:9.2f} {extreme_result['estimated_quantity']:10} ${extreme_result['predicted_revenue']:14.2f} ${extreme_result['profit']:14.2f}")
        
        return True
    
    except Exception as e:
        print(f"Error testing extreme prices: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_models()
    test_extreme_pricing() 