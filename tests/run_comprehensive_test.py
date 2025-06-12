import requests
import json
import time
from datetime import datetime

# Test all major endpoints
base_url = 'http://127.0.0.1:5000'
results = {'total': 0, 'passed': 0, 'failed': 0}

def test_endpoint(name, method, endpoint, payload=None):
    global results
    results['total'] += 1
    try:
        if method == 'GET':
            r = requests.get(f'{base_url}{endpoint}')
        else:
            r = requests.post(f'{base_url}{endpoint}', json=payload)
        
        if r.status_code in [200, 201]:
            results['passed'] += 1
            print(f'✓ {name}: PASS')
            if 'predict' in endpoint and r.status_code == 200:
                data = r.json()
                if 'predicted_revenue' in data:
                    print(f'  Revenue: ${data["predicted_revenue"]:.2f}')
            return True
        else:
            results['failed'] += 1
            print(f'✗ {name}: FAIL ({r.status_code})')
            return False
    except Exception as e:
        results['failed'] += 1
        print(f'✗ {name}: ERROR ({e})')
        return False

print('COMPREHENSIVE SYSTEM TEST')
print('='*60)

# Core endpoints
test_endpoint('Health Check', 'GET', '/health')
test_endpoint('Locations Data', 'GET', '/locations')
test_endpoint('Products Data', 'GET', '/products')
test_endpoint('Dashboard Data', 'GET', '/dashboard-data')

# Prediction & Analysis
pred_payload = {
    'Unit Price': 5000.0, 'Unit Cost': 2000.0, 'Location': 'North',
    '_ProductID': 1, 'Year': 2025, 'Month': 6, 'Day': 15, 'Weekday': 'Monday'
}
test_endpoint('Revenue Prediction', 'POST', '/predict-revenue', pred_payload)

# Test all locations
print('\n--- Testing All Locations ---')
locations = ['Central', 'East', 'North', 'South', 'West']
for loc in locations:
    payload = {**pred_payload, 'Location': loc}
    test_endpoint(f'Prediction for {loc}', 'POST', '/predict-revenue', payload)

# Insights
print('\n--- Testing Insights ---')
test_endpoint('Business Insights', 'GET', '/business-insights')
test_endpoint('Detailed Insights', 'GET', '/insights')

# Forecasting
print('\n--- Testing Forecasting ---')
forecast_payload = {'location': 'Central', 'product_id': 1}
test_endpoint('Sales Forecast', 'POST', '/forecast-sales', forecast_payload)

multi_forecast = {'location': 'Central', 'product_ids': [1, 2, 3]}
test_endpoint('Multiple Product Forecast', 'POST', '/forecast-multiple', multi_forecast)

trend_forecast = {
    'location': 'Central', 'product_id': 1,
    'start_date': '2025-01-01', 'end_date': '2025-03-31'
}
test_endpoint('Trend Forecast', 'POST', '/forecast-trend', trend_forecast)

# Scenario Planning
print('\n--- Testing Scenario Planning ---')
scenario_payload = {
    'Unit Price': 3000.0, 'Unit Cost': 1200.0, 'Location': 'Central',
    '_ProductID': 1, 'Year': 2025, 'Month': 6, 'Day': 15, 'Weekday': 'Monday'
}
test_endpoint('Revenue Simulation', 'POST', '/simulate-revenue', scenario_payload)
test_endpoint('Price Optimization', 'POST', '/optimize-price', scenario_payload)

# Data Management
print('\n--- Testing Data Management ---')
reload_payload = {'confirm': True}
test_endpoint('Data Reload', 'POST', '/reload-data', reload_payload)

# Performance Test
print('\n--- Testing Performance ---')
start_time = time.time()
for i in range(5):
    payload = {**pred_payload, 'Unit Price': 2000 + (i * 500)}
    requests.post(f'{base_url}/predict-revenue', json=payload)
duration = time.time() - start_time
print(f'✓ Performance Test: 5 predictions in {duration:.3f}s ({duration/5:.3f}s avg)')

# Summary
print('\n' + '='*60)
print(f'FINAL RESULTS: {results["passed"]}/{results["total"]} tests passed')
success_rate = results["passed"] / results["total"] * 100
print(f'Success Rate: {success_rate:.1f}%')

if success_rate >= 90:
    print('🎉 SYSTEM STATUS: EXCELLENT - Production Ready!')
elif success_rate >= 80:
    print('✅ SYSTEM STATUS: VERY GOOD - Minor issues')
elif success_rate >= 70:
    print('⚠️ SYSTEM STATUS: GOOD - Some issues to address')
else:
    print('❌ SYSTEM STATUS: NEEDS SIGNIFICANT WORK')

print(f'\nTest completed at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('='*60) 