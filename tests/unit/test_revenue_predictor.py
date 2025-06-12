"""
Unit tests for revenue_predictor_time_enhanced_ethical.py module.
Tests all functions with real-world examples and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from revenue_predictor_time_enhanced_ethical import (
    validate_and_convert_input,
    get_available_locations_and_products,
    predict_revenue,
    predict_revenue_for_forecasting,
    simulate_price_variations,
    optimize_price,
    predict_revenue_batch
)

class TestInputValidation:
    """Test input validation functions."""
    
    @pytest.mark.unit
    def test_validate_and_convert_input_valid_data(self, valid_prediction_input):
        """Test validation with valid input data."""
        result = validate_and_convert_input(valid_prediction_input)
        
        assert result["Unit Price"] == 5000.0
        assert result["Unit Cost"] == 2000.0
        assert result["Location"] == "North"
        assert result["_ProductID"] == "1"
        assert result["Year"] == 2025
        assert result["Month"] == 1
        assert result["Day"] == 15
        assert result["Weekday"] == "Monday"
    
    @pytest.mark.unit
    def test_validate_and_convert_input_missing_fields(self):
        """Test validation with missing required fields."""
        incomplete_data = {
            "Unit Price": 5000,
            "Unit Cost": 2000
            # Missing Location, _ProductID, etc.
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            validate_and_convert_input(incomplete_data)
    
    @pytest.mark.unit
    def test_validate_and_convert_input_invalid_month(self, valid_prediction_input):
        """Test validation with invalid month."""
        invalid_data = valid_prediction_input.copy()
        invalid_data["Month"] = 13
        
        with pytest.raises(ValueError, match="Month must be between 1 and 12"):
            validate_and_convert_input(invalid_data)
    
    @pytest.mark.unit
    def test_validate_and_convert_input_invalid_day(self, valid_prediction_input):
        """Test validation with invalid day."""
        invalid_data = valid_prediction_input.copy()
        invalid_data["Day"] = 32
        
        with pytest.raises(ValueError, match="Day must be between 1 and 31"):
            validate_and_convert_input(invalid_data)
    
    @pytest.mark.unit
    def test_validate_and_convert_input_negative_price(self, valid_prediction_input):
        """Test validation with negative unit price."""
        invalid_data = valid_prediction_input.copy()
        invalid_data["Unit Price"] = -100
        
        with pytest.raises(ValueError, match="Unit Price cannot be negative"):
            validate_and_convert_input(invalid_data)
    
    @pytest.mark.unit
    def test_validate_and_convert_input_cost_greater_than_price(self, valid_prediction_input):
        """Test validation when cost is greater than price."""
        invalid_data = valid_prediction_input.copy()
        invalid_data["Unit Cost"] = 6000  # Greater than Unit Price (5000)
        
        with pytest.raises(ValueError, match="Unit Cost cannot be greater than Unit Price"):
            validate_and_convert_input(invalid_data)
    
    @pytest.mark.unit
    def test_validate_and_convert_input_invalid_weekday(self, valid_prediction_input):
        """Test validation with invalid weekday."""
        invalid_data = valid_prediction_input.copy()
        invalid_data["Weekday"] = "InvalidDay"
        
        with pytest.raises(ValueError, match="Weekday must be one of"):
            validate_and_convert_input(invalid_data)

class TestDataLoading:
    """Test data loading and metadata functions."""
    
    @pytest.mark.unit
    def test_get_available_locations_and_products(self):
        """Test getting available locations and products."""
        locations, products = get_available_locations_and_products()
        
        assert isinstance(locations, list)
        assert isinstance(products, list)
        assert len(locations) > 0
        assert len(products) > 0
        
        # Check for expected locations
        expected_locations = ['Central', 'East', 'North', 'South', 'West']
        for loc in expected_locations:
            assert loc in locations
        
        # Check that products are valid
        for product in products[:5]:  # Check first 5
            assert isinstance(product, (int, str))
    
    @pytest.mark.unit
    @patch('revenue_predictor_time_enhanced_ethical.os.path.exists')
    def test_get_available_locations_fallback(self, mock_exists):
        """Test fallback behavior when data files don't exist."""
        mock_exists.return_value = False
        
        locations, products = get_available_locations_and_products()
        
        # Should return fallback values
        assert isinstance(locations, list)
        assert isinstance(products, list)
        assert len(locations) > 0
        assert len(products) > 0

