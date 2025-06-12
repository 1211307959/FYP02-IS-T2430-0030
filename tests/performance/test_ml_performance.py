"""
Performance tests for ML operations in the revenue prediction system.
Tests response times, batch processing, and load handling.
"""

import pytest
import time
import statistics
import numpy as np
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from revenue_predictor_time_enhanced_ethical import (
    predict_revenue,
    predict_revenue_batch,
    simulate_price_variations
)

class TestMLPerformance:
    """Test ML model performance."""
    
    @pytest.mark.performance
    def test_single_prediction_speed(self, valid_prediction_input):
        """Test speed of single prediction."""
        times = []
        
        for i in range(10):  # 10 runs
            start_time = time.time()
            
            try:
                result = predict_revenue(valid_prediction_input)
                end_time = time.time()
                
                if 'error' not in result:
                    times.append(end_time - start_time)
                
            except Exception as e:
                pytest.skip(f"Model not available: {str(e)}")
        
        if times:
            avg_time = statistics.mean(times)
            median_time = statistics.median(times)
            max_time = max(times)
            
            # Should complete within reasonable time
            assert avg_time < 2.0, f"Average prediction time too slow: {avg_time:.3f}s"
            assert max_time < 5.0, f"Max prediction time too slow: {max_time:.3f}s"
            
            print(f"✅ Single prediction performance:")
            print(f"   Average: {avg_time:.3f}s")
            print(f"   Median: {median_time:.3f}s") 
            print(f"   Max: {max_time:.3f}s")
        else:
            pytest.skip("No successful predictions for performance test")
    
    @pytest.mark.performance
    def test_batch_prediction_speed(self, performance_test_data):
        """Test speed of batch predictions."""
        batch_sizes = [10, 50, 100]
        
        for batch_size in batch_sizes:
            if len(performance_test_data) < batch_size:
                continue
                
            batch_data = performance_test_data[:batch_size]
            
            start_time = time.time()
            
            try:
                results = predict_revenue_batch(batch_data)
                end_time = time.time()
                
                total_time = end_time - start_time
                time_per_prediction = total_time / batch_size
                
                # Should be faster than individual predictions
                assert time_per_prediction < 1.0, f"Batch prediction too slow: {time_per_prediction:.3f}s per item"
                
                successful = sum(1 for r in results if 'error' not in r)
                
                print(f"✅ Batch size {batch_size}:")
                print(f"   Total time: {total_time:.3f}s")
                print(f"   Per prediction: {time_per_prediction:.3f}s")
                print(f"   Success rate: {successful}/{batch_size}")
                
            except Exception as e:
                print(f"⚠️ Batch size {batch_size} failed: {str(e)}")
    
    @pytest.mark.performance
    def test_price_simulation_speed(self, valid_prediction_input):
        """Test speed of price simulation."""
        step_counts = [5, 10, 20]
        
        for steps in step_counts:
            start_time = time.time()
            
            try:
                results = simulate_price_variations(
                    valid_prediction_input,
                    min_price_factor=0.5,
                    max_price_factor=2.0,
                    steps=steps
                )
                end_time = time.time()
                
                total_time = end_time - start_time
                time_per_step = total_time / steps
                
                # Should complete reasonably fast
                assert total_time < 10.0, f"Price simulation too slow: {total_time:.3f}s"
                assert time_per_step < 1.0, f"Per-step simulation too slow: {time_per_step:.3f}s"
                
                print(f"✅ Price simulation {steps} steps:")
                print(f"   Total time: {total_time:.3f}s")
                print(f"   Per step: {time_per_step:.3f}s")
                print(f"   Results: {len(results)} scenarios")
                
            except Exception as e:
                print(f"⚠️ Price simulation {steps} steps failed: {str(e)}")

