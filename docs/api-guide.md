# API Documentation

This guide covers the comprehensive API endpoints available in the Revenue Prediction System.

## Overview

The system provides two API layers:
- **Flask Backend API** (Port 5000): Core ML model and data processing
- **Next.js API Routes** (Port 3000): Frontend integration and proxying

## Flask Backend API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model": "ethical_time_enhanced"
}
```

### Revenue Prediction
```http
POST /predict-revenue
```

**Request Body:**
```json
{
  "Unit Price": 100.0,
  "Unit Cost": 50.0,
  "Location": "North",
  "_ProductID": 1,
  "Year": 2024,
  "Month": 1,
  "Day": 15,
  "Weekday": "Monday"
}
```

**Response:**
```json
{
  "predicted_revenue": 1234.56,
  "quantity": 12,
  "profit": 600.0,
  "profit_margin": 0.486,
  "input_data": { /* original input */ },
  "model_version": "ethical_time_enhanced"
}
```

### Price Scenario Simulation
```http
POST /simulate-revenue
```

**Request Body:**
```json
{
  "Unit Price": 100.0,
  "Unit Cost": 50.0,
  "Location": "North",
  "_ProductID": 1,
  "min_price_factor": 0.5,
  "max_price_factor": 2.0,
  "steps": 7
}
```

**Response:**
```json
{
  "variations": [
    {
      "price_factor": 0.5,
      "unit_price": 50.0,
      "predicted_revenue": 800.0,
      "quantity": 16,
      "profit": 200.0,
      "scenario_name": "50% Lower"
    }
  ],
  "base_price": 100.0,
  "note": "Aggregated prediction across all locations"
}
```

### Price Optimization
```http
POST /optimize-price
```

**Request Body:**
```json
{
  "Unit Price": 100.0,
  "Unit Cost": 50.0,
  "Location": "North",
  "_ProductID": 1,
  "metric": "revenue",
  "min_price_factor": 0.5,
  "max_price_factor": 3.0,
  "steps": 20
}
```

**Response:**
```json
{
  "optimal_price": 156.25,
  "optimal_value": 2450.67,
  "metric": "revenue",
  "improvement": 98.4,
  "improvement_percentage": 4.18
}
```

### Sales Forecasting
```http
POST /forecast-sales
```

**Request Body:**
```json
{
  "Unit Price": 100.0,
  "Unit Cost": 50.0,
  "Location": "North",
  "_ProductID": 1,
  "days": 30,
  "confidence_interval": true,
  "ci_level": 0.9
}
```

**Response:**
```json
{
  "forecast": [
    {
      "date": "2024-01-15",
      "predicted_revenue": 1234.56,
      "quantity": 12,
      "profit": 600.0,
      "ci_lower": 1100.0,
      "ci_upper": 1400.0
    }
  ],
  "summary": {
    "total_revenue": 37036.8,
    "avg_daily_revenue": 1234.56,
    "total_quantity": 360
  }
}
```

### Multi-Product Forecasting
```http
POST /forecast-multiple
```

**Request Body:**
```json
{
  "products": [
    {
      "Unit Price": 100.0,
      "Unit Cost": 50.0,
      "Location": "North",
      "_ProductID": 1
    }
  ],
  "days": 30
}
```

### Price Trend Analysis
```http
POST /forecast-trend
```

**Request Body:**
```json
{
  "Unit Price": 100.0,
  "Unit Cost": 50.0,
  "Location": "North",
  "_ProductID": 1,
  "days": 30,
  "price_points": 5
}
```

### Dashboard Data
```http
GET /dashboard-data
```

**Response:**
```json
{
  "revenue_data": [
    {
      "month": "1/2024",
      "revenue": 15000.50,
      "profit": 6000.20
    }
  ],
  "product_revenue_data": [
    {
      "id": 1,
      "product": "Product 1",
      "name": "Product 1",
      "revenue": 5000.0
    }
  ],
  "location_data": [
    {
      "name": "North",
      "revenue": 12000.0
    }
  ],
  "top_products_data": [
    {
      "id": 1,
      "name": "Product 1",
      "profit": 2500.0,
      "revenue": 5000.0,
      "quantity": 100,
      "margin": 0.5,
      "rank": "top"
    }
  ],
  "summary": {
    "total_revenue": 50000.0,
    "total_sales": 150,
    "avg_revenue": 333.33
  },
  "status": "success"
}
```

### Business Insights
```http
GET /business-insights
```

**Response:**
```json
{
  "insights": [
    {
      "type": "Revenue",
      "severity": "High",
      "title": "High Revenue Variance Detected",
      "description": "Revenue shows high variance (σ=1250.45, μ=2500.00). Consider stabilizing pricing strategy.",
      "impact": "Medium",
      "recommendation": "Analyze top-performing periods and replicate successful strategies",
      "category": "Revenue"
    }
  ],
  "total_count": 1,
  "status": "success"
}
```

## Next.js API Routes

### Product Data
```http
GET /api/products
```

**Response:**
```json
[
  { "id": "1", "name": "Product 1" },
  { "id": "2", "name": "Product 2" }
]
```

### Location Data
```http
GET /api/locations
```

**Response:**
```json
[
  { "id": "North", "name": "North" },
  { "id": "South", "name": "South" }
]
```

### Product Details
```http
GET /api/product-data
```

**Response:**
```json
{
  "products": [
    {
      "id": 1,
      "avgPrice": 5012.34,
      "avgCost": 1900.50
    }
  ],
  "status": "success",
  "file_info": "trainingdataset.csv"
}
```

### Simulation Proxy
```http
POST /api/simulate-revenue
```

Proxies requests to Flask backend with proper field mapping.

### Dashboard Data Proxy
```http
GET /api/dashboard-data
```

Proxies requests to Flask backend with consistency validation.

### Business Insights Proxy
```http
GET /api/insights
```

Proxies requests to Flask backend for business insights.

### File Upload
```http
POST /api/upload-csv
```

**Request:** Multipart form data with CSV file

**Response:**
```json
{
  "success": true,
  "filename": "data_2024-01-15T10-30-00-000Z.csv",
  "message": "File uploaded successfully to data directory"
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error description",
  "status": "error"
}
```

HTTP status codes:
- 200: Success
- 400: Bad Request (validation errors)
- 404: Not Found (missing data)
- 500: Internal Server Error

## Rate Limiting

No rate limiting is currently implemented. For production deployment, consider implementing rate limiting to prevent abuse.

## Best Practices

1. **Input Validation**: Always validate input data before making API calls
2. **Error Handling**: Implement proper error handling for all API calls
3. **Caching**: Use appropriate caching strategies for static data
4. **Monitoring**: Monitor API performance and errors in production
5. **Security**: Implement authentication and authorization for production use

## Authentication

Currently, no authentication is required. For production deployment, implement proper authentication mechanisms.

## Data Formats

### Dates
- Use YYYY-MM-DD format for dates
- Weekday names: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday

### Currency
- All monetary values are in USD
- Use decimal numbers (e.g., 1234.56)

### Product IDs
- Integer values (e.g., 1, 2, 3)
- Consistent with training data

### Locations
- String values matching training data
- Case-sensitive: "North", "South", "East", "West", "Central"

## Response Times

Typical response times:
- Revenue prediction: <50ms
- Price simulation: <200ms
- Sales forecasting: <500ms
- Dashboard data: <300ms
- Business insights: <200ms

## Data Requirements

### Minimum Required Fields
- Unit Price (positive number)
- Unit Cost (positive number)
- Location (valid location string)
- _ProductID (valid product ID)

### Optional Fields
- Year (defaults to current year)
- Month (defaults to current month)
- Day (defaults to current day)
- Weekday (defaults to current weekday)

## Integration Examples

### JavaScript/TypeScript
```typescript
// Revenue prediction
const response = await fetch('/api/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    'Unit Price': 100,
    'Unit Cost': 50,
    'Location': 'North',
    '_ProductID': 1
  })
});

const result = await response.json();
```

### Python
```python
import requests

response = requests.post('http://localhost:5000/predict-revenue', json={
    'Unit Price': 100,
    'Unit Cost': 50,
    'Location': 'North',
    '_ProductID': 1
})

result = response.json()
```

### cURL
```bash
curl -X POST http://localhost:5000/predict-revenue \
  -H "Content-Type: application/json" \
  -d '{
    "Unit Price": 100,
    "Unit Cost": 50,
    "Location": "North",
    "_ProductID": 1
  }'
``` 