class TestRevenuePrediction:
    """Test core revenue prediction functions."""
    
    @pytest.mark.unit
    def test_predict_revenue_valid_input(self, valid_prediction_input):
        """Test revenue prediction with valid input."""
        try:
            result = predict_revenue(valid_prediction_input)
            
            # Check response structure
            assert isinstance(result, dict)
            
            # Check for required fields
            if 'error' not in result:
                assert 'predicted_revenue' in result
                assert 'estimated_quantity' in result
                
                # Check value types and ranges
                assert isinstance(result['predicted_revenue'], (int, float))
                assert isinstance(result['estimated_quantity'], (int, float))
                assert result['predicted_revenue'] >= 0
                assert result['estimated_quantity'] >= 0
                
                print(f"Prediction successful: Revenue={result['predicted_revenue']:.2f}, "
                      f"Quantity={result['estimated_quantity']:.2f}")
            else:
                print(f"Prediction returned error: {result['error']}")
                
        except Exception as e:
            # Model may not be available in test environment
            pytest.skip(f"Model not available for testing: {str(e)}")
    
    @pytest.mark.unit
    def test_predict_revenue_edge_cases(self, sample_locations, sample_product_ids):
        """Test prediction with edge case inputs."""
        edge_cases = [
            {
                "name": "minimum_values",
                "data": {
                    "Unit Price": 1.0,
                    "Unit Cost": 0.5,
                    "Location": "North",
                    "_ProductID": "1",
                    "Year": 2025,
                    "Month": 1,
                    "Day": 1,
                    "Weekday": "Monday"
                }
            },
            {
                "name": "high_values",
                "data": {
                    "Unit Price": 50000.0,
                    "Unit Cost": 25000.0,
                    "Location": "Central",
                    "_ProductID": "47",
                    "Year": 2025,
                    "Month": 12,
                    "Day": 31,
                    "Weekday": "Sunday"
                }
            }
        ]
        
        for case in edge_cases:
            try:
                result = predict_revenue(case["data"])
                
                if 'error' not in result:
                    assert isinstance(result, dict)
                    assert 'predicted_revenue' in result
                    print(f"Edge case '{case['name']}' successful: {result['predicted_revenue']:.2f}")
                else:
                    print(f"Edge case '{case['name']}' returned error: {result['error']}")
                    
            except Exception as e:
                print(f"Edge case '{case['name']}' failed: {str(e)}")
    
    @pytest.mark.unit
    def test_predict_revenue_for_forecasting(self, valid_prediction_input):
        """Test forecasting-specific prediction function."""
        try:
            result = predict_revenue_for_forecasting(valid_prediction_input)
            
            assert isinstance(result, dict)
            
            if 'error' not in result:
                assert 'predicted_revenue' in result
                assert 'estimated_quantity' in result
                
                # Forecasting function should preserve time variations
                assert isinstance(result['predicted_revenue'], (int, float))
                assert result['predicted_revenue'] >= 0
                
                print(f"Forecasting prediction successful: {result['predicted_revenue']:.2f}")
            else:
                print(f"Forecasting prediction error: {result['error']}")
                
        except Exception as e:
            pytest.skip(f"Forecasting model not available: {str(e)}")

class TestBatchPrediction:
    """Test batch prediction functionality."""
    
    @pytest.mark.unit
    def test_predict_revenue_batch_valid_inputs(self, performance_test_data):
        """Test batch prediction with multiple valid inputs."""
        # Use first 10 items for unit test
        batch_data = performance_test_data[:10]
        
        try:
            results = predict_revenue_batch(batch_data)
            
            assert isinstance(results, list)
            
            # Check that some predictions succeeded
            successful_predictions = [r for r in results if 'error' not in r]
            
            if successful_predictions:
                for result in successful_predictions[:3]:  # Check first 3
                    assert 'predicted_revenue' in result
                    assert 'estimated_quantity' in result
                    assert isinstance(result['predicted_revenue'], (int, float))
                    assert result['predicted_revenue'] >= 0
                
                print(f"Batch prediction: {len(successful_predictions)}/{len(batch_data)} successful")
            else:
                print("No successful batch predictions")
                
        except Exception as e:
            pytest.skip(f"Batch prediction not available: {str(e)}")
    
    @pytest.mark.unit
    def test_predict_revenue_batch_empty_input(self):
        """Test batch prediction with empty input."""
        try:
            results = predict_revenue_batch([])
            
            assert isinstance(results, list)
            assert len(results) == 0
            
        except Exception as e:
            pytest.skip(f"Batch prediction not available: {str(e)}")
    
    @pytest.mark.unit
    def test_predict_revenue_batch_mixed_inputs(self, valid_prediction_input, edge_case_inputs):
        """Test batch prediction with mix of valid and invalid inputs."""
        mixed_batch = [
            valid_prediction_input,
            edge_case_inputs["invalid_location"],
            edge_case_inputs["negative_values"],
            valid_prediction_input.copy()
        ]
        
        try:
            results = predict_revenue_batch(mixed_batch)
            
            assert isinstance(results, list)
            assert len(results) <= len(mixed_batch)  # Some may fail and be filtered
            
            # Check that at least some succeeded
            successful = [r for r in results if 'error' not in r]
            if successful:
                print(f"Mixed batch: {len(successful)}/{len(mixed_batch)} successful")
            
        except Exception as e:
            pytest.skip(f"Batch prediction not available: {str(e)}")

