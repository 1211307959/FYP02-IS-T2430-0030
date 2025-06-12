"""
Pytest configuration and fixtures for IDSS Revenue Prediction System tests.
Based on actual analysis of the codebase and running API.
"""

import pytest
import pandas as pd
import numpy as np
import requests
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
API_BASE_URL = "http://localhost:5000"
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture(scope="session")
def api_base_url():
    """Base URL for the Flask API."""
    return API_BASE_URL

@pytest.fixture(scope="session")
def real_training_data():
    """Load actual training dataset for testing."""
    dataset_path = "trainingdataset.csv"
    if os.path.exists(dataset_path):
        # Load first 1000 rows for testing performance
        df = pd.read_csv(dataset_path, nrows=1000)
        return df
    else:
        pytest.skip("Training dataset not found")

@pytest.fixture
def valid_prediction_input():
    """Valid input for revenue prediction based on actual data schema."""
    return {
        "Unit Price": 5000.0,
        "Unit Cost": 2000.0,
        "Location": "North",
        "_ProductID": "1",
        "Year": 2025,
        "Month": 1,
        "Day": 15,
        "Weekday": "Monday"
    }

@pytest.fixture
def valid_api_prediction_input():
    """Valid input for API prediction endpoints."""
    return {
        "Unit Price": 5000.0,
        "Unit Cost": 2000.0,
        "Location": "North",
        "_ProductID": 1,
        "Year": 2025,
        "Month": 1,
        "Day": 15,
        "Weekday": "Monday"
    }

@pytest.fixture
def valid_forecast_input():
    """Valid input for forecasting endpoints."""
    return {
        "Unit Price": 5000.0,
        "Unit Cost": 2000.0,
        "Location": "North",
        "_ProductID": 1,
        "start_date": "2025-01-01",
        "end_date": "2025-01-07",
        "frequency": "D"
    }

@pytest.fixture
def sample_locations():
    """Actual locations from the system."""
    return ["Central", "East", "North", "South", "West"]

@pytest.fixture
def sample_product_ids():
    """Sample product IDs based on actual data."""
    return [1, 2, 3, 4, 5, 10, 20, 30, 47]

@pytest.fixture
def malicious_inputs():
    """Malicious inputs for security testing."""
    return {
        "sql_injection": [
            "'; DROP TABLE revenue; --",
            "1' OR '1'='1",
            "' UNION SELECT * FROM users --"
        ],
        "xss_attempts": [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ],
        "command_injection": [
            "; rm -rf /",
            "| whoami",
            "&& dir C:\\"
        ],
        "extreme_values": [
            float('inf'),
            float('-inf'),
            float('nan'),
            1e308,
            -1e308
        ],
        "buffer_overflow": [
            "A" * 10000,
            "1" * 1000,
            "nested_" * 100
        ]
    }

@pytest.fixture
def edge_case_inputs():
    """Edge case inputs for boundary testing."""
    return {
        "zero_values": {
            "Unit Price": 0,
            "Unit Cost": 0,
            "Location": "North",
            "_ProductID": 1
        },
        "negative_values": {
            "Unit Price": -100,
            "Unit Cost": -50,
            "Location": "North", 
            "_ProductID": 1
        },
        "very_large_values": {
            "Unit Price": 1000000,
            "Unit Cost": 999999,
            "Location": "North",
            "_ProductID": 1
        },
        "invalid_location": {
            "Unit Price": 5000,
            "Unit Cost": 2000,
            "Location": "INVALID_LOCATION",
            "_ProductID": 1
        },
        "invalid_product": {
            "Unit Price": 5000,
            "Unit Cost": 2000,
            "Location": "North",
            "_ProductID": 99999
        }
    }

@pytest.fixture
def performance_test_data():
    """Large dataset for performance testing."""
    np.random.seed(42)
    data = []
    locations = ["Central", "East", "North", "South", "West"]
    
    for i in range(500):  # 500 test cases
        data.append({
            "Unit Price": np.random.uniform(1000, 10000),
            "Unit Cost": np.random.uniform(500, 5000),
            "Location": np.random.choice(locations),
            "_ProductID": np.random.randint(1, 48),
            "Year": np.random.choice([2023, 2024, 2025]),
            "Month": np.random.randint(1, 13),
            "Day": np.random.randint(1, 29),
            "Weekday": np.random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        })
    
    return data

@pytest.fixture(scope="session")
def api_health_check():
    """Check if API is running before tests."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True
        else:
            pytest.skip("API is not healthy")
    except requests.exceptions.RequestException:
        pytest.skip("API is not available")

@pytest.fixture
def create_test_csv():
    """Create test CSV files for data loading tests."""
    def _create_csv(filename: str, data: List[Dict], invalid: bool = False):
        filepath = os.path.join(TEST_DATA_DIR, filename)
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
        
        if invalid:
            # Create malformed CSV
            with open(filepath, 'w') as f:
                f.write("Invalid,CSV,Data\nMissing,Columns\nInconsistent,Row,Data,Extra")
        else:
            # Create valid CSV
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
        
        return filepath
    
    return _create_csv

@pytest.fixture
def cleanup_test_files():
    """Cleanup test files after tests."""
    created_files = []
    
    def _add_file(filepath):
        created_files.append(filepath)
        return filepath
    
    yield _add_file
    
    # Cleanup
    for filepath in created_files:
        if os.path.exists(filepath):
            os.remove(filepath)

@pytest.fixture
def mock_model_prediction():
    """Mock model prediction for unit tests."""
    return {
        "predicted_revenue": 10000.0,
        "estimated_quantity": 2.0,
        "unit_price": 5000.0,
        "estimated_cost": 4000.0,
        "estimated_profit": 6000.0,
        "location": "North",
        "product_id": "1",
        "profit_margin": 0.6,
        "season": "Winter"
    }

# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "api: API endpoint tests")

# Custom assertions
def assert_valid_prediction_response(response_data: Dict[str, Any]):
    """Assert that a prediction response has valid structure and values."""
    required_fields = ["predicted_revenue", "estimated_quantity"]
    
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"
    
    # Check that values are reasonable
    assert isinstance(response_data["predicted_revenue"], (int, float))
    assert isinstance(response_data["estimated_quantity"], (int, float))
    assert response_data["predicted_revenue"] >= 0
    assert response_data["estimated_quantity"] >= 0

def assert_valid_api_response(response):
    """Assert that an API response is valid."""
    assert response.status_code in [200, 400, 422, 500], f"Unexpected status code: {response.status_code}"
    
    if response.status_code == 200:
        try:
            data = response.json()
            assert isinstance(data, dict), "Response should be JSON object"
        except json.JSONDecodeError:
            pytest.fail("Response is not valid JSON")

# Make custom assertions available globally
pytest.assert_valid_prediction_response = assert_valid_prediction_response
pytest.assert_valid_api_response = assert_valid_api_response 