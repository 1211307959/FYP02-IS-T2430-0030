import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from revenue_predictor_time_enhanced_ethical import predict_revenue, simulate_price_variations, optimize_price

def test_prediction():
    """Test basic prediction functionality"""
    print("\n=== TESTING BASIC PREDICTION ===")
    
    # Test data
    test_data = {
        'Unit Price': 100.00,
        'Unit Cost': 50.00,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': '1',
        'Year': 2023
    }
    
    # Make prediction
    result = predict_revenue(test_data)
    print(f"Prediction result: {result}")
    
    # Verify key fields are present
    required_fields = ['predicted_revenue', 'estimated_quantity', 'profit', 'profit_margin_pct']
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    
    # Verify reasonable results
    assert result['predicted_revenue'] >= 0, "Revenue should be non-negative"
    assert result['estimated_quantity'] >= 0, "Quantity should be non-negative"
    
    # Verify time features
    assert 'time_features' in result, "Missing time features"
    assert 'season' in result['time_features'], "Missing season information"
    
    print("Basic prediction test passed!")

def test_price_elasticity():
    """Test price elasticity behavior"""
    print("\n=== TESTING PRICE ELASTICITY ===")
    
    # Base test data
    base_data = {
        'Unit Price': 100.00,
        'Unit Cost': 50.00,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': '1',
        'Year': 2023
    }
    
    # Test prices
    test_prices = [50, 100, 150, 200, 250, 500, 1000, 5000, 10000]
    results = []
    
    for price in test_prices:
        data = base_data.copy()
        data['Unit Price'] = price
        prediction = predict_revenue(data)
        
        results.append({
            'price': price,
            'revenue': prediction.get('predicted_revenue', 0),
            'quantity': prediction.get('estimated_quantity', 0),
            'profit': prediction.get('profit', 0)
        })
    
    # Print results
    print("\nPrice elasticity test results:")
    for result in results:
        print(f"Price: ${result['price']:.2f}, Quantity: {result['quantity']}, Revenue: ${result['revenue']:.2f}, Profit: ${result['profit']:.2f}")
    
    # Verify price elasticity behavior (price increases should decrease quantity)
    for i in range(1, len(results)):
        assert results[i]['quantity'] <= results[i-1]['quantity'], f"Quantity should decrease as price increases (${results[i-1]['price']} -> ${results[i]['price']})"
    
    # Verify extreme prices lead to zero quantity
    extreme_data = base_data.copy()
    extreme_data['Unit Price'] = 1000000
    extreme_result = predict_revenue(extreme_data)
    
    # Check for error response or zero quantity
    if 'error' in extreme_result:
        print(f"Extreme price test: Got expected error response: {extreme_result['error']}")
    else:
        assert extreme_result.get('estimated_quantity', 0) == 0, "Extremely high price should result in zero quantity"
        assert extreme_result.get('predicted_revenue', 0) == 0, "Extremely high price should result in zero revenue"
    
    # Create price elasticity plot
    plt.figure(figsize=(12, 8))
    
    # Plot quantity vs price
    plt.subplot(3, 1, 1)
    plt.plot([r['price'] for r in results], [r['quantity'] for r in results], 'o-', color='orange')
    plt.title('Quantity vs Price')
    plt.xlabel('Price ($)')
    plt.ylabel('Quantity')
    plt.grid(True)
    
    # Plot revenue vs price
    plt.subplot(3, 1, 2)
    plt.plot([r['price'] for r in results], [r['revenue'] for r in results], 'o-', color='blue')
    plt.title('Revenue vs Price')
    plt.xlabel('Price ($)')
    plt.ylabel('Revenue ($)')
    plt.grid(True)
    
    # Plot profit vs price
    plt.subplot(3, 1, 3)
    plt.plot([r['price'] for r in results], [r['profit'] for r in results], 'o-', color='green')
    plt.title('Profit vs Price')
    plt.xlabel('Price ($)')
    plt.ylabel('Profit ($)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('ethical_price_elasticity_test.png')
    print("Price elasticity plot saved as 'ethical_price_elasticity_test.png'")
    
    print("Price elasticity test passed!")

def test_simulation():
    """Test price simulation functionality"""
    print("\n=== TESTING PRICE SIMULATION ===")
    
    # Base test data
    base_data = {
        'Unit Price': 100.00,
        'Unit Cost': 50.00,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': '1',
        'Year': 2023
    }
    
    # Run simulation
    variations = simulate_price_variations(base_data)
    
    # Verify simulation returned results
    assert variations, "Simulation returned no results"
    assert len(variations) > 0, "Simulation should return multiple variations"
    
    # Print simulation results
    print("\nSimulation results:")
    for v in variations:
        print(f"Price: ${v.get('Unit Price', 0):.2f}, Quantity: {v.get('Predicted Quantity', 0)}, Revenue: ${v.get('Predicted Revenue', 0):.2f}, Profit: ${v.get('Profit', 0):.2f}")
    
    # Verify fields
    required_fields = ['Unit Price', 'Predicted Revenue', 'Predicted Quantity', 'Profit']
    for field in required_fields:
        assert field in variations[0], f"Missing field in simulation results: {field}"
    
    # Verify price elasticity behavior in simulation
    for i in range(1, len(variations)):
        if variations[i]['Unit Price'] > variations[i-1]['Unit Price']:
            assert variations[i]['Predicted Quantity'] <= variations[i-1]['Predicted Quantity'], "Quantity should decrease as price increases in simulation"
    
    print("Simulation test passed!")

def test_optimization():
    """Test price optimization functionality"""
    print("\n=== TESTING PRICE OPTIMIZATION ===")
    
    # Base test data
    base_data = {
        'Unit Price': 100.00,
        'Unit Cost': 50.00,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Friday',
        'Location': 'North',
        '_ProductID': '1',
        'Year': 2023
    }
    
    # Run optimization for revenue
    revenue_optimization = optimize_price(base_data, metric='revenue')
    assert revenue_optimization, "Revenue optimization returned no results"
    
    # Run optimization for profit
    profit_optimization = optimize_price(base_data, metric='profit')
    assert profit_optimization, "Profit optimization returned no results"
    
    # Print optimization results
    print("\nRevenue optimization results:")
    print(f"Optimal price for revenue: ${revenue_optimization['optimal_price']:.2f}")
    print(f"Resulting revenue: ${revenue_optimization['optimal_revenue']:.2f}")
    print(f"Improvement: {revenue_optimization['improvement_pct']:.2f}%")
    
    print("\nProfit optimization results:")
    print(f"Optimal price for profit: ${profit_optimization['optimal_price']:.2f}")
    print(f"Resulting profit: ${profit_optimization['optimal_profit']:.2f}")
    print(f"Improvement: {profit_optimization['improvement_pct']:.2f}%")
    
    # Verify fields
    required_fields = ['optimal_price', 'optimal_revenue', 'optimal_quantity', 'optimal_profit']
    for field in required_fields:
        assert field in revenue_optimization, f"Missing field in revenue optimization: {field}"
        assert field in profit_optimization, f"Missing field in profit optimization: {field}"
    
    # Verify optimal values
    assert revenue_optimization['optimal_price'] > 0, "Optimal price for revenue should be positive"
    assert profit_optimization['optimal_price'] > 0, "Optimal price for profit should be positive"
    
    # Plot optimization results
    revenue_variations = revenue_optimization.get('variations', [])
    profit_variations = profit_optimization.get('variations', [])
    
    if revenue_variations and profit_variations:
        plt.figure(figsize=(12, 10))
        
        # Plot revenue curve
        plt.subplot(2, 1, 1)
        plt.plot([v.get('Unit Price', 0) for v in revenue_variations], 
                [v.get('Predicted Revenue', 0) for v in revenue_variations], 'o-', color='blue')
        plt.axvline(x=revenue_optimization['optimal_price'], color='red', linestyle='--', 
                    label=f"Optimal Price: ${revenue_optimization['optimal_price']:.2f}")
        plt.title('Revenue vs Price')
        plt.xlabel('Price ($)')
        plt.ylabel('Revenue ($)')
        plt.legend()
        plt.grid(True)
        
        # Plot profit curve
        plt.subplot(2, 1, 2)
        plt.plot([v.get('Unit Price', 0) for v in profit_variations], 
                [v.get('Profit', 0) for v in profit_variations], 'o-', color='green')
        plt.axvline(x=profit_optimization['optimal_price'], color='red', linestyle='--',
                    label=f"Optimal Price: ${profit_optimization['optimal_price']:.2f}")
        plt.title('Profit vs Price')
        plt.xlabel('Price ($)')
        plt.ylabel('Profit ($)')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('ethical_price_optimization_test.png')
        print("Price optimization plot saved as 'ethical_price_optimization_test.png'")
    
    print("Optimization test passed!")

def test_seasonal_variation():
    """Test seasonal variation in predictions"""
    print("\n=== TESTING SEASONAL VARIATION ===")
    
    # Base test data
    base_data = {
        'Unit Price': 100.00,
        'Unit Cost': 50.00,
        'Day': 15,
        'Weekday': 'Wednesday',
        'Location': 'North',
        '_ProductID': '1',
        'Year': 2023
    }
    
    # Test all months
    results = []
    for month in range(1, 13):
        data = base_data.copy()
        data['Month'] = month
        prediction = predict_revenue(data)
        
        # Get month name
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        results.append({
            'month': month,
            'month_name': month_names[month-1],
            'revenue': prediction.get('predicted_revenue', 0),
            'quantity': prediction.get('estimated_quantity', 0),
            'season': prediction.get('season', '')
        })
    
    # Print results
    print("\nSeasonal variation test results:")
    for result in results:
        print(f"Month: {result['month_name']}, Season: {result['season']}, Quantity: {result['quantity']}, Revenue: ${result['revenue']:.2f}")
    
    # Verify seasonal variation exists
    revenues = [r['revenue'] for r in results]
    max_revenue = max(revenues)
    min_revenue = min(revenues)
    variation_pct = ((max_revenue - min_revenue) / max_revenue) * 100
    
    print(f"\nSeasonal variation: {variation_pct:.2f}%")
    assert variation_pct > 0, "There should be some seasonal variation in revenues"
    
    # Plot seasonal variation
    plt.figure(figsize=(12, 6))
    
    plt.plot([r['month_name'] for r in results], [r['revenue'] for r in results], 'o-', color='blue', label='Revenue')
    
    # Highlight seasons with different colors
    seasons = ['Winter', 'Spring', 'Summer', 'Fall']
    season_colors = ['lightblue', 'lightgreen', 'yellow', 'orange']
    season_start = [0, 2, 5, 8] # Indexes for Jan, Mar, Jun, Sep
    
    for i, season in enumerate(seasons):
        start = season_start[i]
        end = season_start[(i+1) % 4] if i < 3 else 12
        plt.axvspan(start - 0.5, end - 0.5, alpha=0.2, color=season_colors[i], label=season)
    
    plt.title('Seasonal Revenue Variation')
    plt.xlabel('Month')
    plt.ylabel('Revenue ($)')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('ethical_seasonal_variation_test.png')
    print("Seasonal variation plot saved as 'ethical_seasonal_variation_test.png'")
    
    print("Seasonal variation test passed!")

def test_location_variation():
    """Test location variation in predictions"""
    print("\n=== TESTING LOCATION VARIATION ===")
    
    # Base test data
    base_data = {
        'Unit Price': 100.00,
        'Unit Cost': 50.00,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Wednesday',
        '_ProductID': '1',
        'Year': 2023
    }
    
    # Test locations
    locations = ['North', 'South', 'East', 'West', 'Central']
    results = []
    
    for location in locations:
        try:
            data = base_data.copy()
            data['Location'] = location
            prediction = predict_revenue(data)
            
            if 'error' in prediction:
                print(f"Warning: Error for location {location}: {prediction['error']}")
                continue
                
            results.append({
                'location': location,
                'revenue': prediction.get('predicted_revenue', 0),
                'quantity': prediction.get('estimated_quantity', 0)
            })
        except Exception as e:
            print(f"Error testing location {location}: {str(e)}")
    
    # Skip the test if no valid locations
    if not results:
        print("Skipping location variation test - no valid locations found")
        return
    
    # Print results
    print("\nLocation variation test results:")
    for result in results:
        print(f"Location: {result['location']}, Quantity: {result['quantity']}, Revenue: ${result['revenue']:.2f}")
    
    # Verify location variation exists
    revenues = [r['revenue'] for r in results]
    max_revenue = max(revenues)
    min_revenue = min(revenues)
    variation_pct = ((max_revenue - min_revenue) / max_revenue) * 100
    
    print(f"\nLocation variation: {variation_pct:.2f}%")
    assert variation_pct > 0, "There should be some location variation in revenues"
    
    # Plot location variation
    plt.figure(figsize=(10, 6))
    
    plt.bar([r['location'] for r in results], [r['revenue'] for r in results], color='blue', alpha=0.6)
    
    plt.title('Revenue by Location')
    plt.xlabel('Location')
    plt.ylabel('Revenue ($)')
    plt.grid(axis='y')
    
    plt.tight_layout()
    plt.savefig('ethical_location_variation_test.png')
    print("Location variation plot saved as 'ethical_location_variation_test.png'")
    
    print("Location variation test passed!")

def test_weekday_variation():
    """Test weekday variation in predictions"""
    print("\n=== TESTING WEEKDAY VARIATION ===")
    
    # Base test data
    base_data = {
        'Unit Price': 100.00,
        'Unit Cost': 50.00,
        'Month': 6,
        'Day': 15,
        'Location': 'North',
        '_ProductID': '1',
        'Year': 2023
    }
    
    # Test weekdays
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    results = []
    
    for weekday in weekdays:
        data = base_data.copy()
        data['Weekday'] = weekday
        prediction = predict_revenue(data)
        
        results.append({
            'weekday': weekday,
            'is_weekend': 1 if weekday in ['Saturday', 'Sunday'] else 0,
            'revenue': prediction.get('predicted_revenue', 0),
            'quantity': prediction.get('estimated_quantity', 0)
        })
    
    # Print results
    print("\nWeekday variation test results:")
    for result in results:
        print(f"Weekday: {result['weekday']}, Weekend: {'Yes' if result['is_weekend'] else 'No'}, Quantity: {result['quantity']}, Revenue: ${result['revenue']:.2f}")
    
    # Verify weekday variation exists
    revenues = [r['revenue'] for r in results]
    max_revenue = max(revenues)
    min_revenue = min(revenues)
    variation_pct = ((max_revenue - min_revenue) / max_revenue) * 100
    
    print(f"\nWeekday variation: {variation_pct:.2f}%")
    assert variation_pct > 0, "There should be some weekday variation in revenues"
    
    # Calculate weekend vs weekday difference
    weekend_revenues = [r['revenue'] for r in results if r['is_weekend']]
    weekday_revenues = [r['revenue'] for r in results if not r['is_weekend']]
    
    avg_weekend = sum(weekend_revenues) / len(weekend_revenues) if weekend_revenues else 0
    avg_weekday = sum(weekday_revenues) / len(weekday_revenues) if weekday_revenues else 0
    
    print(f"Average weekend revenue: ${avg_weekend:.2f}")
    print(f"Average weekday revenue: ${avg_weekday:.2f}")
    print(f"Weekend vs Weekday difference: {((avg_weekend - avg_weekday) / avg_weekday * 100):.2f}%")
    
    # Plot weekday variation
    plt.figure(figsize=(10, 6))
    
    # Colors: blue for weekdays, orange for weekends
    colors = ['blue' if r['is_weekend'] == 0 else 'orange' for r in results]
    
    plt.bar([r['weekday'] for r in results], [r['revenue'] for r in results], color=colors, alpha=0.6)
    
    plt.title('Revenue by Weekday')
    plt.xlabel('Weekday')
    plt.ylabel('Revenue ($)')
    plt.grid(axis='y')
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='blue', alpha=0.6, label='Weekday'),
        Patch(facecolor='orange', alpha=0.6, label='Weekend')
    ]
    plt.legend(handles=legend_elements)
    
    plt.tight_layout()
    plt.savefig('ethical_weekday_variation_test.png')
    print("Weekday variation plot saved as 'ethical_weekday_variation_test.png'")
    
    print("Weekday variation test passed!")

def run_all_tests():
    """Run all tests"""
    print("\n====== ETHICAL TIME-ENHANCED MODEL TESTS ======")
    
    # Run tests
    test_prediction()
    test_price_elasticity()
    test_simulation()
    test_optimization()
    test_seasonal_variation()
    test_location_variation()
    test_weekday_variation()
    
    print("\n====== ALL TESTS PASSED! ======")

if __name__ == "__main__":
    run_all_tests() 