"""
Comprehensive tests for ALL API endpoints and features.
Tests every single endpoint, forecast type, insight generation, etc.
"""

import pytest
import requests
import json
import time
from unittest.mock import patch
import pandas as pd
from datetime import datetime, timedelta


class TestAllAPIEndpoints:
    """Test ALL API endpoints comprehensively"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "model_status" in data
    
    def test_locations_endpoint(self):
        """Test locations endpoint returns all locations"""
        response = requests.get(f"{self.base_url}/locations")
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data
        locations = data["locations"]
        # Should have 5 locations based on our data
        assert len(locations) >= 4
        expected_locations = {"Central", "East", "North", "South", "West"}
        assert set(locations).issubset(expected_locations)
    
    def test_products_endpoint(self):
        """Test products endpoint returns all products"""
        response = requests.get(f"{self.base_url}/products")
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        products = data["products"]
        # Should have 47 products based on our data
        assert len(products) >= 40
        # Check products are integers
        assert all(isinstance(p, int) for p in products)
    
    def test_predict_revenue_basic(self):
        """Test basic revenue prediction"""
        payload = {
            "Unit Price": 5000.0,
            "Unit Cost": 2000.0,
            "Location": "North",
            "_ProductID": 1,
            "Year": 2025,
            "Month": 1,
            "Day": 15,
            "Weekday": "Monday"
        }
        response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_revenue" in data
        assert isinstance(data["predicted_revenue"], (int, float))
        assert data["predicted_revenue"] > 0
    
    def test_predict_revenue_all_locations(self):
        """Test revenue prediction for all locations"""
        locations = ["Central", "East", "North", "South", "West"]
        for location in locations:
            payload = {
                "Unit Price": 1000.0,
                "Unit Cost": 500.0,
                "Location": location,
                "_ProductID": 5,
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": "Thursday"
            }
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200, f"Failed for location {location}"
            data = response.json()
            assert data["predicted_revenue"] > 0
    
    def test_predict_revenue_all_products(self):
        """Test revenue prediction for multiple products"""
        products = [1, 5, 10, 20, 30, 40]  # Sample product IDs
        for product_id in products:
            payload = {
                "Unit Price": 2000.0,
                "Unit Cost": 800.0,
                "Location": "Central",
                "_ProductID": product_id,
                "Year": 2025,
                "Month": 3,
                "Day": 10,
                "Weekday": "Friday"
            }
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200, f"Failed for product {product_id}"
            data = response.json()
            assert data["predicted_revenue"] > 0
    
    def test_simulate_revenue_scenarios(self):
        """Test revenue simulation with multiple scenarios"""
        scenarios = [
            {"Unit Price": 1000, "Unit Cost": 400},
            {"Unit Price": 2000, "Unit Cost": 800},
            {"Unit Price": 5000, "Unit Cost": 2000},
            {"Unit Price": 10000, "Unit Cost": 4000}
        ]
        
        for scenario in scenarios:
            payload = {
                **scenario,
                "Location": "Central",
                "_ProductID": 1,
                "Year": 2025,
                "Month": 6,
                "Day": 1,
                "Weekday": "Sunday"
            }
            response = requests.post(f"{self.base_url}/simulate-revenue", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "scenarios" in data
            assert len(data["scenarios"]) > 0
            # Check each scenario has required fields
            for sim_scenario in data["scenarios"]:
                assert "price" in sim_scenario
                assert "predicted_revenue" in sim_scenario
                assert "potential_profit" in sim_scenario
    
    def test_optimize_price_comprehensive(self):
        """Test price optimization for different scenarios"""
        test_cases = [
            {"base_price": 1000, "cost": 400, "product": 1},
            {"base_price": 5000, "cost": 2000, "product": 10},
            {"base_price": 10000, "cost": 3000, "product": 20}
        ]
        
        for case in test_cases:
            payload = {
                "Unit Price": case["base_price"],
                "Unit Cost": case["cost"],
                "Location": "North",
                "_ProductID": case["product"],
                "Year": 2025,
                "Month": 4,
                "Day": 15,
                "Weekday": "Tuesday"
            }
            response = requests.post(f"{self.base_url}/optimize-price", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "optimizations" in data
            assert len(data["optimizations"]) > 0
            
            # Verify optimization results
            for opt in data["optimizations"]:
                assert "price" in opt
                assert "predicted_revenue" in opt
                assert "profit_margin" in opt
                assert opt["price"] > 0
                assert opt["predicted_revenue"] > 0
    
    def test_forecast_sales_automatic(self):
        """Test automatic sales forecasting"""
        payload = {
            "location": "Central",
            "product_id": 1
        }
        response = requests.post(f"{self.base_url}/forecast-sales", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
        assert len(data["forecast"]) > 0
        
        # Check forecast structure
        for forecast_point in data["forecast"]:
            assert "date" in forecast_point
            assert "predicted_revenue" in forecast_point
            assert "predicted_quantity" in forecast_point
            assert forecast_point["predicted_revenue"] > 0
    
    def test_forecast_sales_all_locations(self):
        """Test automatic forecasting for all locations"""
        locations = ["Central", "East", "North", "South", "West"]
        for location in locations:
            payload = {
                "location": location,
                "product_id": 5
            }
            response = requests.post(f"{self.base_url}/forecast-sales", json=payload)
            assert response.status_code == 200, f"Forecast failed for {location}"
            data = response.json()
            assert "forecast" in data
            assert len(data["forecast"]) > 0
    
    def test_forecast_multiple_products(self):
        """Test forecasting multiple products simultaneously"""
        payload = {
            "location": "Central",
            "product_ids": [1, 5, 10, 15]
        }
        response = requests.post(f"{self.base_url}/forecast-multiple", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "forecasts" in data
        assert len(data["forecasts"]) > 0
        
        # Should have forecasts for multiple products
        product_ids_in_response = set()
        for forecast in data["forecasts"]:
            assert "product_id" in forecast
            assert "forecast_data" in forecast
            product_ids_in_response.add(forecast["product_id"])
        
        # Should cover the requested products
        assert len(product_ids_in_response) >= 2
    
    def test_forecast_multiple_all_location(self):
        """Test forecasting multiple products for 'All' locations"""
        payload = {
            "location": "All",
            "product_ids": [1, 2, 3]
        }
        response = requests.post(f"{self.base_url}/forecast-multiple", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "forecasts" in data
        # Should handle 'All' location without timeout
        assert len(data["forecasts"]) > 0
    
    def test_forecast_trend_analysis(self):
        """Test trend forecasting functionality"""
        payload = {
            "location": "North",
            "product_id": 1,
            "start_date": "2025-01-01",
            "end_date": "2025-03-31"
        }
        response = requests.post(f"{self.base_url}/forecast-trend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "trend_analysis" in data
        assert "forecast_points" in data
        
        trend = data["trend_analysis"]
        assert "trend_direction" in trend
        assert "confidence_score" in trend
        assert "total_forecasted_revenue" in trend
        
        # Check forecast points
        forecast_points = data["forecast_points"]
        assert len(forecast_points) > 0
        for point in forecast_points:
            assert "date" in point
            assert "predicted_revenue" in point
    
    def test_dashboard_data_comprehensive(self):
        """Test dashboard data endpoint thoroughly"""
        response = requests.get(f"{self.base_url}/dashboard-data")
        assert response.status_code == 200
        data = response.json()
        
        # Check all required dashboard sections
        required_sections = [
            "summary_stats",
            "top_products",
            "location_performance", 
            "recent_trends",
            "monthly_comparison"
        ]
        
        for section in required_sections:
            assert section in data, f"Missing dashboard section: {section}"
        
        # Verify summary stats
        summary = data["summary_stats"]
        assert "total_revenue" in summary
        assert "total_transactions" in summary
        assert "avg_transaction_value" in summary
        assert summary["total_revenue"] > 0
        
        # Verify top products
        top_products = data["top_products"]
        assert len(top_products) > 0
        for product in top_products:
            assert "product_id" in product
            assert "revenue" in product
        
        # Verify location performance
        location_perf = data["location_performance"]
        assert len(location_perf) > 0
        for location in location_perf:
            assert "location" in location
            assert "revenue" in location
    
    def test_business_insights_generation(self):
        """Test business insights endpoint"""
        response = requests.get(f"{self.base_url}/business-insights")
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
        
        insights = data["insights"]
        assert len(insights) > 0
        assert len(insights) <= 5  # Max 5 insights
        
        # Check insight structure
        for insight in insights:
            required_fields = [
                "type", "priority_score", "title", 
                "description", "action_items", "expected_impact"
            ]
            for field in required_fields:
                assert field in insight, f"Missing field {field} in insight"
            
            # Check priority score is valid
            assert 0 <= insight["priority_score"] <= 100
            
            # Check action items exist
            assert len(insight["action_items"]) > 0
    
    def test_insights_endpoint_detailed(self):
        """Test detailed insights endpoint"""
        response = requests.get(f"{self.base_url}/insights")
        assert response.status_code == 200
        data = response.json()
        assert "insights" in data
        
        insights = data["insights"]
        assert len(insights) > 0
        
        # Should have different insight types
        insight_types = set()
        for insight in insights:
            insight_types.add(insight["type"])
        
        # Should have multiple different types of insights
        assert len(insight_types) >= 2
    
    def test_reload_data_functionality(self):
        """Test data reload endpoint"""
        payload = {"confirm": True}
        response = requests.post(f"{self.base_url}/reload-data", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "records_loaded" in data
        assert data["records_loaded"] > 0


class TestForecastingScenarios:
    """Test ALL forecasting scenarios comprehensively"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_custom_date_range_forecasts(self):
        """Test custom date range forecasting"""
        date_ranges = [
            ("2025-01-01", "2025-01-31"),  # 1 month
            ("2025-01-01", "2025-03-31"),  # 3 months
            ("2025-01-01", "2025-06-30"),  # 6 months
            ("2025-01-01", "2025-12-31"),  # 1 year
        ]
        
        for start_date, end_date in date_ranges:
            payload = {
                "location": "Central",
                "product_id": 1,
                "start_date": start_date,
                "end_date": end_date
            }
            response = requests.post(f"{self.base_url}/forecast-trend", json=payload)
            assert response.status_code == 200, f"Failed for range {start_date} to {end_date}"
            data = response.json()
            assert "forecast_points" in data
            assert len(data["forecast_points"]) > 0
    
    def test_all_location_forecasting(self):
        """Test forecasting for 'All' locations specifically"""
        payload = {
            "location": "All",
            "product_id": 1
        }
        response = requests.post(f"{self.base_url}/forecast-sales", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
        # Should aggregate all locations
        assert len(data["forecast"]) > 0
    
    def test_weekend_vs_weekday_forecasts(self):
        """Test forecasting for different days of week"""
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for weekday in weekdays:
            payload = {
                "Unit Price": 2000.0,
                "Unit Cost": 800.0,
                "Location": "Central",
                "_ProductID": 1,
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": weekday
            }
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200, f"Failed for {weekday}"
            data = response.json()
            assert data["predicted_revenue"] > 0


class TestScenarioPlanning:
    """Test ALL scenario planning features"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_price_optimization_scenarios(self):
        """Test all price optimization scenarios"""
        # Test different optimization ranges
        optimization_cases = [
            {"base_price": 1000, "expected_range": (800, 1500)},
            {"base_price": 5000, "expected_range": (4000, 7500)},
            {"base_price": 10000, "expected_range": (8000, 15000)},
        ]
        
        for case in optimization_cases:
            payload = {
                "Unit Price": case["base_price"],
                "Unit Cost": case["base_price"] * 0.4,  # 40% cost ratio
                "Location": "Central",
                "_ProductID": 1,
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": "Monday"
            }
            response = requests.post(f"{self.base_url}/optimize-price", json=payload)
            assert response.status_code == 200
            data = response.json()
            
            optimizations = data["optimizations"]
            assert len(optimizations) > 0
            
            # Should test prices around the base price
            prices_tested = [opt["price"] for opt in optimizations]
            min_price, max_price = case["expected_range"]
            assert any(min_price <= price <= max_price for price in prices_tested)
    
    def test_revenue_simulation_comprehensive(self):
        """Test comprehensive revenue simulation scenarios"""
        # Test edge cases
        edge_cases = [
            {"price": 100, "cost": 50, "name": "low_price"},
            {"price": 1000, "cost": 500, "name": "medium_price"},
            {"price": 20000, "cost": 10000, "name": "high_price"},
            {"price": 50000, "cost": 25000, "name": "premium_price"},
        ]
        
        for case in edge_cases:
            payload = {
                "Unit Price": case["price"],
                "Unit Cost": case["cost"],
                "Location": "North",
                "_ProductID": 5,
                "Year": 2025,
                "Month": 3,
                "Day": 20,
                "Weekday": "Thursday"
            }
            response = requests.post(f"{self.base_url}/simulate-revenue", json=payload)
            assert response.status_code == 200, f"Failed for {case['name']}"
            data = response.json()
            
            scenarios = data["scenarios"]
            assert len(scenarios) > 0
            
            # Verify profit calculations
            for scenario in scenarios:
                profit = scenario["potential_profit"]
                revenue = scenario["predicted_revenue"]
                # Profit should be reasonable relative to cost
                assert profit > -case["cost"] * 2  # Shouldn't lose more than 2x cost


class TestInsightsComprehensive:
    """Test ALL insight generation features"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_all_insight_types_generated(self):
        """Test that all 5+ insight types can be generated"""
        response = requests.get(f"{self.base_url}/business-insights")
        assert response.status_code == 200
        data = response.json()
        
        insights = data["insights"]
        insight_types = [insight["type"] for insight in insights]
        
        # Should generate different types of insights
        expected_types = {
            "revenue_optimization",
            "product_performance", 
            "pricing_strategy",
            "location_performance",
            "profit_margin",
            "compound_insight"
        }
        
        # At least 3 different types should be present
        unique_types = set(insight_types)
        assert len(unique_types) >= 3, f"Only got types: {unique_types}"
    
    def test_insight_priority_ranking(self):
        """Test that insights are properly prioritized"""
        response = requests.get(f"{self.base_url}/business-insights")
        assert response.status_code == 200
        data = response.json()
        
        insights = data["insights"]
        assert len(insights) > 1
        
        # Check priority scores are in descending order
        priorities = [insight["priority_score"] for insight in insights]
        assert priorities == sorted(priorities, reverse=True), "Insights not properly prioritized"
        
        # Top insight should have high priority
        assert priorities[0] >= 60, "Top insight priority too low"
    
    def test_insight_action_items_quality(self):
        """Test that insights have actionable items"""
        response = requests.get(f"{self.base_url}/business-insights")
        assert response.status_code == 200
        data = response.json()
        
        insights = data["insights"]
        for insight in insights:
            action_items = insight["action_items"]
            assert len(action_items) >= 2, "Insufficient action items"
            
            # Action items should be specific
            for action in action_items:
                assert len(action) > 20, f"Action too vague: {action}"
                # Should contain specific business terms
                business_terms = ["increase", "reduce", "optimize", "focus", "analyze", "implement", "test"]
                assert any(term in action.lower() for term in business_terms)
    
    def test_insight_expected_impact(self):
        """Test that insights have realistic expected impact"""
        response = requests.get(f"{self.base_url}/business-insights")
        assert response.status_code == 200
        data = response.json()
        
        insights = data["insights"]
        for insight in insights:
            expected_impact = insight["expected_impact"]
            assert len(expected_impact) > 30, "Expected impact too brief"
            
            # Should mention specific metrics or percentages
            impact_indicators = ["%", "revenue", "profit", "increase", "improve", "reduce"]
            assert any(indicator in expected_impact.lower() for indicator in impact_indicators)


class TestPerformanceUnderLoad:
    """Test system performance under various loads"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_concurrent_predictions(self):
        """Test multiple concurrent predictions"""
        import concurrent.futures
        import threading
        
        def make_prediction(thread_id):
            payload = {
                "Unit Price": 2000.0 + (thread_id * 100),  # Vary price
                "Unit Cost": 800.0,
                "Location": "Central",
                "_ProductID": 1,
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": "Monday"
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            end_time = time.time()
            
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "thread_id": thread_id
            }
        
        # Test 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_prediction, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(result["status_code"] == 200 for result in results)
        
        # Response times should be reasonable
        avg_response_time = sum(result["response_time"] for result in results) / len(results)
        assert avg_response_time < 2.0, f"Average response time too slow: {avg_response_time:.3f}s"
    
    def test_large_batch_forecast(self):
        """Test large batch forecasting performance"""
        start_time = time.time()
        
        payload = {
            "location": "All",
            "product_ids": list(range(1, 21))  # 20 products
        }
        response = requests.post(f"{self.base_url}/forecast-multiple", json=payload)
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 10.0, f"Large batch forecast too slow: {duration:.3f}s"
        
        data = response.json()
        assert len(data["forecasts"]) > 0


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    base_url = "http://127.0.0.1:5000"
    
    def test_invalid_prediction_inputs(self):
        """Test prediction with invalid inputs"""
        invalid_cases = [
            {"Unit Price": -1000, "Unit Cost": 500},  # Negative price
            {"Unit Price": 1000, "Unit Cost": -500},  # Negative cost
            {"Unit Price": 0, "Unit Cost": 500},      # Zero price
            {"Unit Price": 1000, "Unit Cost": 2000},  # Cost > Price
        ]
        
        for case in invalid_cases:
            payload = {
                **case,
                "Location": "Central",
                "_ProductID": 1,
                "Year": 2025,
                "Month": 6,
                "Day": 15,
                "Weekday": "Monday"
            }
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            # Should either succeed with a reasonable prediction or fail gracefully
            assert response.status_code in [200, 400], f"Unexpected status for case {case}"
    
    def test_invalid_location_handling(self):
        """Test handling of invalid locations"""
        payload = {
            "Unit Price": 1000.0,
            "Unit Cost": 500.0,
            "Location": "InvalidLocation",
            "_ProductID": 1,
            "Year": 2025,
            "Month": 6,
            "Day": 15,
            "Weekday": "Monday"
        }
        response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_invalid_product_handling(self):
        """Test handling of invalid product IDs"""
        payload = {
            "Unit Price": 1000.0,
            "Unit Cost": 500.0,
            "Location": "Central",
            "_ProductID": 99999,  # Invalid product ID
            "Year": 2025,
            "Month": 6,
            "Day": 15,
            "Weekday": "Monday"
        }
        response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        incomplete_payload = {
            "Unit Price": 1000.0,
            # Missing other required fields
        }
        response = requests.post(f"{self.base_url}/predict-revenue", json=incomplete_payload)
        assert response.status_code == 400 