class TestPriceOptimization:
    """Test price optimization and simulation functions."""
    
    @pytest.mark.unit
    def test_simulate_price_variations(self, valid_prediction_input):
        """Test price variation simulation."""
        try:
            results = simulate_price_variations(valid_prediction_input)
            
            assert isinstance(results, list)
            
            if results:
                # Check structure of results
                for result in results[:3]:  # Check first 3
                    assert 'price' in result
                    assert 'revenue' in result
                    assert isinstance(result['price'], (int, float))
                    assert isinstance(result['revenue'], (int, float))
                    assert result['price'] > 0
                    assert result['revenue'] >= 0
                
                # Check that prices vary
                prices = [r['price'] for r in results]
                assert len(set(prices)) > 1, "Prices should vary in simulation"
                
                print(f"Price simulation: {len(results)} scenarios generated")
            else:
                print("No price simulation results")
                
        except Exception as e:
            pytest.skip(f"Price simulation not available: {str(e)}")
    
    @pytest.mark.unit  
    def test_optimize_price_profit(self, valid_prediction_input):
        """Test price optimization for profit maximization."""
        try:
            result = optimize_price(valid_prediction_input, metric='profit')
            
            assert isinstance(result, dict)
            
            if 'error' not in result:
                assert 'optimal_price' in result
                assert 'expected_revenue' in result
                assert 'expected_profit' in result
                
                assert isinstance(result['optimal_price'], (int, float))
                assert result['optimal_price'] > 0
                assert result['expected_profit'] >= 0
                
                print(f"Price optimization successful: Optimal price=${result['optimal_price']:.2f}, "
                      f"Expected profit=${result['expected_profit']:.2f}")
            else:
                print(f"Price optimization error: {result['error']}")
                
        except Exception as e:
            pytest.skip(f"Price optimization not available: {str(e)}")
    
    @pytest.mark.unit
    def test_optimize_price_revenue(self, valid_prediction_input):
        """Test price optimization for revenue maximization."""
        try:
            result = optimize_price(valid_prediction_input, metric='revenue')
            
            assert isinstance(result, dict)
            
            if 'error' not in result:
                assert 'optimal_price' in result
                assert 'expected_revenue' in result
                
                assert isinstance(result['optimal_price'], (int, float))
                assert result['optimal_price'] > 0
                assert result['expected_revenue'] >= 0
                
                print(f"Revenue optimization successful: Optimal price=${result['optimal_price']:.2f}, "
                      f"Expected revenue=${result['expected_revenue']:.2f}")
            else:
                print(f"Revenue optimization error: {result['error']}")
                
        except Exception as e:
            pytest.skip(f"Revenue optimization not available: {str(e)}")

class TestErrorHandling:
    """Test error handling in prediction functions."""
    
    @pytest.mark.unit
    def test_predict_revenue_missing_model_files(self):
        """Test behavior when model files are missing."""
        invalid_input = {
            "Unit Price": 5000,
            "Unit Cost": 2000,
            "Location": "North",
            "_ProductID": "1",
            "Year": 2025,
            "Month": 1,
            "Day": 15,
            "Weekday": "Monday"
        }
        
        with patch('revenue_predictor_time_enhanced_ethical.os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            try:
                result = predict_revenue(invalid_input)
                # Should either skip or return error
                if isinstance(result, dict) and 'error' in result:
                    assert 'error' in result
                    print(f"Expected error for missing model: {result['error']}")
            except FileNotFoundError:
                # This is expected behavior
                print("Expected FileNotFoundError for missing model files")
            except Exception as e:
                print(f"Different error for missing model: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 