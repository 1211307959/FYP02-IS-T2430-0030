import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# API base URL
API_URL = "http://localhost:5000"

def test_health():
    """Test if the API is running properly"""
    response = requests.get(f"{API_URL}/health")
    print(f"Health check status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_model_info():
    """Get information about the model"""
    response = requests.get(f"{API_URL}/model-info")
    print(f"Model info status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def predict_revenue(input_data):
    """Make a revenue prediction using the enhanced ethical model"""
    response = requests.post(f"{API_URL}/predict-revenue", json=input_data)
    return response.json()

def simulate_revenue(input_data, min_factor=0.5, max_factor=2.0, steps=10):
    """Simulate revenue at different price points"""
    # Add simulation parameters
    data = input_data.copy()
    data["min_price_factor"] = min_factor
    data["max_price_factor"] = max_factor
    data["steps"] = steps
    
    response = requests.post(f"{API_URL}/simulate-revenue", json=data)
    return response.json()

def optimize_price(input_data, metric="profit"):
    """Find optimal price for revenue or profit maximization"""
    # Add optimization parameters
    data = input_data.copy()
    data["metric"] = metric
    data["steps"] = 20
    
    response = requests.post(f"{API_URL}/optimize-price", json=data)
    return response.json()

def test_basic_prediction():
    """Test basic prediction functionality"""
    print("=== Testing Basic Prediction ===")
    
    # Sample input
    input_data = {
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
    result = predict_revenue(input_data)
    print(f"Prediction result: {json.dumps(result, indent=2)}")
    print()
    
    # Calculate profit margin
    if "predicted_revenue" in result and "profit" in result:
        profit_margin = (result["profit"] / result["predicted_revenue"]) * 100
        print(f"Profit margin: {profit_margin:.2f}%")
    print()

def test_price_sensitivity():
    """Test if the model correctly shows price sensitivity"""
    print("=== Testing Price Sensitivity ===")
    
    # Base product
    base_product = {
        'Unit Cost': 50,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': 12,
        'Year': 2023
    }
    
    # Test different price points
    price_points = [50, 75, 100, 125, 150, 200, 300, 500]
    results = []
    
    for price in price_points:
        input_data = base_product.copy()
        input_data['Unit Price'] = price
        
        result = predict_revenue(input_data)
        if "error" not in result:
            results.append({
                "price": price,
                "revenue": result.get("predicted_revenue", 0),
                "quantity": result.get("estimated_quantity", 0),
                "profit": result.get("profit", 0)
            })
    
    # Create DataFrame for better display
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    print()
    
    # Plot price sensitivity
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 3, 1)
    plt.plot(df["price"], df["quantity"], marker='o', linestyle='-')
    plt.title("Price vs Quantity")
    plt.xlabel("Price")
    plt.ylabel("Estimated Quantity")
    plt.grid(True)
    
    plt.subplot(1, 3, 2)
    plt.plot(df["price"], df["revenue"], marker='o', linestyle='-')
    plt.title("Price vs Revenue")
    plt.xlabel("Price")
    plt.ylabel("Predicted Revenue")
    plt.grid(True)
    
    plt.subplot(1, 3, 3)
    plt.plot(df["price"], df["profit"], marker='o', linestyle='-')
    plt.title("Price vs Profit")
    plt.xlabel("Price")
    plt.ylabel("Profit")
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("price_sensitivity.png")
    print("Price sensitivity plot saved to price_sensitivity.png")
    print()

def test_product_variations():
    """Test the model with different products"""
    print("=== Testing Product Variations ===")
    
    # Base configuration
    base_input = {
        'Unit Price': 100,
        'Unit Cost': 50,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        'Year': 2023
    }
    
    # Test different products
    product_ids = [1, 5, 10, 15, 20, 25, 30]
    results = []
    
    for product_id in product_ids:
        input_data = base_input.copy()
        input_data['_ProductID'] = product_id
        
        result = predict_revenue(input_data)
        if "error" not in result:
            results.append({
                "product_id": product_id,
                "revenue": result.get("predicted_revenue", 0),
                "quantity": result.get("estimated_quantity", 0)
            })
    
    # Create DataFrame for better display
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    print()

def test_seasonal_variations():
    """Test the model's seasonal awareness"""
    print("=== Testing Seasonal Variations ===")
    
    # Base configuration
    base_input = {
        'Unit Price': 100,
        'Unit Cost': 50,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': 12,
        'Year': 2023
    }
    
    # Test all months
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    results = []
    
    for month_num, month_name in enumerate(month_names, 1):
        input_data = base_input.copy()
        input_data['Month'] = month_num
        
        result = predict_revenue(input_data)
        if "error" not in result:
            results.append({
                "month": month_name,
                "revenue": result.get("predicted_revenue", 0),
                "quantity": result.get("estimated_quantity", 0)
            })
    
    # Create DataFrame for better display
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    print()
    
    # Plot seasonal variation
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.bar(df["month"], df["revenue"])
    plt.title("Seasonal Revenue Variation")
    plt.xlabel("Month")
    plt.ylabel("Predicted Revenue")
    plt.xticks(rotation=45)
    plt.grid(True, axis='y')
    
    plt.subplot(1, 2, 2)
    plt.bar(df["month"], df["quantity"])
    plt.title("Seasonal Quantity Variation")
    plt.xlabel("Month")
    plt.ylabel("Estimated Quantity")
    plt.xticks(rotation=45)
    plt.grid(True, axis='y')
    
    plt.tight_layout()
    plt.savefig("seasonal_variation.png")
    print("Seasonal variation plot saved to seasonal_variation.png")
    print()

def test_price_simulation():
    """Test the price simulation functionality"""
    print("=== Testing Price Simulation ===")
    
    # Sample input
    input_data = {
        'Unit Price': 100,
        'Unit Cost': 50,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': 12,
        'Year': 2023
    }
    
    # Run simulation
    result = simulate_revenue(input_data, min_factor=0.5, max_factor=2.0, steps=10)
    
    if "error" in result:
        print(f"Simulation error: {result['error']}")
    else:
        # Print simulation results
        print(f"Base Price: ${result.get('base_price', 0)}")
        print(f"Unit Cost: ${result.get('unit_cost', 0)}")
        
        # Extract optimal prices
        optimal_revenue = result.get('optimal_revenue_price', {})
        optimal_profit = result.get('optimal_profit_price', {})
        
        print(f"\nOptimal Revenue Price: ${optimal_revenue.get('unit_price', 0)}")
        print(f"Revenue at Optimal: ${optimal_revenue.get('revenue', 0)}")
        print(f"Quantity at Optimal: {optimal_revenue.get('quantity', 0)}")
        
        print(f"\nOptimal Profit Price: ${optimal_profit.get('unit_price', 0)}")
        print(f"Profit at Optimal: ${optimal_profit.get('profit', 0)}")
        print(f"Quantity at Optimal: {optimal_profit.get('quantity', 0)}")
        
        # Print all variations
        variations = result.get('variations', [])
        if variations:
            print("\nAll price variations:")
            df = pd.DataFrame(variations)
            print(df.to_string(index=False))
            
            # Plot variations
            plt.figure(figsize=(12, 6))
            
            plt.subplot(1, 2, 1)
            plt.plot(df["unit_price"], df["revenue"], marker='o', linestyle='-')
            plt.axvline(x=optimal_revenue.get('unit_price', 0), color='r', linestyle='--', 
                       label=f"Optimal: ${optimal_revenue.get('unit_price', 0)}")
            plt.title("Price vs Revenue")
            plt.xlabel("Unit Price")
            plt.ylabel("Revenue")
            plt.legend()
            plt.grid(True)
            
            plt.subplot(1, 2, 2)
            plt.plot(df["unit_price"], df["profit"], marker='o', linestyle='-')
            plt.axvline(x=optimal_profit.get('unit_price', 0), color='r', linestyle='--',
                       label=f"Optimal: ${optimal_profit.get('unit_price', 0)}")
            plt.title("Price vs Profit")
            plt.xlabel("Unit Price")
            plt.ylabel("Profit")
            plt.legend()
            plt.grid(True)
            
            plt.tight_layout()
            plt.savefig("price_simulation.png")
            print("Price simulation plot saved to price_simulation.png")
    print()

def test_price_optimization():
    """Test the price optimization functionality"""
    print("=== Testing Price Optimization ===")
    
    # Sample input
    input_data = {
        'Unit Price': 100,
        'Unit Cost': 50,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': 12,
        'Year': 2023
    }
    
    # Optimize for profit
    profit_result = optimize_price(input_data, metric="profit")
    
    if "error" in profit_result:
        print(f"Profit optimization error: {profit_result['error']}")
    else:
        print("Profit Optimization Results:")
        print(f"Base Price: ${profit_result.get('base_price', 0)}")
        print(f"Optimal Price: ${profit_result.get('optimal_price', 0)}")
        print(f"Optimal Profit: ${profit_result.get('optimal_value', 0)}")
        print(f"Quantity at Optimal: {profit_result.get('quantity_at_optimal', 0)}")
        print(f"Profit Margin at Optimal: {profit_result.get('profit_margin_at_optimal', 0)}%")
    
    print()
    
    # Optimize for revenue
    revenue_result = optimize_price(input_data, metric="revenue")
    
    if "error" in revenue_result:
        print(f"Revenue optimization error: {revenue_result['error']}")
    else:
        print("Revenue Optimization Results:")
        print(f"Base Price: ${revenue_result.get('base_price', 0)}")
        print(f"Optimal Price: ${revenue_result.get('optimal_price', 0)}")
        print(f"Optimal Revenue: ${revenue_result.get('optimal_value', 0)}")
        print(f"Quantity at Optimal: {revenue_result.get('quantity_at_optimal', 0)}")
    
    print()

if __name__ == "__main__":
    # Run all tests
    test_health()
    test_model_info()
    test_basic_prediction()
    test_price_sensitivity()
    test_product_variations()
    test_seasonal_variations()
    test_price_simulation()
    test_price_optimization()
    
    print("All tests completed. Check the generated plots for visualizations.") 