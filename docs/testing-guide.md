# Testing Guide - Revenue Prediction System

## Overview
This guide covers all testing procedures for the Revenue Prediction System, including model validation, API testing, integration testing, and performance benchmarking.

## Testing Framework

### Core Testing Files
- `app_model_test.py` - Main model validation and quick tests
- `test_ethical_time_enhanced_model.py` - Comprehensive model testing
- `application_integration_test.py` - End-to-end integration testing
- `application_test_model.py` - Detailed application testing
- `test_scenario_planner.js` - Frontend scenario planner testing

## Model Testing

### 1. Quick Model Validation

Run the basic model test to verify the system is working:

```bash
python app_model_test.py
```

**Expected Output:**
```
✓ Model loads successfully
✓ Basic prediction works
✓ Price simulation works  
✓ All locations aggregation works
✓ Price elasticity working correctly

Basic Model Test Results:
- Model loaded: ✓
- Test prediction: $1,247.85 revenue
- Price simulation: 7 variations generated
- All tests passed
```

### 2. Comprehensive Model Testing

Run the full test suite for detailed validation:

```bash
python test_ethical_time_enhanced_model.py
```

**Expected Results:**
- **R² Score:** ≥ 0.99
- **MAE:** < 50
- **RMSE:** < 250
- **Feature Count:** 50+ features
- **Prediction Time:** < 100ms per prediction

### 3. Integration Testing

Run comprehensive integration tests:

```bash
python application_integration_test.py
```

**Test Coverage:**
- Input validation across all parameters
- Edge case handling (extreme prices, invalid dates)
- Batch prediction performance
- Error handling and recovery
- Data consistency validation

### 4. Performance Testing

Run performance benchmarks:

```bash
python test_api_performance.py
```

**Performance Targets:**
- Single prediction: < 10ms
- Batch predictions (100): < 1s
- Price simulation (7 points): < 50ms
- Memory usage: < 500MB

## API Testing

### 1. Health Check Test

```bash
curl -X GET http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Revenue prediction API is running",
  "model_loaded": true
}
```

### 2. Revenue Prediction Test

```bash
curl -X POST http://localhost:5000/predict-revenue \
  -H "Content-Type: application/json" \
  -d '{
    "_ProductID": 12,
    "Location": "North",
    "Unit Price": 150.00,
    "Unit Cost": 75.00,
    "Weekday": "Friday",
    "Month": 6,
    "Day": 15,
    "Year": 2024
  }'
```

**Validation Criteria:**
- Response time < 100ms
- Revenue > 0 for reasonable inputs
- All required fields in response
- Profit calculation accuracy

### 3. Price Simulation Test

```bash
curl -X POST http://localhost:5000/simulate-revenue \
  -H "Content-Type: application/json" \
  -d '{
    "_ProductID": 12,
    "Location": "North",
    "Unit Price": 150.00,
    "Unit Cost": 75.00,
    "Weekday": "Friday",
    "Month": 6,
    "Day": 15,
    "Year": 2024
  }'
```

**Validation Criteria:**
- 7 price variations generated
- Price elasticity evident (higher price = lower quantity)
- Optimal prices identified
- Reasonable profit margins

### 4. Sales Forecasting Test

```bash
curl -X POST http://localhost:5000/forecast-sales \
  -H "Content-Type: application/json" \
  -d '{
    "_ProductID": 12,
    "Location": "North",
    "Unit Price": 150.00,
    "Unit Cost": 75.00,
    "start_date": "2024-01-01",
    "end_date": "2024-01-30",
    "frequency": "daily"
  }'
```

**Validation Criteria:**
- 30 daily forecasts generated
- Confidence intervals provided
- Temporal patterns evident
- Summary statistics accurate

## Frontend Testing

### 1. Scenario Planner Testing

Run the JavaScript test suite:

```bash
cd tests
npm test
```

Or run specifically:

```bash
node test_scenario_planner.js
```

**Test Coverage:**
- Product selection and data loading
- Location handling including "All Locations"
- Price simulation with realistic ranges
- Chart data processing and display
- Error handling for extreme values

### 2. Manual Frontend Testing

**Dashboard Page:**
1. Navigate to http://localhost:3000/dashboard
2. Verify all KPIs load correctly
3. Check chart rendering and responsiveness
4. Test profit ranking toggle functionality

**Scenario Planner:**
1. Navigate to http://localhost:3000/scenario-planner
2. Select different products and locations
3. Test price simulation with various inputs
4. Verify chart updates correctly
5. Test "All Locations" aggregation

**Sales Forecasting:**
1. Navigate to http://localhost:3000/sales-forecasting
2. Test automatic forecast generation
3. Verify custom forecast functionality
4. Check chart rendering and data accuracy

## Data Validation Testing

### 1. Data Consistency Tests

```bash
python test_dashboard_consistency.py
```

**Validation Checks:**
- No product appears in both top and bottom rankings
- Revenue calculations are consistent
- Location aggregations are accurate
- Date ranges are valid

### 2. Price Elasticity Testing

```bash
python test_price_elasticity.py
```

**Validation Criteria:**
- Lower prices result in higher quantities
- Higher prices result in lower quantities
- Extreme prices result in zero quantities
- Price ratios are calculated correctly

### 3. Location and Product Variation Testing

```bash
python test_location_product_variation.py
```

