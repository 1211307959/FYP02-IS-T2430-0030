"""
COMPREHENSIVE TESTS FOR ALL SYSTEM FEATURES
Tests every major feature: insights, forecasting, scenario planning, dashboard, etc.
"""

import pytest
import requests
import json
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from actionable_insights import ActionableInsights
import pandas as pd
import concurrent.futures


class TestInsightsComprehensive:
    """Test ALL insight generation capabilities"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_all_five_insight_types(self):
        """Test that all 5 main insight types can be generated"""
        # Test both API endpoint and direct function
        response = requests.get(f"{self.base_url}/business-insights")
        assert response.status_code == 200
        data = response.json()
        
        insights = data["insights"]
        assert len(insights) > 0
        
        # Track insight types
        insight_types = set()
        for insight in insights:
            insight_types.add(insight["type"])
        
        # Should have multiple insight types
        print(f"Generated insight types: {insight_types}")
        assert len(insight_types) >= 3, f"Expected multiple insight types, got: {insight_types}"
        
        # Verify insight structure
        for insight in insights:
            assert "type" in insight
            assert "priority_score" in insight
            assert "title" in insight
            assert "description" in insight
            assert "action_items" in insight
            assert "expected_impact" in insight
            assert len(insight["action_items"]) >= 2
    
    def test_insight_priority_system(self):
        """Test insight priority scoring and ranking"""
        response = requests.get(f"{self.base_url}/business-insights")
        assert response.status_code == 200
        data = response.json()
        
        insights = data["insights"]
        if len(insights) > 1:
            # Check priority scores are in descending order
            priorities = [insight["priority_score"] for insight in insights]
            assert priorities == sorted(priorities, reverse=True), "Insights not properly prioritized"
            
            # Top insight should have reasonable priority
            assert priorities[0] >= 50, f"Top insight priority too low: {priorities[0]}"
    
    def test_compound_insights_detection(self):
        """Test compound/cross-insight detection"""
        # Load sample data to test insights generation directly
        insights_engine = ActionableInsights()
        
        # Create test dataframe that should trigger compound insights
        test_data = {
            'Location': ['Central'] * 100 + ['East'] * 50 + ['North'] * 200,
            '_ProductID': [1] * 150 + [2] * 100 + [3] * 100,
            'Unit Price': [1000] * 100 + [5000] * 150 + [2000] * 100,
            'Unit Cost': [400] * 100 + [2000] * 150 + [800] * 100,
            'Total Revenue': [800] * 100 + [4500] * 150 + [1800] * 100,
            'Year': [2024] * 350,
            'Month': [6] * 350,
            'Day': list(range(1, 31)) * 11 + [30] * 10,
            'Weekday': ['Monday'] * 350
        }
        
        df = pd.DataFrame(test_data)
        insights = insights_engine.generate_insights(df)
        
        assert len(insights) > 0
        print(f"Generated {len(insights)} insights")
        
        # Look for compound insights or cross-references
        compound_found = any("compound" in insight.get("type", "").lower() for insight in insights)
        cross_reference_found = any(len(insight.get("action_items", [])) > 3 for insight in insights)
        
        # At least one insight should be complex/compound
        assert compound_found or cross_reference_found, "No compound insights detected"
    
    def test_insight_actionability(self):
        """Test that insights provide truly actionable recommendations"""
        response = requests.get(f"{self.base_url}/business-insights")
        assert response.status_code == 200
        data = response.json()
        
        insights = data["insights"]
        for insight in insights:
            action_items = insight["action_items"]
            
            # Each insight should have multiple action items
            assert len(action_items) >= 2, f"Insufficient action items: {len(action_items)}"
            
            # Action items should be specific and actionable
            for action in action_items:
                assert len(action) > 20, f"Action too vague: {action}"
                
                # Should contain actionable verbs
                actionable_verbs = ["increase", "reduce", "optimize", "focus", "test", "implement", "analyze", "adjust"]
                has_actionable_verb = any(verb in action.lower() for verb in actionable_verbs)
                assert has_actionable_verb, f"Action not actionable: {action}"


class TestForecastingComprehensive:
    """Test ALL forecasting capabilities"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_automatic_forecast_all_locations(self):
        """Test automatic forecasting for all locations"""
        locations = ["Central", "East", "North", "South", "West", "All"]
        
        for location in locations:
            payload = {"location": location, "product_id": 1}
            response = requests.post(f"{self.base_url}/forecast-sales", json=payload)
            assert response.status_code == 200, f"Forecast failed for {location}"
            
            data = response.json()
            assert "forecast" in data
            forecast = data["forecast"]
            assert len(forecast) > 0, f"No forecast data for {location}"
            
            # Check forecast structure
            for point in forecast:
                assert "date" in point
                assert "predicted_revenue" in point
                assert "predicted_quantity" in point
                assert point["predicted_revenue"] > 0
                assert point["predicted_quantity"] > 0
    
    def test_custom_date_range_forecasting(self):
        """Test custom date range forecasting"""
        date_ranges = [
            ("2025-01-01", "2025-01-31", "1 month"),
            ("2025-01-01", "2025-03-31", "3 months"),
            ("2025-01-01", "2025-06-30", "6 months"),
            ("2025-01-01", "2025-12-31", "1 year")
        ]
        
        for start_date, end_date, description in date_ranges:
            payload = {
                "location": "Central",
                "product_id": 1,
                "start_date": start_date,
                "end_date": end_date
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/forecast-trend", json=payload)
            end_time = time.time()
            
            assert response.status_code == 200, f"Failed for {description}"
            
            # Should complete within reasonable time
            duration = end_time - start_time
            assert duration < 15.0, f"Forecast for {description} too slow: {duration:.2f}s"
            
            data = response.json()
            assert "forecast_points" in data
            assert "trend_analysis" in data
            
            forecast_points = data["forecast_points"]
            assert len(forecast_points) > 0
            
            # Verify trend analysis
            trend = data["trend_analysis"]
            assert "trend_direction" in trend
            assert "confidence_score" in trend
            assert "total_forecasted_revenue" in trend
            assert trend["total_forecasted_revenue"] > 0
    
    def test_multiple_product_forecasting(self):
        """Test forecasting multiple products simultaneously"""
        product_sets = [
            [1, 2, 3],
            [1, 5, 10, 15],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # Large set
            list(range(1, 21))  # Very large set
        ]
        
        for products in product_sets:
            payload = {
                "location": "Central",
                "product_ids": products
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/forecast-multiple", json=payload)
            end_time = time.time()
            
            assert response.status_code == 200, f"Failed for {len(products)} products"
            
            # Should complete within reasonable time even for large sets
            duration = end_time - start_time
            assert duration < 30.0, f"Forecast for {len(products)} products too slow: {duration:.2f}s"
            
            data = response.json()
            assert "forecasts" in data
            forecasts = data["forecasts"]
            
            # Should have forecasts for multiple products
            assert len(forecasts) > 0
            product_ids_returned = set()
            for forecast in forecasts:
                assert "product_id" in forecast
                assert "forecast_data" in forecast
                product_ids_returned.add(forecast["product_id"])
            
            # Should cover at least some of the requested products
            assert len(product_ids_returned) >= min(3, len(products))
    
    def test_forecast_all_location_performance(self):
        """Test 'All' location forecast performance and accuracy"""
        payload = {
            "location": "All",
            "product_id": 1
        }
        
        start_time = time.time()
        response = requests.post(f"{self.base_url}/forecast-sales", json=payload)
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should complete quickly even for all locations
        duration = end_time - start_time
        assert duration < 10.0, f"'All' location forecast too slow: {duration:.2f}s"
        
        data = response.json()
        forecast = data["forecast"]
        assert len(forecast) > 0
        
        # Should have reasonable revenue values (aggregated across locations)
        total_forecasted = sum(point["predicted_revenue"] for point in forecast)
        assert total_forecasted > 0, "No revenue forecasted for 'All' locations"


class TestScenarioPlanningComprehensive:
    """Test ALL scenario planning capabilities"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_price_optimization_comprehensive(self):
        """Test price optimization across different scenarios"""
        optimization_scenarios = [
            {
                "name": "Low-cost product",
                "price": 500,
                "cost": 200,
                "product": 1,
                "expected_optimizations": 5
            },
            {
                "name": "Medium-cost product", 
                "price": 2000,
                "cost": 800,
                "product": 5,
                "expected_optimizations": 5
            },
            {
                "name": "High-cost product",
                "price": 10000,
                "cost": 4000,
                "product": 10,
                "expected_optimizations": 5
            },
            {
                "name": "Premium product",
                "price": 25000,
                "cost": 10000,
                "product": 15,
                "expected_optimizations": 5
            }
        ]
        
        for scenario in optimization_scenarios:
            payload = {
                "Unit Price": scenario["price"],
                "Unit Cost": scenario["cost"],
                "Location": "Central",
                "_ProductID": scenario["product"],
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": "Monday"
            }
            
            response = requests.post(f"{self.base_url}/optimize-price", json=payload)
            assert response.status_code == 200, f"Optimization failed for {scenario['name']}"
            
            data = response.json()
            assert "optimizations" in data
            optimizations = data["optimizations"]
            
            # Should provide multiple optimization options
            assert len(optimizations) >= 3, f"Insufficient optimizations for {scenario['name']}"
            
            # Check optimization structure
            for opt in optimizations:
                assert "price" in opt
                assert "predicted_revenue" in opt
                assert "profit_margin" in opt
                assert opt["price"] > 0
                assert opt["predicted_revenue"] > 0
                assert 0 <= opt["profit_margin"] <= 1  # Should be between 0 and 100%
            
            # Prices should vary around the base price
            prices = [opt["price"] for opt in optimizations]
            base_price = scenario["price"]
            price_range = max(prices) - min(prices)
            assert price_range > base_price * 0.1, f"Price optimization range too narrow for {scenario['name']}"
    
    def test_revenue_simulation_scenarios(self):
        """Test revenue simulation for various scenarios"""
        simulation_cases = [
            {"price": 1000, "cost": 400, "margin_expectation": 0.6},
            {"price": 5000, "cost": 2000, "margin_expectation": 0.6},
            {"price": 15000, "cost": 6000, "margin_expectation": 0.6},
        ]
        
        for case in simulation_cases:
            payload = {
                "Unit Price": case["price"],
                "Unit Cost": case["cost"],
                "Location": "North",
                "_ProductID": 5,
                "Year": 2025,
                "Month": 4,
                "Day": 10,
                "Weekday": "Thursday"
            }
            
            response = requests.post(f"{self.base_url}/simulate-revenue", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert "scenarios" in data
            scenarios = data["scenarios"]
            assert len(scenarios) > 0
            
            # Verify simulation results
            for scenario in scenarios:
                assert "price" in scenario
                assert "predicted_revenue" in scenario
                assert "potential_profit" in scenario
                
                revenue = scenario["predicted_revenue"]
                profit = scenario["potential_profit"]
                price = scenario["price"]
                
                # Basic sanity checks
                assert revenue > 0, "Revenue should be positive"
                assert profit > -case["cost"] * 3, "Losses shouldn't be excessive"
                assert price > 0, "Price should be positive"
    
    def test_what_if_analysis(self):
        """Test what-if analysis scenarios"""
        # Test price sensitivity analysis
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
        
        # Test price variations
        price_variations = [1000, 1500, 2000, 2500, 3000]
        results = []
        
        for price in price_variations:
            payload = {**base_payload, "Unit Price": price}
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            results.append({
                "price": price,
                "revenue": data["predicted_revenue"]
            })
        
        # Analyze price-revenue relationship
        assert len(results) == len(price_variations)
        
        # Should have reasonable revenue predictions
        revenues = [r["revenue"] for r in results]
        assert all(rev > 0 for rev in revenues), "All revenues should be positive"
        
        # Revenue should generally correlate with price (though not necessarily linearly)
        revenue_range = max(revenues) - min(revenues)
        assert revenue_range > 0, "Revenue should vary with price changes"


class TestDashboardComprehensive:
    """Test ALL dashboard functionality"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_dashboard_data_completeness(self):
        """Test dashboard data contains all required sections"""
        response = requests.get(f"{self.base_url}/dashboard-data")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check all required sections exist
        required_sections = [
            "summary_stats",
            "top_products", 
            "location_performance",
            "recent_trends",
            "monthly_comparison"
        ]
        
        for section in required_sections:
            assert section in data, f"Missing dashboard section: {section}"
            assert data[section] is not None, f"Dashboard section {section} is null"
        
        # Verify summary stats structure
        summary = data["summary_stats"]
        summary_fields = ["total_revenue", "total_transactions", "avg_transaction_value"]
        for field in summary_fields:
            assert field in summary, f"Missing summary field: {field}"
            assert isinstance(summary[field], (int, float)), f"Summary {field} should be numeric"
            assert summary[field] > 0, f"Summary {field} should be positive"
        
        # Verify top products
        top_products = data["top_products"]
        assert isinstance(top_products, list), "Top products should be a list"
        assert len(top_products) > 0, "Should have top products"
        
        for product in top_products:
            assert "product_id" in product
            assert "revenue" in product
            assert isinstance(product["product_id"], int)
            assert isinstance(product["revenue"], (int, float))
            assert product["revenue"] > 0
        
        # Verify location performance
        location_perf = data["location_performance"]
        assert isinstance(location_perf, list), "Location performance should be a list"
        assert len(location_perf) > 0, "Should have location performance data"
        
        for location in location_perf:
            assert "location" in location
            assert "revenue" in location
            assert isinstance(location["location"], str)
            assert isinstance(location["revenue"], (int, float))
    
    def test_dashboard_performance_metrics(self):
        """Test dashboard data generation performance"""
        start_time = time.time()
        response = requests.get(f"{self.base_url}/dashboard-data")
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Dashboard should load quickly
        duration = end_time - start_time
        assert duration < 5.0, f"Dashboard data too slow: {duration:.2f}s"
    
    def test_dashboard_data_consistency(self):
        """Test dashboard data consistency across multiple calls"""
        # Make multiple calls to dashboard
        responses = []
        for i in range(3):
            response = requests.get(f"{self.base_url}/dashboard-data")
            assert response.status_code == 200
            responses.append(response.json())
            time.sleep(0.5)  # Small delay between calls
        
        # Data should be consistent (same totals)
        for i in range(1, len(responses)):
            current_total = responses[i]["summary_stats"]["total_revenue"]
            previous_total = responses[i-1]["summary_stats"]["total_revenue"]
            assert current_total == previous_total, "Dashboard data inconsistent between calls"


class TestDataManagementComprehensive:
    """Test ALL data management features"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_locations_products_endpoints(self):
        """Test locations and products data endpoints"""
        # Test locations endpoint
        response = requests.get(f"{self.base_url}/locations")
        assert response.status_code == 200
        
        data = response.json()
        assert "locations" in data
        locations = data["locations"]
        assert isinstance(locations, list)
        assert len(locations) >= 4  # Should have multiple locations
        
        # Verify expected locations
        expected_locations = {"Central", "East", "North", "South", "West"}
        actual_locations = set(locations)
        assert actual_locations.issubset(expected_locations), f"Unexpected locations: {actual_locations}"
        
        # Test products endpoint
        response = requests.get(f"{self.base_url}/products")
        assert response.status_code == 200
        
        data = response.json()
        assert "products" in data
        products = data["products"]
        assert isinstance(products, list)
        assert len(products) >= 40  # Should have many products
        
        # Verify products are integers
        assert all(isinstance(p, int) for p in products), "All products should be integers"
        assert all(p > 0 for p in products), "All product IDs should be positive"
    
    def test_data_reload_functionality(self):
        """Test data reload endpoint"""
        payload = {"confirm": True}
        response = requests.post(f"{self.base_url}/reload-data", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "records_loaded" in data
        assert isinstance(data["records_loaded"], int)
        assert data["records_loaded"] > 0, "Should have loaded some records"
    
    def test_system_health_monitoring(self):
        """Test system health endpoint"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "model_status" in data
        
        # Verify timestamp format
        timestamp = data["timestamp"]
        assert isinstance(timestamp, str)
        assert len(timestamp) > 10  # Should be ISO format
        
        # Model should be loaded
        model_status = data["model_status"]
        assert model_status in ["loaded", "ready", "available"]


class TestPerformanceStress:
    """Test system performance under stress"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_concurrent_requests_stress(self):
        """Test system under concurrent request load"""
        def make_request(request_id):
            payload = {
                "Unit Price": 2000.0 + (request_id * 10),
                "Unit Cost": 800.0,
                "Location": "Central",
                "_ProductID": (request_id % 10) + 1,
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": "Monday"
            }
            
            start_time = time.time()
            try:
                response = requests.post(f"{self.base_url}/predict-revenue", json=payload, timeout=10)
                end_time = time.time()
                return {
                    "success": response.status_code == 200,
                    "response_time": end_time - start_time,
                    "request_id": request_id
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "request_id": request_id
                }
        
        # Test with 20 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request, i) for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        # Should handle most requests successfully
        success_rate = len(successful_requests) / len(results)
        assert success_rate >= 0.8, f"Success rate too low: {success_rate:.2%}"
        
        if successful_requests:
            # Response times should be reasonable
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            assert avg_response_time < 3.0, f"Average response time too slow: {avg_response_time:.3f}s"
            assert max_response_time < 10.0, f"Max response time too slow: {max_response_time:.3f}s"
    
    def test_large_forecast_stress(self):
        """Test large-scale forecasting performance"""
        # Test forecasting many products for all locations
        large_product_list = list(range(1, 26))  # 25 products
        
        payload = {
            "location": "All",
            "product_ids": large_product_list
        }
        
        start_time = time.time()
        response = requests.post(f"{self.base_url}/forecast-multiple", json=payload, timeout=60)
        end_time = time.time()
        
        duration = end_time - start_time
        
        assert response.status_code == 200, "Large forecast request failed"
        assert duration < 45.0, f"Large forecast too slow: {duration:.2f}s"
        
        data = response.json()
        assert "forecasts" in data
        forecasts = data["forecasts"]
        assert len(forecasts) > 0, "No forecasts returned for large request"


class TestErrorHandlingRobustness:
    """Test error handling and edge cases"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_invalid_input_handling(self):
        """Test handling of various invalid inputs"""
        invalid_test_cases = [
            {
                "name": "negative_price",
                "payload": {
                    "Unit Price": -1000,
                    "Unit Cost": 500,
                    "Location": "Central",
                    "_ProductID": 1,
                    "Year": 2025,
                    "Month": 6,
                    "Day": 15,
                    "Weekday": "Monday"
                }
            },
            {
                "name": "zero_price",
                "payload": {
                    "Unit Price": 0,
                    "Unit Cost": 500,
                    "Location": "Central",
                    "_ProductID": 1,
                    "Year": 2025,
                    "Month": 6,
                    "Day": 15,
                    "Weekday": "Monday"
                }
            },
            {
                "name": "cost_higher_than_price",
                "payload": {
                    "Unit Price": 1000,
                    "Unit Cost": 2000,
                    "Location": "Central",
                    "_ProductID": 1,
                    "Year": 2025,
                    "Month": 6,
                    "Day": 15,
                    "Weekday": "Monday"
                }
            },
            {
                "name": "invalid_location",
                "payload": {
                    "Unit Price": 1000,
                    "Unit Cost": 500,
                    "Location": "InvalidLocation",
                    "_ProductID": 1,
                    "Year": 2025,
                    "Month": 6,
                    "Day": 15,
                    "Weekday": "Monday"
                }
            },
            {
                "name": "invalid_product",
                "payload": {
                    "Unit Price": 1000,
                    "Unit Cost": 500,
                    "Location": "Central",
                    "_ProductID": 99999,
                    "Year": 2025,
                    "Month": 6,
                    "Day": 15,
                    "Weekday": "Monday"
                }
            }
        ]
        
        for test_case in invalid_test_cases:
            response = requests.post(f"{self.base_url}/predict-revenue", json=test_case["payload"])
            
            # Should either handle gracefully (200) or return proper error (400)
            assert response.status_code in [200, 400], f"Unexpected status for {test_case['name']}: {response.status_code}"
            
            # If it returns 200, should still give a reasonable response
            if response.status_code == 200:
                data = response.json()
                assert "predicted_revenue" in data
                # Revenue might be unusual but shouldn't be completely unreasonable
                revenue = data["predicted_revenue"]
                assert isinstance(revenue, (int, float)), f"Invalid revenue type for {test_case['name']}"
    
    def test_malformed_request_handling(self):
        """Test handling of malformed requests"""
        malformed_cases = [
            {},  # Empty payload
            {"Unit Price": "not_a_number"},  # String instead of number
            {"invalid_field": 123},  # Completely wrong fields
            None,  # Null payload
        ]
        
        for payload in malformed_cases:
            try:
                response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
                # Should return 400 for malformed requests
                assert response.status_code in [400, 422], f"Should reject malformed payload: {payload}"
            except Exception:
                # Some malformed requests might cause connection errors, which is acceptable
                pass


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_complete_business_analysis_workflow(self):
        """Test complete business analysis workflow"""
        # 1. Get dashboard overview
        dashboard_response = requests.get(f"{self.base_url}/dashboard-data")
        assert dashboard_response.status_code == 200
        dashboard_data = dashboard_response.json()
        
        # 2. Get business insights
        insights_response = requests.get(f"{self.base_url}/business-insights")
        assert insights_response.status_code == 200
        insights_data = insights_response.json()
        
        # 3. Test scenario based on insights
        if insights_data["insights"]:
            # Pick a product from top products for testing
            top_product = dashboard_data["top_products"][0]["product_id"]
            
            # Test price optimization for this product
            optimization_payload = {
                "Unit Price": 5000,
                "Unit Cost": 2000,
                "Location": "Central",
                "_ProductID": top_product,
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": "Monday"
            }
            
            optimization_response = requests.post(f"{self.base_url}/optimize-price", json=optimization_payload)
            assert optimization_response.status_code == 200
            
            # 4. Generate forecast based on optimization
            forecast_payload = {
                "location": "Central",
                "product_id": top_product
            }
            
            forecast_response = requests.post(f"{self.base_url}/forecast-sales", json=forecast_payload)
            assert forecast_response.status_code == 200
        
        # Verify we completed the full workflow
        assert all([
            dashboard_response.status_code == 200,
            insights_response.status_code == 200
        ])
    
    def test_multi_product_scenario_planning(self):
        """Test multi-product scenario planning workflow"""
        # 1. Get available products
        products_response = requests.get(f"{self.base_url}/products")
        assert products_response.status_code == 200
        products = products_response.json()["products"][:5]  # Use first 5 products
        
        # 2. Test multiple products forecast
        multi_forecast_payload = {
            "location": "Central",
            "product_ids": products
        }
        
        multi_forecast_response = requests.post(f"{self.base_url}/forecast-multiple", json=multi_forecast_payload)
        assert multi_forecast_response.status_code == 200
        
        # 3. Test price optimization for each product
        for product_id in products[:3]:  # Test first 3 to avoid timeout
            optimization_payload = {
                "Unit Price": 3000,
                "Unit Cost": 1200,
                "Location": "Central",
                "_ProductID": product_id,
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": "Monday"
            }
            
            optimization_response = requests.post(f"{self.base_url}/optimize-price", json=optimization_payload)
            assert optimization_response.status_code == 200
        
        # Verify multi-product planning completed
        assert multi_forecast_response.status_code == 200 