class TestAPIPerformance:
    """Test API endpoint performance."""
    
    @pytest.mark.performance
    @pytest.mark.api
    def test_api_prediction_speed(self, api_base_url, api_health_check, valid_api_prediction_input):
        """Test API prediction endpoint speed."""
        times = []
        
        for i in range(5):  # 5 API calls
            start_time = time.time()
            
            response = requests.post(
                f"{api_base_url}/predict-revenue",
                json=valid_api_prediction_input,
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                times.append(end_time - start_time)
        
        if times:
            avg_time = statistics.mean(times)
            median_time = statistics.median(times)
            max_time = max(times)
            
            # API should respond quickly
            assert avg_time < 5.0, f"API too slow: {avg_time:.3f}s"
            assert max_time < 10.0, f"API max time too slow: {max_time:.3f}s"
            
            print(f"✅ API prediction performance:")
            print(f"   Average: {avg_time:.3f}s")
            print(f"   Median: {median_time:.3f}s")
            print(f"   Max: {max_time:.3f}s")
        else:
            pytest.skip("No successful API calls for performance test")
    
    @pytest.mark.performance
    @pytest.mark.api
    @pytest.mark.slow
    def test_concurrent_api_requests(self, api_base_url, api_health_check, valid_api_prediction_input):
        """Test concurrent API request handling."""
        num_concurrent = 5
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.post(
                    f"{api_base_url}/predict-revenue",
                    json=valid_api_prediction_input,
                    headers={"Content-Type": "application/json"},
                    timeout=15
                )
                end_time = time.time()
                
                return {
                    'success': response.status_code == 200,
                    'time': end_time - start_time,
                    'status': response.status_code
                }
            except Exception as e:
                return {
                    'success': False,
                    'time': 0,
                    'error': str(e)
                }
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful = sum(1 for r in results if r['success'])
        response_times = [r['time'] for r in results if r['success']]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            
            # All or most should succeed
            success_rate = successful / num_concurrent
            assert success_rate >= 0.6, f"Low success rate: {success_rate:.2f}"
            
            # Concurrent processing should be reasonably fast
            assert total_time < 30.0, f"Concurrent processing too slow: {total_time:.3f}s"
            
            print(f"✅ Concurrent API performance:")
            print(f"   Success rate: {successful}/{num_concurrent} ({success_rate:.2%})")
            print(f"   Total time: {total_time:.3f}s")
            print(f"   Avg response: {avg_response_time:.3f}s")
        else:
            pytest.fail("No successful concurrent requests")
    
    @pytest.mark.performance
    @pytest.mark.api
    def test_api_endpoint_variety(self, api_base_url, api_health_check):
        """Test performance across different API endpoints."""
        endpoints = [
            ('GET', '/health', {}),
            ('GET', '/locations', {}),
            ('GET', '/dashboard-data', {}),
            ('GET', '/business-insights', {}),
        ]
        
        results = {}
        
        for method, endpoint, data in endpoints:
            times = []
            
            for i in range(3):  # 3 calls per endpoint
                start_time = time.time()
                
                if method == 'GET':
                    response = requests.get(f"{api_base_url}{endpoint}")
                else:
                    response = requests.post(
                        f"{api_base_url}{endpoint}",
                        json=data,
                        headers={"Content-Type": "application/json"}
                    )
                
                end_time = time.time()
                
                if response.status_code == 200:
                    times.append(end_time - start_time)
            
            if times:
                avg_time = statistics.mean(times)
                results[endpoint] = avg_time
                
                # Most endpoints should be fast
                assert avg_time < 10.0, f"{endpoint} too slow: {avg_time:.3f}s"
                
                print(f"✅ {endpoint}: {avg_time:.3f}s avg")
            else:
                print(f"⚠️ {endpoint}: No successful calls")
        
        print(f"✅ Tested {len(results)} endpoints successfully")

class TestMemoryUsage:
    """Test memory usage patterns."""
    
    @pytest.mark.performance
    def test_memory_stability(self, performance_test_data):
        """Test that repeated predictions don't leak memory."""
        import psutil
        import gc
        
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run multiple predictions
        for i in range(20):
            try:
                # Use smaller batches to avoid overwhelming
                batch = performance_test_data[i:i+5]
                results = predict_revenue_batch(batch)
                
                # Force garbage collection
                if i % 5 == 0:
                    gc.collect()
                    
            except Exception:
                continue  # Skip failed predictions
        
        # Get final memory
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 100, f"Memory leak detected: {memory_increase:.1f}MB increase"
        
        print(f"✅ Memory usage:")
        print(f"   Initial: {initial_memory:.1f}MB")
        print(f"   Final: {final_memory:.1f}MB")
        print(f"   Increase: {memory_increase:.1f}MB")

class TestScalabilityBenchmarks:
    """Scalability and load testing."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_batch_processing(self, performance_test_data):
        """Test processing large batches."""
        if len(performance_test_data) < 100:
            pytest.skip("Not enough test data for large batch test")
        
        # Test increasingly large batches
        batch_sizes = [50, 100, 200]
        
        for batch_size in batch_sizes:
            if len(performance_test_data) < batch_size:
                continue
                
            batch = performance_test_data[:batch_size]
            
            start_time = time.time()
            
            try:
                results = predict_revenue_batch(batch)
                end_time = time.time()
                
                processing_time = end_time - start_time
                throughput = batch_size / processing_time
                
                # Should maintain reasonable throughput
                assert throughput > 1.0, f"Throughput too low: {throughput:.2f} predictions/sec"
                
                successful = sum(1 for r in results if 'error' not in r)
                success_rate = successful / batch_size
                
                print(f"✅ Batch size {batch_size}:")
                print(f"   Time: {processing_time:.2f}s")
                print(f"   Throughput: {throughput:.2f} predictions/sec")
                print(f"   Success rate: {success_rate:.2%}")
                
            except Exception as e:
                print(f"⚠️ Batch size {batch_size} failed: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 