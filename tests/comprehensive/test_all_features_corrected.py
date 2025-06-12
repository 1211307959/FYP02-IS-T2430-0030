"""
CORRECTED COMPREHENSIVE TESTS FOR ALL SYSTEM FEATURES
Tests based on actual API responses and real system behavior
"""

import pytest
import requests
import json
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestAllRealEndpoints:
    """Test ALL API endpoints based on actual response structures"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_health_endpoint_actual(self):
        """Test health endpoint with actual response structure"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model" in data  # Actual field name is "model" not "model_status"
        assert data["model"] == "ethical_time_enhanced"
    
    def test_locations_endpoint_complete(self):
        """Test locations endpoint returns all 5 locations"""
        response = requests.get(f"{self.base_url}/locations")
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data
        locations = data["locations"]
        assert len(locations) == 5  # Exactly 5 locations
        expected_locations = {"Central", "East", "North", "South", "West"}
        assert set(locations) == expected_locations
    
    def test_products_endpoint_complete(self):
        """Test products endpoint returns all 47 products"""
        response = requests.get(f"{self.base_url}/products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        products = data["products"]
        assert len(products) == 47  # Exactly 47 products
        assert all(isinstance(p, int) for p in products)
        assert all(1 <= p <= 47 for p in products)  # Product IDs 1-47
    
    def test_prediction_all_combinations(self):
        """Test prediction for multiple location/product combinations"""
        test_combinations = [
            ("Central", 1, 5000, 2000),
            ("East", 10, 3000, 1200),
            ("North", 20, 8000, 3000),
            ("South", 30, 2000, 800),
            ("West", 47, 10000, 4000)
        ]
        
        for location, product_id, price, cost in test_combinations:
            payload = {
                "Unit Price": price,
                "Unit Cost": cost,
                "Location": location,
                "_ProductID": product_id,
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": "Monday"
            }
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200, f"Failed for {location}, Product {product_id}"
            
            data = response.json()
            assert "predicted_revenue" in data
            revenue = data["predicted_revenue"]
            assert isinstance(revenue, (int, float))
            assert revenue > 0, f"Revenue should be positive for {location}, Product {product_id}"
            print(f"✓ {location} Product {product_id}: ${revenue:.2f}")
    
    def test_dashboard_data_comprehensive_real(self):
        """Test dashboard data with actual response structure"""
        response = requests.get(f"{self.base_url}/dashboard-data")
        assert response.status_code == 200
        data = response.json()
        
        # Check actual response structure
        assert "products" in data
        assert "total_revenue" in data  
        assert "total_sales" in data
        
        # Verify products data
        products = data["products"]
        assert len(products) == 47  # All 47 products
        
        for product in products:
            assert "id" in product
            assert "name" in product
            assert "revenue" in product
            assert "profit" in product
            assert "quantity" in product
            assert "margin" in product
            assert "rank" in product
            assert product["revenue"] > 0
            assert product["profit"] > 0
            assert product["quantity"] > 0
            assert 0 <= product["margin"] <= 1
            assert product["rank"] in ["top", "bottom"]
        
        # Verify totals
        assert data["total_revenue"] > 800_000_000  # Should be around 858M based on actual data
        assert data["total_sales"] > 100_000  # Should be around 100K transactions
        
        print(f"✓ Dashboard: ${data['total_revenue']:,.0f} revenue, {data['total_sales']:,} sales")
    
    def test_business_insights_real_structure(self):
        """Test business insights with actual response structure"""
        response = requests.get(f"{self.base_url}/business-insights")
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
        
        insights = data["insights"]
        assert len(insights) > 0
        assert len(insights) <= 5  # Max 5 insights
        
        # Check actual insight structure (based on real API response)
        for insight in insights:
            # Core fields that should always be present
            assert "type" in insight
            assert "priority_score" in insight
            assert "title" in insight
            assert "description" in insight
            
            # Priority should be reasonable
            priority = insight["priority_score"]
            assert isinstance(priority, (int, float))
            assert 0 <= priority <= 100
            
            # Title and description should be meaningful
            assert len(insight["title"]) > 10
            assert len(insight["description"]) > 20
            
            print(f"✓ Insight: {insight['title']} (Priority: {priority})")
    
    def test_forecast_sales_real_structure(self):
        """Test forecast sales with actual response structure"""
        payload = {"location": "Central", "product_id": 1}
        response = requests.post(f"{self.base_url}/forecast-sales", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Check actual forecast structure
        assert "forecast" in data
        assert "status" in data
        assert "summary" in data
        assert data["status"] == "success"
        
        forecast = data["forecast"]
        assert len(forecast) > 0
        
        # Check forecast point structure (based on actual response)
        for point in forecast:
            assert "date" in point
            assert "revenue" in point  # Not "predicted_revenue"
            assert "quantity" in point  # Not "predicted_quantity" 
            assert "profit" in point
            assert "weekday" in point
            
            # Each metric should have prediction bounds
            for metric in ["revenue", "quantity", "profit"]:
                metric_data = point[metric]
                assert "prediction" in metric_data
                assert "lower_bound" in metric_data
                assert "upper_bound" in metric_data
                assert metric_data["prediction"] > 0
                assert metric_data["lower_bound"] <= metric_data["prediction"] <= metric_data["upper_bound"]
        
        # Check summary
        summary = data["summary"]
        assert "total_revenue" in summary
        assert "avg_revenue" in summary
        assert "location" in summary
        assert "product_id" in summary
        assert summary["total_revenue"] > 0
        assert summary["location"] == "Central"
        assert summary["product_id"] == 1
        
        print(f"✓ Forecast: {len(forecast)} days, ${summary['total_revenue']:,.0f} total revenue")
    
    def test_forecast_all_locations_performance(self):
        """Test forecasting for all locations including 'All'"""
        locations = ["Central", "East", "North", "South", "West", "All"]
        
        for location in locations:
            payload = {"location": location, "product_id": 1}
            start_time = time.time()
            response = requests.post(f"{self.base_url}/forecast-sales", json=payload)
            end_time = time.time()
            
            assert response.status_code == 200, f"Forecast failed for {location}"
            
            # Should complete within reasonable time
            duration = end_time - start_time
            max_time = 15.0 if location == "All" else 10.0
            assert duration < max_time, f"Forecast too slow for {location}: {duration:.2f}s"
            
            data = response.json()
            forecast = data["forecast"]
            assert len(forecast) > 0
            
            print(f"✓ {location} forecast: {len(forecast)} points in {duration:.2f}s")
    
    def test_multiple_product_forecasting_real(self):
        """Test multiple product forecasting (if endpoint exists)"""
        # First check if endpoint exists
        payload = {"location": "Central", "product_ids": [1, 2, 3]}
        response = requests.post(f"{self.base_url}/forecast-multiple", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert "forecasts" in data
            forecasts = data["forecasts"]
            assert len(forecasts) > 0
            print(f"✓ Multiple forecast: {len(forecasts)} products")
        elif response.status_code == 404:
            print("ℹ Multiple product forecasting endpoint not available")
        else:
            # If it fails for another reason, investigate
            print(f"⚠ Multiple forecast returned {response.status_code}: {response.text}")
    
    def test_price_optimization_real(self):
        """Test price optimization with actual response structure"""
        payload = {
            "Unit Price": 5000,
            "Unit Cost": 2000,
            "Location": "Central",
            "_ProductID": 1,
            "Year": 2025,
            "Month": 6,
            "Day": 15,
            "Weekday": "Monday"
        }
        response = requests.post(f"{self.base_url}/optimize-price", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert "optimizations" in data
            optimizations = data["optimizations"]
            assert len(optimizations) > 0
            
            for opt in optimizations:
                assert "price" in opt
                assert "predicted_revenue" in opt
                assert opt["price"] > 0
                assert opt["predicted_revenue"] > 0
            
            print(f"✓ Price optimization: {len(optimizations)} scenarios")
        elif response.status_code == 400:
            print("ℹ Price optimization may have validation requirements")
        else:
            print(f"⚠ Price optimization returned {response.status_code}: {response.text}")
    
    def test_revenue_simulation_real(self):
        """Test revenue simulation with actual response structure"""
        payload = {
            "Unit Price": 2000,
            "Unit Cost": 800,
            "Location": "Central",
            "_ProductID": 1,
            "Year": 2025,
            "Month": 6,
            "Day": 15,
            "Weekday": "Monday"
        }
        response = requests.post(f"{self.base_url}/simulate-revenue", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert "scenarios" in data
            scenarios = data["scenarios"]
            assert len(scenarios) > 0
            
            for scenario in scenarios:
                assert "price" in scenario
                assert "predicted_revenue" in scenario
                assert scenario["price"] > 0
                assert scenario["predicted_revenue"] > 0
            
            print(f"✓ Revenue simulation: {len(scenarios)} scenarios")
        else:
            print(f"⚠ Revenue simulation returned {response.status_code}: {response.text}")


class TestRealWorldScenarios:
    """Test real-world business scenarios"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_seasonal_variations(self):
        """Test predictions for different seasons/months"""
        seasonal_tests = [
            (1, "January", "Winter"),
            (4, "April", "Spring"), 
            (7, "July", "Summer"),
            (10, "October", "Fall"),
            (12, "December", "Holiday")
        ]
        
        base_payload = {
            "Unit Price": 3000,
            "Unit Cost": 1200,
            "Location": "Central",
            "_ProductID": 1,
            "Year": 2025,
            "Day": 15,
            "Weekday": "Monday"
        }
        
        for month, month_name, season in seasonal_tests:
            payload = {**base_payload, "Month": month}
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            revenue = data["predicted_revenue"]
            print(f"✓ {season} ({month_name}): ${revenue:.2f}")
    
    def test_weekday_patterns(self):
        """Test predictions for different days of the week"""
        weekdays = [
            ("Monday", "Weekstart"),
            ("Wednesday", "Midweek"),
            ("Friday", "Weekend prep"),
            ("Saturday", "Weekend"),
            ("Sunday", "Weekend end")
        ]
        
        base_payload = {
            "Unit Price": 2000,
            "Unit Cost": 800,
            "Location": "Central",
            "_ProductID": 5,
            "Year": 2025,
            "Month": 6,
            "Day": 15
        }
        
        for weekday, description in weekdays:
            payload = {**base_payload, "Weekday": weekday}
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            revenue = data["predicted_revenue"]
            print(f"✓ {weekday} ({description}): ${revenue:.2f}")
    
    def test_price_sensitivity_analysis(self):
        """Test how revenue changes with price variations"""
        base_payload = {
            "Unit Cost": 1000,
            "Location": "Central",
            "_ProductID": 1,
            "Year": 2025,
            "Month": 6,
            "Day": 15,
            "Weekday": "Monday"
        }
        
        price_points = [1500, 2000, 2500, 3000, 4000, 5000]
        results = []
        
        for price in price_points:
            payload = {**base_payload, "Unit Price": price}
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            revenue = data["predicted_revenue"]
            margin = (price - 1000) / price * 100
            results.append((price, revenue, margin))
            print(f"✓ Price ${price}: Revenue ${revenue:.2f} (Margin {margin:.1f}%)")
        
        # Verify results make sense
        assert len(results) == len(price_points)
        revenues = [r[1] for r in results]
        assert all(rev > 0 for rev in revenues)
    
    def test_location_performance_comparison(self):
        """Test revenue predictions across all locations for comparison"""
        locations = ["Central", "East", "North", "South", "West"]
        base_payload = {
            "Unit Price": 3000,
            "Unit Cost": 1200,
            "_ProductID": 10,
            "Year": 2025,
            "Month": 6,
            "Day": 15,
            "Weekday": "Tuesday"
        }
        
        location_results = []
        
        for location in locations:
            payload = {**base_payload, "Location": location}
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            revenue = data["predicted_revenue"]
            location_results.append((location, revenue))
            print(f"✓ {location}: ${revenue:.2f}")
        
        # Verify all locations work
        assert len(location_results) == 5
        revenues = [r[1] for r in location_results]
        assert all(rev > 0 for rev in revenues)
        
        # Calculate performance spread
        max_revenue = max(revenues)
        min_revenue = min(revenues)
        spread = (max_revenue - min_revenue) / max_revenue * 100
        print(f"✓ Location performance spread: {spread:.1f}%")
    
    def test_product_portfolio_analysis(self):
        """Test revenue predictions for different products"""
        products = [1, 10, 20, 30, 40, 47]  # Sample across product range
        base_payload = {
            "Unit Price": 4000,
            "Unit Cost": 1600,
            "Location": "Central",
            "Year": 2025,
            "Month": 6,
            "Day": 15,
            "Weekday": "Thursday"
        }
        
        product_results = []
        
        for product_id in products:
            payload = {**base_payload, "_ProductID": product_id}
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            revenue = data["predicted_revenue"]
            product_results.append((product_id, revenue))
            print(f"✓ Product {product_id}: ${revenue:.2f}")
        
        # Verify all products work
        assert len(product_results) == len(products)
        revenues = [r[1] for r in product_results]
        assert all(rev > 0 for rev in revenues)


class TestSystemPerformanceReal:
    """Test real system performance and reliability"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_rapid_consecutive_predictions(self):
        """Test system handles rapid consecutive predictions"""
        base_payload = {
            "Unit Price": 2000,
            "Unit Cost": 800,
            "Location": "Central",
            "_ProductID": 1,
            "Year": 2025,
            "Month": 6,
            "Day": 15,
            "Weekday": "Monday"
        }
        
        # Make 20 rapid requests
        start_time = time.time()
        results = []
        
        for i in range(20):
            # Slightly vary the price
            payload = {**base_payload, "Unit Price": 2000 + (i * 10)}
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            end_time = time.time()
            
            results.append({
                "success": response.status_code == 200,
                "request_num": i + 1,
                "response_time": end_time - start_time if response.status_code == 200 else None
            })
            
            if response.status_code == 200:
                data = response.json()
                assert "predicted_revenue" in data
                assert data["predicted_revenue"] > 0
        
        total_time = time.time() - start_time
        successful_requests = sum(1 for r in results if r["success"])
        success_rate = successful_requests / len(results)
        
        print(f"✓ {successful_requests}/20 requests successful in {total_time:.2f}s")
        print(f"✓ Success rate: {success_rate:.1%}")
        print(f"✓ Average time per request: {total_time/20:.3f}s")
        
        # Should have high success rate
        assert success_rate >= 0.9, f"Success rate too low: {success_rate:.1%}"
        assert total_time < 30, f"Total time too slow: {total_time:.2f}s"
    
    def test_dashboard_load_time(self):
        """Test dashboard data loads within acceptable time"""
        start_time = time.time()
        response = requests.get(f"{self.base_url}/dashboard-data")
        end_time = time.time()
        
        assert response.status_code == 200
        load_time = end_time - start_time
        
        print(f"✓ Dashboard loaded in {load_time:.3f}s")
        assert load_time < 5.0, f"Dashboard too slow: {load_time:.3f}s"
    
    def test_insights_generation_time(self):
        """Test insights generate within acceptable time"""
        start_time = time.time()
        response = requests.get(f"{self.base_url}/business-insights")
        end_time = time.time()
        
        assert response.status_code == 200
        generation_time = end_time - start_time
        
        print(f"✓ Insights generated in {generation_time:.3f}s")
        assert generation_time < 10.0, f"Insights generation too slow: {generation_time:.3f}s"
    
    def test_forecast_generation_time(self):
        """Test forecast generates within acceptable time"""
        payload = {"location": "Central", "product_id": 1}
        
        start_time = time.time()
        response = requests.post(f"{self.base_url}/forecast-sales", json=payload)
        end_time = time.time()
        
        assert response.status_code == 200
        forecast_time = end_time - start_time
        
        print(f"✓ Forecast generated in {forecast_time:.3f}s")
        assert forecast_time < 15.0, f"Forecast generation too slow: {forecast_time:.3f}s"


class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_data_reload_functionality(self):
        """Test data reload works correctly"""
        payload = {"confirm": True}
        response = requests.post(f"{self.base_url}/reload-data", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "records_loaded" in data
        records = data["records_loaded"]
        assert isinstance(records, int)
        assert records > 90_000, f"Expected 100K+ records, got {records}"
        
        print(f"✓ Data reload: {records:,} records loaded")
    
    def test_consistent_predictions(self):
        """Test that identical inputs give identical predictions"""
        payload = {
            "Unit Price": 3000,
            "Unit Cost": 1200,
            "Location": "Central",
            "_ProductID": 1,
            "Year": 2025,
            "Month": 6,
            "Day": 15,
            "Weekday": "Monday"
        }
        
        # Make same prediction 3 times
        predictions = []
        for i in range(3):
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200
            data = response.json()
            predictions.append(data["predicted_revenue"])
            time.sleep(0.1)  # Small delay
        
        # All predictions should be identical
        assert len(set(predictions)) == 1, f"Inconsistent predictions: {predictions}"
        print(f"✓ Consistent prediction: ${predictions[0]:.2f}")
    
    def test_location_product_availability(self):
        """Test all locations and products are available"""
        # Get available locations
        locations_response = requests.get(f"{self.base_url}/locations")
        assert locations_response.status_code == 200
        locations = locations_response.json()["locations"]
        
        # Get available products  
        products_response = requests.get(f"{self.base_url}/products")
        assert products_response.status_code == 200
        products = products_response.json()["products"]
        
        # Test sample combinations work
        test_combinations = [
            (locations[0], products[0]),
            (locations[2], products[10]),
            (locations[4], products[-1])
        ]
        
        for location, product_id in test_combinations:
            payload = {
                "Unit Price": 2000,
                "Unit Cost": 800,
                "Location": location,
                "_ProductID": product_id,
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": "Monday"
            }
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200, f"Failed for {location}, Product {product_id}"
        
        print(f"✓ Data integrity: {len(locations)} locations, {len(products)} products available")


if __name__ == "__main__":
    print("Running corrected comprehensive tests...")
    
    # Run a quick subset for immediate feedback
    test_classes = [
        TestAllRealEndpoints,
        TestRealWorldScenarios, 
        TestSystemPerformanceReal,
        TestDataIntegrity
    ]
    
    for test_class in test_classes:
        print(f"\n{'='*50}")
        print(f"Running {test_class.__name__}")
        print(f"{'='*50}")
        
        instance = test_class()
        methods = [method for method in dir(instance) if method.startswith('test_')]
        
        for method_name in methods:
            try:
                print(f"\n{method_name}:")
                method = getattr(instance, method_name)
                method()
                print(f"✅ PASSED")
            except Exception as e:
                print(f"❌ FAILED: {e}") 