**Test Coverage:**
- Different products show different predictions
- Different locations show different patterns
- "All Locations" properly aggregates data
- Product-location combinations are unique

## Error Testing

### 1. Invalid Input Testing

Test various invalid inputs to ensure proper error handling:

```python
# Test invalid product ID
invalid_tests = [
    {"_ProductID": -1},  # Negative ID
    {"_ProductID": 9999},  # Non-existent ID
    {"Unit Price": -50},  # Negative price
    {"Month": 13},  # Invalid month
    {"Location": "InvalidLocation"}  # Non-existent location
]
```

### 2. Extreme Value Testing

```python
# Test extreme values
extreme_tests = [
    {"Unit Price": 999999},  # Very high price
    {"Unit Price": 0.01},  # Very low price
    {"Unit Cost": 999999},  # Very high cost
    {"Year": 1900},  # Very old year
    {"Year": 2100}  # Future year
]
```

### 3. Network Error Simulation

Test API resilience:
- Stop backend server during frontend requests
- Send malformed JSON data
- Test timeout handling
- Verify fallback mechanisms

## Automated Testing Setup

### 1. Continuous Integration

Create a test script for CI/CD:

```bash
#!/bin/bash
# test_all.sh

echo "Starting comprehensive test suite..."

# Model tests
echo "Running model tests..."
python app_model_test.py || exit 1
python test_ethical_time_enhanced_model.py || exit 1

# API tests  
echo "Starting API server..."
python combined_time_enhanced_ethical_api.py &
API_PID=$!
sleep 5

echo "Running API tests..."
python test_api_performance.py || exit 1

# Frontend tests
echo "Running frontend tests..."
cd tests
npm test || exit 1

# Cleanup
kill $API_PID
echo "All tests completed successfully!"
```

### 2. Pre-deployment Testing

Before deploying to production:

```bash
# Full test suite
./test_all.sh

# Performance benchmarks
python test_api_performance.py

# Data validation
python test_dashboard_consistency.py

# Integration tests
python application_integration_test.py
```

## Test Data Management

### 1. Test Dataset

Use a subset of the training data for testing:

```python
# Create test dataset
test_data = df.sample(n=1000, random_state=42)
test_data.to_csv('test_dataset.csv', index=False)
```

### 2. Mock Data Generation

For frontend testing without backend:

```javascript
// Generate mock simulation data
const generateMockSimulation = () => {
  return {
    variations: [
      { name: "50% Lower", price: 75, revenue: 1200, quantity: 16 },
      { name: "Current Price", price: 150, revenue: 1000, quantity: 7 },
      { name: "100% Higher", price: 300, revenue: 400, quantity: 1 }
    ]
  };
};
```

## Test Result Interpretation

### 1. Model Performance Metrics

**R² Score (Coefficient of Determination):**
- 0.99+ = Excellent (our target)
- 0.95-0.99 = Very Good
- 0.90-0.95 = Good
- <0.90 = Needs Improvement

**Mean Absolute Error (MAE):**
- <50 = Excellent (our target)
- 50-100 = Good
- 100-200 = Acceptable
- >200 = Needs Improvement

**Root Mean Square Error (RMSE):**
- <250 = Excellent (our target)  
- 250-500 = Good
- 500-1000 = Acceptable
- >1000 = Needs Improvement

### 2. API Performance Metrics

**Response Time:**
- <10ms = Excellent
- 10-50ms = Good
- 50-100ms = Acceptable
- >100ms = Needs Optimization

**Throughput:**
- >1000 requests/second = Excellent
- 500-1000 requests/second = Good
- 100-500 requests/second = Acceptable
- <100 requests/second = Needs Optimization

### 3. Price Elasticity Validation

**Expected Behavior:**
- 50% price reduction → 50-100% quantity increase
- 50% price increase → 30-60% quantity decrease
- 100% price increase → 60-90% quantity decrease
- Extreme prices (>5x average) → Near-zero quantity

## Troubleshooting Tests

### 1. Model Loading Issues

```bash
# Check model files
ls -la *.pkl

# Test model loading
python -c "from revenue_predictor_time_enhanced_ethical import load_model; load_model()"

# Check dependencies
pip list | grep -E "(lightgbm|pandas|numpy|scikit-learn)"
```

### 2. API Connection Issues

```bash
# Check if API is running
curl -X GET http://localhost:5000/health

# Check port availability
netstat -an | grep 5000

# Check API logs
tail -f api.log
```

### 3. Frontend Issues

```bash
# Check if frontend is running
curl -X GET http://localhost:3000

# Check frontend build
npm run build

# Check browser console for errors
# Open developer tools in browser
```

## Best Practices

### 1. Test-Driven Development
- Write tests before implementing features
- Maintain high test coverage (>80%)
- Use meaningful test names and documentation

### 2. Regular Testing Schedule
- Run quick tests daily during development
- Run full test suite before commits
- Run performance tests weekly
- Run integration tests before releases

### 3. Test Data Quality
- Use realistic test data
- Include edge cases and boundary conditions
- Regularly update test datasets
- Validate test data consistency

### 4. Monitoring and Alerting
- Set up automated test runs
- Monitor test execution times
- Alert on test failures
- Track test coverage metrics

For additional testing scenarios and advanced debugging, refer to the deployment guide and API documentation. 