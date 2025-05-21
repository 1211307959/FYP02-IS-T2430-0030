import json
from revenue_predictor_50_50 import predict_revenue, simulate_price_variations, optimize_price

def verify_model():
    """Simple verification test for the 50/50 split model that can be used in your application.
    Returns True if the model is working properly, False otherwise.
    """
    print("Running model verification test...")
    
    try:
        # Test basic prediction
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
        
        # Basic prediction
        result = predict_revenue(test_data)
        
        # Verify result structure
        required_keys = ['predicted_revenue', 'estimated_quantity', 'total_cost', 
                         'profit', 'profit_margin_pct', 'unit_price', 'unit_cost']
        
        for key in required_keys:
            if key not in result:
                print(f"❌ Missing required key in prediction: {key}")
                return False
                
        # Verify price sensitivity
        low_price_test = test_data.copy()
        low_price_test['Unit Price'] = 50
        high_price_test = test_data.copy()
        high_price_test['Unit Price'] = 200
        
        low_result = predict_revenue(low_price_test)
        high_result = predict_revenue(high_price_test)
        
        if not (low_result['estimated_quantity'] > high_result['estimated_quantity']):
            print("❌ Model does not show proper price sensitivity")
            return False
            
        # Test price simulation
        sim_results = simulate_price_variations(test_data, steps=5)
        
        if len(sim_results) != 5:
            print(f"❌ Price simulation returned {len(sim_results)} results, expected 5")
            return False
            
        # Test optimization
        revenue_opt = optimize_price(test_data, metric="revenue", steps=10)
        profit_opt = optimize_price(test_data, metric="profit", steps=10)
        
        if not (revenue_opt and 'unit_price' in revenue_opt and 'revenue' in revenue_opt):
            print("❌ Revenue optimization failed")
            return False
            
        if not (profit_opt and 'unit_price' in profit_opt and 'profit' in profit_opt):
            print("❌ Profit optimization failed")
            return False
        
        print("✅ Model verification completed successfully!")
        print(f"Sample prediction for $100 product: ${result['predicted_revenue']:.2f} revenue")
        print(f"Optimal price for revenue: ${revenue_opt['unit_price']:.2f}")
        print(f"Optimal price for profit: ${profit_opt['unit_price']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model verification failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def sample_prediction():
    """Make a sample prediction with the 50/50 model and return the formatted result.
    Use this to test a specific scenario in your application.
    """
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
    
    # Return formatted result
    return {
        'status': 'success',
        'test_input': test_data,
        'prediction': result
    }

def sample_price_simulation():
    """Run a sample price simulation with the 50/50 model.
    Use this to test the price simulation functionality in your application.
    """
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
    
    # Simulate prices
    variations = simulate_price_variations(
        test_data,
        min_price_factor=0.5,
        max_price_factor=2.0,
        steps=7
    )
    
    # Return formatted result
    return {
        'status': 'success',
        'test_input': test_data,
        'price_variations': variations
    }

def sample_price_optimization():
    """Run a sample price optimization with the 50/50 model.
    Use this to test the price optimization functionality in your application.
    """
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
    
    # Optimize for both revenue and profit
    revenue_opt = optimize_price(test_data, metric="revenue")
    profit_opt = optimize_price(test_data, metric="profit")
    
    # Return formatted result
    return {
        'status': 'success',
        'test_input': test_data,
        'revenue_optimization': revenue_opt,
        'profit_optimization': profit_opt
    }

if __name__ == "__main__":
    # Run the verification test
    model_ok = verify_model()
    
    if model_ok:
        print("\n=== Sample Prediction ===")
        prediction_result = sample_prediction()
        print(json.dumps(prediction_result['prediction'], indent=2))
        
        print("\n=== Sample Price Optimization ===")
        optimization_result = sample_price_optimization()
        print(f"Revenue-optimal price: ${optimization_result['revenue_optimization']['unit_price']:.2f}")
        print(f"Profit-optimal price: ${optimization_result['profit_optimization']['unit_price']:.2f}")
    else:
        print("\n⚠️ Model verification failed. Please check the model and try again.") 