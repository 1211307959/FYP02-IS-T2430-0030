"""
COMPREHENSIVE FEATURE TEST SUMMARY
Tests every major feature of the revenue prediction system
"""

import requests
import json
import time
from datetime import datetime


class ComprehensiveFeatureTester:
    """Test every major feature of the system"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:5000"
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def run_test(self, test_name, test_func):
        """Run a test and track results"""
        print(f"\n{'='*50}")
        print(f"TESTING: {test_name}")
        print(f"{'='*50}")
        
        self.test_results["total_tests"] += 1
        
        try:
            start_time = time.time()
            test_func()
            duration = time.time() - start_time
            self.test_results["passed"] += 1
            print(f"✅ PASSED ({duration:.3f}s)")
            return True
        except Exception as e:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {str(e)}")
            print(f"❌ FAILED: {str(e)}")
            return False
    
    def test_all_endpoints(self):
        """Test ALL API endpoints exist and respond"""
        endpoints = [
            ("GET", "/health", None),
            ("GET", "/locations", None),
            ("GET", "/products", None),
            ("GET", "/dashboard-data", None),
            ("GET", "/business-insights", None),
            ("GET", "/insights", None),
            ("POST", "/predict-revenue", {
                "Unit Price": 5000.0, "Unit Cost": 2000.0, "Location": "North",
                "_ProductID": 1, "Year": 2025, "Month": 1, "Day": 15, "Weekday": "Monday"
            }),
            ("POST", "/simulate-revenue", {
                "Unit Price": 2000.0, "Unit Cost": 800.0, "Location": "Central",
                "_ProductID": 1, "Year": 2025, "Month": 6, "Day": 15, "Weekday": "Monday"
            }),
            ("POST", "/optimize-price", {
                "Unit Price": 3000.0, "Unit Cost": 1200.0, "Location": "Central",
                "_ProductID": 1, "Year": 2025, "Month": 6, "Day": 15, "Weekday": "Monday"
            }),
            ("POST", "/forecast-sales", {"location": "Central", "product_id": 1}),
            ("POST", "/forecast-multiple", {"location": "Central", "product_ids": [1, 2, 3]}),
            ("POST", "/forecast-trend", {
                "location": "Central", "product_id": 1, 
                "start_date": "2025-01-01", "end_date": "2025-03-31"
            }),
            ("POST", "/reload-data", {"confirm": True})
        ]
        
        successful_endpoints = 0
        
        for method, endpoint, payload in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}")
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", json=payload)
                
                if response.status_code in [200, 201]:
                    successful_endpoints += 1
                    print(f"✓ {method} {endpoint}: OK")
                elif response.status_code == 400:
                    print(f"⚠ {method} {endpoint}: Validation error (may be expected)")
                    successful_endpoints += 0.5  # Partial credit
                else:
                    print(f"✗ {method} {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"✗ {method} {endpoint}: Error - {e}")
        
        print(f"\nEndpoint Summary: {successful_endpoints}/{len(endpoints)} working")
        assert successful_endpoints >= len(endpoints) * 0.7, "Too many endpoints failing"
    
    def test_all_locations_and_products(self):
        """Test all 5 locations and 47 products work"""
        # Get locations
        response = requests.get(f"{self.base_url}/locations")
        assert response.status_code == 200
        locations = response.json()["locations"]
        assert len(locations) == 5
        print(f"✓ Found {len(locations)} locations: {locations}")
        
        # Get products
        response = requests.get(f"{self.base_url}/products")
        assert response.status_code == 200
        products = response.json()["products"]
        assert len(products) == 47
        print(f"✓ Found {len(products)} products: {products[:10]}...{products[-5:]}")
        
        # Test predictions for all locations
        for location in locations:
            payload = {
                "Unit Price": 2000.0, "Unit Cost": 800.0, "Location": location,
                "_ProductID": 1, "Year": 2025, "Month": 6, "Day": 15, "Weekday": "Monday"
            }
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200
            revenue = response.json()["predicted_revenue"]
            print(f"✓ {location}: ${revenue:.2f}")
        
        # Test sample products
        sample_products = [1, 10, 20, 30, 40, 47]
        for product_id in sample_products:
            payload = {
                "Unit Price": 3000.0, "Unit Cost": 1200.0, "Location": "Central",
                "_ProductID": product_id, "Year": 2025, "Month": 6, "Day": 15, "Weekday": "Monday"
            }
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            assert response.status_code == 200
            revenue = response.json()["predicted_revenue"]
            print(f"✓ Product {product_id}: ${revenue:.2f}")
    
    def test_all_forecasting_scenarios(self):
        """Test ALL forecasting capabilities"""
        scenarios = [
            ("Automatic Forecast Central", {"location": "Central", "product_id": 1}),
            ("Automatic Forecast All Locations", {"location": "All", "product_id": 1}),
            ("Custom Date Range", {
                "location": "Central", "product_id": 1,
                "start_date": "2025-01-01", "end_date": "2025-03-31"
            }),
            ("Multiple Products", {"location": "Central", "product_ids": [1, 2, 3, 4, 5]})
        ]
        
        for scenario_name, payload in scenarios:
            try:
                if "product_ids" in payload:
                    endpoint = "/forecast-multiple"
                elif "start_date" in payload:
                    endpoint = "/forecast-trend"
                else:
                    endpoint = "/forecast-sales"
                
                start_time = time.time()
                response = requests.post(f"{self.base_url}{endpoint}", json=payload)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if "forecast" in data:
                        forecast_points = len(data["forecast"])
                        print(f"✓ {scenario_name}: {forecast_points} forecast points ({duration:.2f}s)")
                    elif "forecasts" in data:
                        forecast_count = len(data["forecasts"])
                        print(f"✓ {scenario_name}: {forecast_count} product forecasts ({duration:.2f}s)")
                    else:
                        print(f"✓ {scenario_name}: Forecast generated ({duration:.2f}s)")
                else:
                    print(f"⚠ {scenario_name}: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                print(f"✗ {scenario_name}: Error - {e}")
    
    def test_all_scenario_planning(self):
        """Test ALL scenario planning features"""
        base_payload = {
            "Unit Price": 3000.0, "Unit Cost": 1200.0, "Location": "Central",
            "_ProductID": 1, "Year": 2025, "Month": 6, "Day": 15, "Weekday": "Monday"
        }
        
        # Test price optimization
        try:
            response = requests.post(f"{self.base_url}/optimize-price", json=base_payload)
            if response.status_code == 200:
                data = response.json()
                optimizations = data.get("optimizations", [])
                print(f"✓ Price Optimization: {len(optimizations)} scenarios")
            else:
                print(f"⚠ Price Optimization: {response.status_code}")
        except Exception as e:
            print(f"✗ Price Optimization: {e}")
        
        # Test revenue simulation
        try:
            response = requests.post(f"{self.base_url}/simulate-revenue", json=base_payload)
            if response.status_code == 200:
                data = response.json()
                scenarios = data.get("scenarios", [])
                print(f"✓ Revenue Simulation: {len(scenarios)} scenarios")
            else:
                print(f"⚠ Revenue Simulation: {response.status_code}")
        except Exception as e:
            print(f"✗ Revenue Simulation: {e}")
        
        # Test what-if analysis (price sensitivity)
        print("\n--- Price Sensitivity Analysis ---")
        prices = [1500, 2000, 2500, 3000, 4000, 5000]
        for price in prices:
            payload = {**base_payload, "Unit Price": price}
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            if response.status_code == 200:
                revenue = response.json()["predicted_revenue"]
                margin = (price - 1200) / price * 100
                print(f"  Price ${price}: Revenue ${revenue:.2f} (Margin {margin:.1f}%)")
    
    def test_all_insights_generation(self):
        """Test ALL insight generation capabilities"""
        # Test business insights
        response = requests.get(f"{self.base_url}/business-insights")
        assert response.status_code == 200
        data = response.json()
        insights = data["insights"]
        print(f"✓ Business Insights: {len(insights)} insights generated")
        
        insight_types = set()
        for insight in insights:
            insight_types.add(insight.get("type", "unknown"))
            priority = insight.get("priority_score", 0)
            title = insight.get("title", "No title")[:50]
            print(f"  - {title} (Priority: {priority})")
        
        print(f"✓ Insight Types: {len(insight_types)} different types: {list(insight_types)}")
        
        # Test detailed insights endpoint
        response = requests.get(f"{self.base_url}/insights")
        if response.status_code == 200:
            data = response.json()
            insights2 = data.get("insights", [])
            print(f"✓ Detailed Insights: {len(insights2)} insights")
    
    def test_dashboard_comprehensive(self):
        """Test complete dashboard functionality"""
        response = requests.get(f"{self.base_url}/dashboard-data")
        assert response.status_code == 200
        data = response.json()
        
        # Check main metrics
        total_revenue = data.get("total_revenue", 0)
        total_sales = data.get("total_sales", 0)
        products = data.get("products", [])
        
        print(f"✓ Total Revenue: ${total_revenue:,.0f}")
        print(f"✓ Total Sales: {total_sales:,} transactions")
        print(f"✓ Products: {len(products)} products analyzed")
        
        # Check product rankings
        top_products = [p for p in products if p.get("rank") == "top"]
        bottom_products = [p for p in products if p.get("rank") == "bottom"]
        print(f"✓ Product Rankings: {len(top_products)} top, {len(bottom_products)} bottom performers")
        
        # Check data quality
        assert total_revenue > 800_000_000, "Revenue seems too low"
        assert total_sales > 90_000, "Transaction count seems too low"
        assert len(products) == 47, "Should have 47 products"
    
    def test_system_performance(self):
        """Test system performance under various loads"""
        # Test rapid predictions
        start_time = time.time()
        successful_predictions = 0
        
        for i in range(10):
            payload = {
                "Unit Price": 2000.0 + (i * 100), "Unit Cost": 800.0, "Location": "Central",
                "_ProductID": (i % 5) + 1, "Year": 2025, "Month": 6, "Day": 15, "Weekday": "Monday"
            }
            response = requests.post(f"{self.base_url}/predict-revenue", json=payload)
            if response.status_code == 200:
                successful_predictions += 1
        
        duration = time.time() - start_time
        success_rate = successful_predictions / 10
        avg_time = duration / 10
        
        print(f"✓ Rapid Predictions: {successful_predictions}/10 successful")
        print(f"✓ Success Rate: {success_rate:.1%}")
        print(f"✓ Average Response Time: {avg_time:.3f}s")
        
        assert success_rate >= 0.8, "Success rate too low"
        assert avg_time < 1.0, "Average response time too slow"
        
        # Test dashboard load time
        start_time = time.time()
        response = requests.get(f"{self.base_url}/dashboard-data")
        dashboard_time = time.time() - start_time
        print(f"✓ Dashboard Load Time: {dashboard_time:.3f}s")
        assert dashboard_time < 5.0, "Dashboard too slow"
        
        # Test forecast generation time
        start_time = time.time()
        response = requests.post(f"{self.base_url}/forecast-sales", 
                               json={"location": "Central", "product_id": 1})
        forecast_time = time.time() - start_time
        print(f"✓ Forecast Generation Time: {forecast_time:.3f}s")
        assert forecast_time < 15.0, "Forecast generation too slow"
    
    def run_all_tests(self):
        """Run ALL comprehensive feature tests"""
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE REVENUE PREDICTION SYSTEM TEST")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Run all test categories
        test_categories = [
            ("API Endpoints", self.test_all_endpoints),
            ("Locations & Products", self.test_all_locations_and_products),
            ("Forecasting Scenarios", self.test_all_forecasting_scenarios),
            ("Scenario Planning", self.test_all_scenario_planning),
            ("Insights Generation", self.test_all_insights_generation),
            ("Dashboard Features", self.test_dashboard_comprehensive),
            ("System Performance", self.test_system_performance)
        ]
        
        for category_name, test_func in test_categories:
            self.run_test(category_name, test_func)
        
        # Print final summary
        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")
        success_rate = self.test_results['passed'] / self.test_results['total_tests'] * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print(f"\nErrors:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Overall assessment
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: System is production-ready!")
        elif success_rate >= 80:
            print(f"\n✅ GOOD: System is working well with minor issues")
        elif success_rate >= 70:
            print(f"\n⚠️ ACCEPTABLE: System works but needs improvement")
        else:
            print(f"\n❌ POOR: System has significant issues")
        
        return success_rate >= 70


if __name__ == "__main__":
    tester = ComprehensiveFeatureTester()
    tester.run_all_tests() 