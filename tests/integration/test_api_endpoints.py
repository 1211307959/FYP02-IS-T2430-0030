"""
Integration tests for Flask API endpoints.
Tests real HTTP requests to running API server.
"""

import pytest
import requests
import json
import time

class TestAPIBasics:
    """Test basic API functionality."""
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_health_endpoint(self, api_base_url, api_health_check):
        """Test the /health endpoint."""
        response = requests.get(f"{api_base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model" in data
        assert data["status"] == "healthy"
        assert data["model"] == "ethical_time_enhanced"
        
        print("✅ Health endpoint working")
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_locations_endpoint(self, api_base_url, api_health_check):
        """Test the /locations endpoint."""
        response = requests.get(f"{api_base_url}/locations")
        
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data
        assert isinstance(data["locations"], list)
        assert len(data["locations"]) > 0
        
        print(f"✅ Locations endpoint: {len(data['locations'])} locations")
    
    @pytest.mark.integration
    @pytest.mark.api
    def test_predict_revenue_endpoint(self, api_base_url, api_health_check, valid_api_prediction_input):
        """Test /predict-revenue endpoint."""
        response = requests.post(
            f"{api_base_url}/predict-revenue",
            json=valid_api_prediction_input,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "predicted_revenue" in data
        assert "estimated_quantity" in data
        assert isinstance(data["predicted_revenue"], (int, float))
        assert data["predicted_revenue"] > 0
        
        print(f"✅ Revenue prediction: ${data['predicted_revenue']:.2f}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 