"""Quick API check script"""
import requests
import json


def check_endpoint(url, method="GET", payload=None):
    """Check an endpoint and print the response"""
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=payload)
        
        print(f"\n{method} {url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Response: {response.text}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to {url}: {e}")


base_url = "http://127.0.0.1:5000"

# Check basic endpoints
check_endpoint(f"{base_url}/health")
check_endpoint(f"{base_url}/locations")
check_endpoint(f"{base_url}/products")

# Check prediction
predict_payload = {
    "Unit Price": 5000.0,
    "Unit Cost": 2000.0,
    "Location": "North",
    "_ProductID": 1,
    "Year": 2025,
    "Month": 1,
    "Day": 15,
    "Weekday": "Monday"
}
check_endpoint(f"{base_url}/predict-revenue", "POST", predict_payload)

# Check insights
check_endpoint(f"{base_url}/business-insights")
check_endpoint(f"{base_url}/insights")

# Check dashboard
check_endpoint(f"{base_url}/dashboard-data")

# Check forecast
forecast_payload = {"location": "Central", "product_id": 1}
check_endpoint(f"{base_url}/forecast-sales", "POST", forecast_payload) 