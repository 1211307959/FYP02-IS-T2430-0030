import json
import time
import pandas as pd
import sys
import requests
from revenue_predictor_50_50 import predict_revenue, simulate_price_variations, optimize_price

class ModelIntegrationTest:
    def __init__(self):
        self.test_cases = [
            {
                "name": "Standard Product",
                "input": {
                    'Unit Price': 100,
                    'Unit Cost': 50,
                    'Month': 6,
                    'Day': 15,
                    'Weekday': 'Friday',
                    'Location': 'North',
                    '_ProductID': '12',
                    'Year': 2023
                }
            },
            {
                "name": "Premium Product",
                "input": {
                    'Unit Price': 250,
                    'Unit Cost': 100,
                    'Month': 6,
                    'Day': 15,
                    'Weekday': 'Friday',
                    'Location': 'North',
                    '_ProductID': '13',
                    'Year': 2023
                }
            },
            {
                "name": "String Inputs",
                "input": {
                    'Unit Price': "100",
                    'Unit Cost': "50",
                    'Month': "6",
                    'Day': "15",
                    'Weekday': "Friday",
                    'Location': "North",
                    '_ProductID': "12",
                    'Year': "2023"
                }
            },
            {
                "name": "Invalid Month",
                "input": {
                    'Unit Price': 100,
                    'Unit Cost': 50,
                    'Month': 13,  # Invalid month
                    'Day': 15,
                    'Weekday': 'Friday',
                    'Location': 'North',
                    '_ProductID': '12',
                    'Year': 2023
                }
            },
            {
                "name": "Invalid Day",
                "input": {
                    'Unit Price': 100,
                    'Unit Cost': 50,
                    'Month': 6,
                    'Day': 32,  # Invalid day
                    'Weekday': 'Friday',
                    'Location': 'North',
                    '_ProductID': '12',
                    'Year': 2023
                }
            },
            {
                "name": "Negative Price",
                "input": {
                    'Unit Price': -100,  # Invalid price
                    'Unit Cost': 50,
                    'Month': 6,
                    'Day': 15,
                    'Weekday': 'Friday',
                    'Location': 'North',
                    '_ProductID': '12',
                    'Year': 2023
                }
            },
            {
                "name": "Cost Greater Than Price",
                "input": {
                    'Unit Price': 50,
                    'Unit Cost': 100,  # Cost > Price
                    'Month': 6,
                    'Day': 15,
                    'Weekday': 'Friday',
                    'Location': 'North',
                    '_ProductID': '12',
                    'Year': 2023
                }
            }
        ]
        
    def run_prediction_tests(self):
        """Test basic prediction functionality with different inputs"""
        print("\n===== PREDICTION TESTS =====\n")
        
        results = []
        for case in self.test_cases:
            print(f"Testing: {case['name']}")
            start_time = time.time()
            
            try:
                result = predict_revenue(case['input'])
                duration = time.time() - start_time
                
                if 'error' in result:
                    print(f"  ❌ Error: {result['error']}")
                    case_result = {
                        "test_case": case['name'],
                        "status": "error",
                        "error": result['error']
                    }
                else:
                    print(f"  Revenue: ${result['predicted_revenue']:.2f}")
                    print(f"  Quantity: {result['estimated_quantity']}")
                    print(f"  Profit: ${result['profit']:.2f}")
                    print(f"  Duration: {duration:.4f} seconds")
                    
                    case_result = {
                        "test_case": case['name'],
                        "status": "success",
                        "result": result,
                        "duration": duration
                    }
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                case_result = {
                    "test_case": case['name'],
                    "status": "error",
                    "error": str(e)
                }
            
            results.append(case_result)
            print()
            
        return results
    
    def test_input_validation(self):
        """Test how the model handles invalid or missing inputs"""
        print("\n===== INPUT VALIDATION TESTS =====\n")
        
        validation_tests = [
            {
                "name": "Missing Unit Price",
                "input": {
                    'Unit Cost': 50,
                    'Month': 6,
                    'Day': 15,
                    'Weekday': 'Friday',
                    'Location': 'North',
                    '_ProductID': '12',
                    'Year': 2023
                }
            },
            {
                "name": "Missing Month",
                "input": {
                    'Unit Price': 100,
                    'Unit Cost': 50,
                    'Day': 15,
                    'Weekday': 'Friday',
                    'Location': 'North',
                    '_ProductID': '12',
                    'Year': 2023
                }
            },
            {
                "name": "Invalid Location",
                "input": {
                    'Unit Price': 100,
                    'Unit Cost': 50,
                    'Month': 6,
                    'Day': 15,
                    'Weekday': 'Friday',
                    'Location': 'Unknown',
                    '_ProductID': '12',
                    'Year': 2023
                }
            },
            {
                "name": "Invalid Product ID",
                "input": {
                    'Unit Price': 100,
                    'Unit Cost': 50,
                    'Month': 6,
                    'Day': 15,
                    'Weekday': 'Friday',
                    'Location': 'North',
                    '_ProductID': '9999',
                    'Year': 2023
                }
            },
            {
                "name": "Invalid Weekday",
                "input": {
                    'Unit Price': 100,
                    'Unit Cost': 50,
                    'Month': 6,
                    'Day': 15,
                    'Weekday': 'InvalidDay',
                    'Location': 'North',
                    '_ProductID': '12',
                    'Year': 2023
                }
            }
        ]
        
        results = []
        for case in validation_tests:
            print(f"Testing: {case['name']}")
            
            try:
                result = predict_revenue(case['input'])
                
                if 'error' in result:
                    print(f"  ✅ Expected error: {result['error']}")
                    case_result = {
                        "test_case": case['name'],
                        "status": "success",
                        "error": result['error']
                    }
                else:
                    print(f"  ❌ Unexpected success: {result}")
                    case_result = {
                        "test_case": case['name'],
                        "status": "error",
                        "message": "Expected validation error but got success"
                    }
            except Exception as e:
                print(f"  ✅ Expected error: {str(e)}")
                case_result = {
                    "test_case": case['name'],
                    "status": "success",
                    "error": str(e)
                }
            
            results.append(case_result)
            print()
            
        return results
    
    def test_performance(self):
        """Test model performance with multiple predictions"""
        print("\n===== PERFORMANCE TEST =====\n")
        
        # Use standard test case
        test_input = self.test_cases[0]['input']
        
        num_predictions = 100
        print(f"Making {num_predictions} predictions...")
        
        start_time = time.time()
        errors = 0
        
        for _ in range(num_predictions):
            result = predict_revenue(test_input)
            if 'error' in result:
                errors += 1
            
        total_time = time.time() - start_time
        avg_time = total_time / num_predictions
        
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Average prediction time: {avg_time:.4f} seconds")
        print(f"Errors: {errors}")
        
        return {
            "num_predictions": num_predictions,
            "total_time": total_time,
            "avg_time": avg_time,
            "errors": errors
        }
    
    def test_batch_predictions(self):
        """Test making predictions on a batch of inputs"""
        print("\n===== BATCH PREDICTION TEST =====\n")
        
        # Create batch of 10 test cases with varying prices
        batch_inputs = []
        for price in range(50, 550, 50):
            batch_inputs.append({
                'Unit Price': price,
                'Unit Cost': price * 0.5,
                'Month': 6,
                'Day': 15,
                'Weekday': 'Friday',
                'Location': 'North',
                '_ProductID': '12',
                'Year': 2023
            })
        
        print(f"Processing batch of {len(batch_inputs)} inputs...")
        
        start_time = time.time()
        batch_results = []
        errors = 0
        
        for input_data in batch_inputs:
            result = predict_revenue(input_data)
            if 'error' in result:
                errors += 1
            batch_results.append(result)
            
        batch_time = time.time() - start_time
        
        # Create a dataframe for better visualization
        df_results = pd.DataFrame({
            'Unit Price': [input_data['Unit Price'] for input_data in batch_inputs],
            'Predicted Revenue': [result.get('predicted_revenue', 0) for result in batch_results],
            'Estimated Quantity': [result.get('estimated_quantity', 0) for result in batch_results],
            'Profit': [result.get('profit', 0) for result in batch_results],
            'Error': ['error' in result for result in batch_results]
        })
        
        print(f"Batch processing time: {batch_time:.2f} seconds")
        print(f"Average processing time per item: {batch_time/len(batch_inputs):.4f} seconds")
        print(f"Errors: {errors}")
        print("\nBatch Results Preview:")
        print(df_results.to_string(index=False))
        
        return {
            "batch_size": len(batch_inputs),
            "batch_time": batch_time,
            "avg_time_per_item": batch_time/len(batch_inputs),
            "errors": errors,
            "results": batch_results
        }
    
    def test_price_optimization(self):
        """Test price optimization functionality"""
        print("\n===== PRICE OPTIMIZATION TEST =====\n")
        
        # Use standard test case
        test_input = self.test_cases[0]['input']
        
        print("Optimizing for revenue...")
        start_time = time.time()
        revenue_opt = optimize_price(test_input, metric="revenue")
        revenue_time = time.time() - start_time
        
        print("Optimizing for profit...")
        start_time = time.time()
        profit_opt = optimize_price(test_input, metric="profit")
        profit_time = time.time() - start_time
        
        print(f"Revenue optimization time: {revenue_time:.2f} seconds")
        print(f"Profit optimization time: {profit_time:.2f} seconds")
        
        if 'error' in revenue_opt:
            print(f"\n❌ Revenue optimization error: {revenue_opt['error']}")
        else:
            print(f"\nRevenue-optimal price: ${revenue_opt['unit_price']:.2f}")
            print(f"Expected revenue: ${revenue_opt['revenue']:.2f}")
            print(f"Expected quantity: {revenue_opt['quantity']}")
        
        if 'error' in profit_opt:
            print(f"\n❌ Profit optimization error: {profit_opt['error']}")
        else:
            print(f"\nProfit-optimal price: ${profit_opt['unit_price']:.2f}")
            print(f"Expected profit: ${profit_opt['profit']:.2f}")
            print(f"Expected revenue: ${profit_opt['revenue']:.2f}")
        
        return {
            "revenue_optimization": {
                "result": revenue_opt,
                "time": revenue_time
            },
            "profit_optimization": {
                "result": profit_opt,
                "time": profit_time
            }
        }
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n===== API ENDPOINT TESTS =====\n")
        
        # API base URL
        base_url = "http://localhost:5000"
        
        # Test health endpoint
        print("Testing health endpoint...")
        try:
            response = requests.get(f"{base_url}/health")
            print(f"Health check status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")
        
        # Test prediction endpoint
        print("\nTesting prediction endpoint...")
        test_input = self.test_cases[0]['input']
        try:
            response = requests.post(
                f"{base_url}/predict-revenue",
                json=test_input
            )
            print(f"Prediction status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Prediction failed: {str(e)}")
        
        # Test simulation endpoint
        print("\nTesting simulation endpoint...")
        try:
            response = requests.post(
                f"{base_url}/simulate-revenue",
                json=test_input,
                params={
                    'min_price_factor': 0.5,
                    'max_price_factor': 2.0,
                    'steps': 7
                }
            )
            print(f"Simulation status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Simulation failed: {str(e)}")
        
        # Test optimization endpoint
        print("\nTesting optimization endpoint...")
        try:
            response = requests.post(
                f"{base_url}/optimize-price",
                json=test_input,
                params={
                    'metric': 'profit',
                    'min_price_factor': 0.5,
                    'max_price_factor': 2.0,
                    'steps': 20
                }
            )
            print(f"Optimization status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Optimization failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 80)
        print("RUNNING MODEL INTEGRATION TESTS FOR APPLICATION")
        print("=" * 80)
        
        try:
            # Run all tests
            prediction_results = self.run_prediction_tests()
            validation_results = self.test_input_validation()
            performance_results = self.test_performance()
            batch_results = self.test_batch_predictions()
            optimization_results = self.test_price_optimization()
            self.test_api_endpoints()
            
            # Summarize results
            print("\n" + "=" * 80)
            print("TEST SUMMARY")
            print("=" * 80)
            
            prediction_success = sum(1 for r in prediction_results if r["status"] == "success" and 'error' not in r.get('result', {}))
            print(f"Prediction Tests: {prediction_success}/{len(prediction_results)} successful")
            
            validation_success = sum(1 for r in validation_results if r["status"] == "success")
            print(f"Validation Tests: {validation_success}/{len(validation_results)} successful")
            
            print(f"Performance: {performance_results['avg_time']:.4f} seconds per prediction")
            print(f"Performance Errors: {performance_results['errors']}")
            print(f"Batch Processing: {batch_results['avg_time_per_item']:.4f} seconds per item")
            print(f"Batch Errors: {batch_results['errors']}")
            
            if 'error' not in optimization_results['revenue_optimization']['result']:
                print(f"Revenue Optimization: Successful")
            else:
                print(f"Revenue Optimization: Failed - {optimization_results['revenue_optimization']['result']['error']}")
                
            if 'error' not in optimization_results['profit_optimization']['result']:
                print(f"Profit Optimization: Successful")
            else:
                print(f"Profit Optimization: Failed - {optimization_results['profit_optimization']['result']['error']}")
            
            all_success = (prediction_success == len(prediction_results) and 
                          validation_success == len(validation_results) and
                          performance_results['errors'] == 0 and
                          batch_results['errors'] == 0 and
                          'error' not in optimization_results['revenue_optimization']['result'] and
                          'error' not in optimization_results['profit_optimization']['result'])
            
            if all_success:
                print("\n✅ ALL TESTS PASSED - Model is ready for application integration!")
            else:
                print("\n⚠️ SOME TESTS FAILED - Review results before integrating.")
            
            return {
                "overall_success": all_success,
                "prediction_tests": prediction_results,
                "validation_tests": validation_results,
                "performance_test": performance_results,
                "batch_test": batch_results,
                "optimization_test": optimization_results
            }
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"overall_success": False, "error": str(e)}

if __name__ == "__main__":
    # Create and run integration tests
    test_runner = ModelIntegrationTest()
    results = test_runner.run_all_tests()
    
    # Save detailed results to JSON file
    try:
        with open('integration_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print("\nDetailed test results saved to 'integration_test_results.json'")
    except Exception as e:
        print(f"Could not save results: {e}")
    
    # Set exit code based on test success
    sys.exit(0 if results.get("overall_success", False) else 1) 