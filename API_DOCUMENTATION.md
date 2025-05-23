# Revenue Prediction API Documentation

## Overview
This API provides revenue prediction services for small businesses. It uses an XGBoost model trained on a 50/50 split of historical sales data to predict revenue based on various inputs such as product information, pricing, and location data. The model achieves 99.4% accuracy (R² = 0.9947) on the test set.

## Base URL
```
http://localhost:5000
```

## Authentication
Currently, the API does not require authentication as it is designed for internal use only.

## Endpoints

### Health Check
**GET /health**

Checks the status of the API and model.

**Response:**
```json
{
  "status": "online",
  "model_status": "healthy",
  "model_version": "50/50 Split XGBoost",
  "model_message": "Revenue model loaded successfully",
  "data_status": "healthy",
  "data_message": "CSV data loaded successfully",
  "current_data_file": "trainingdataset.csv"
}
```

### Root Endpoint
**GET /**

Basic connectivity check.

**Response:**
```json
{
  "status": "API is running",
  "message": "Welcome to the Revenue Prediction API"
}
```

### List Data Files
**GET /data-files**

Lists all available data files that can be used for predictions.

**Response:**
```json
{
  "files": [
    "Adjusted_Sales_Data_With_Location_100K_ValidDates.csv",
    "Adjusted_Sales_Data_Original.csv"
  ],
  "current_file": "Adjusted_Sales_Data_With_Location_100K_ValidDates.csv",
  "count": 2
}
```

### Select Data File
**POST /select-data-file**

Selects a specific data file to use for subsequent operations.

**Request:**
```json
{
  "filename": "Adjusted_Sales_Data_With_Location_100K_ValidDates.csv"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully loaded data from Adjusted_Sales_Data_With_Location_100K_ValidDates.csv",
  "rows": 100000
}
```

### Get Products
**GET /products**

Returns a list of unique products from the dataset.

**Response:**
```json
[
  {"id": "1", "name": "Product 1"},
  {"id": "2", "name": "Product 2"},
  {"id": "3", "name": "Product 3"}
]
```

### Get Locations
**GET /locations**

Returns a list of unique locations from the dataset.

**Response:**
```json
[
  {"id": "North", "name": "North"},
  {"id": "South", "name": "South"},
  {"id": "East", "name": "East"},
  {"id": "West", "name": "West"}
]
```

### Dashboard Data
**GET /dashboard-data**

Returns aggregated data for dashboard visualizations.

**Response:**
```json
{
  "revenue_data": [
    {"month": "Jan", "revenue": 1234567.89},
    {"month": "Feb", "revenue": 1345678.90}
  ],
  "product_revenue_data": [
    {"name": "Product 2", "revenue": 500000.00},
    {"name": "Product 7", "revenue": 450000.00}
  ],
  "location_revenue_data": [
    {"name": "North", "revenue": 800000.00},
    {"name": "South", "revenue": 750000.00}
  ],
  "top_products_data": [
    {"name": "Product 2", "profit": 250000.00},
    {"name": "Product 7", "profit": 220000.00}
  ],
  "total_revenue": 12345678.90,
  "total_sales": 50000,
  "avg_revenue_per_sale": 246.91
}
```

### Predict Revenue
**POST /predict-revenue**

Predicts revenue using the 50/50 split XGBoost model.

**Request:**
```json
{
  "Unit Price": 100.00,
  "Unit Cost": 50.00,
  "Location": "North",
  "ProductID": 12,
  "Month": 6,
  "Day": 15,
  "Weekday": "Friday"
}
```

**Response:**
```json
{
  "predicted_revenue": 1054.21,
  "confidence_score": 0.994,
  "predicted_quantity": 5,
  "estimated_profit": 250.00
}
```

### Simulate Revenue
**POST /simulate-revenue**

Simulates revenue for different price points using the 50/50 split model.

**Request:**
```json
{
  "base_price": 100.00,
  "unit_cost": 50.00,
  "location": "North",
  "product_id": 12,
  "month": 6,
  "day": 15,
  "weekday": "Friday",
  "price_variations": [-20, -10, 0, 10, 20]
}
```

**Response:**
```json
{
  "base_price": 100.00,
  "variations": [
    {
      "price": 80.00,
      "predicted_revenue": 1030.77,
      "predicted_quantity": 12,
      "profit_margin": 37.5,
      "total_profit": 360.00
    },
    {
      "price": 90.00,
      "predicted_revenue": 1049.52,
      "predicted_quantity": 11,
      "profit_margin": 44.4,
      "total_profit": 440.00
    },
    {
      "price": 100.00,
      "predicted_revenue": 1054.21,
      "predicted_quantity": 10,
      "profit_margin": 50.0,
      "total_profit": 500.00
    },
    {
      "price": 110.00,
      "predicted_revenue": 1073.89,
      "predicted_quantity": 9,
      "profit_margin": 54.5,
      "total_profit": 540.00
    },
    {
      "price": 120.00,
      "predicted_revenue": 1087.26,
      "predicted_quantity": 8,
      "profit_margin": 58.3,
      "total_profit": 560.00
    }
  ],
  "optimal_price": 120.00,
  "optimal_profit": 560.00,
  "price_elasticity": -0.42
}
```

### Get Data
**GET /data**

Returns a sample of the current dataset.

**Response:**
```json
{
  "count": 100000,
  "sample": [
    {
      "Location": "North",
      "_ProductID": 12,
      "Order Quantity": 5,
      "Unit Cost": 50,
      "Unit Price": 100,
      "Total Cost": 250,
      "Total Revenue": 500,
      "Profit": 250
    }
  ],
  "columns": ["Location", "_ProductID", "Order Quantity", "Unit Cost", "Unit Price", "Total Cost", "Total Revenue", "Profit"]
}
```

### Reload
**GET /reload**

Reloads the model and data files.

**Response:**
```json
{
  "status": "success",
  "message": "Reloaded models and data files",
  "model_status": "healthy",
  "model_message": "Revenue model reloaded successfully",
  "files": ["Adjusted_Sales_Data_With_Location_100K_ValidDates.csv", "Adjusted_Sales_Data_Original.csv"]
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- 200: Successful request
- 400: Bad request (invalid parameters)
- 404: Resource not found
- 500: Server error

Error responses include a descriptive message:

```json
{
  "error": "Missing required fields: Unit Price, Unit Cost"
}
```

## Data Types

### Input Fields
- **Unit Price**: Float (required) - Selling price per unit
- **Unit Cost**: Float (required) - Cost per unit
- **Location**: String (required) - Regional location
- **ProductID**: Integer (required) - Product identifier
- **Month**: Integer (required) - Month of the order (1-12)
- **Day**: Integer (required) - Day of the month (1-31)
- **Weekday**: String (required) - Day of the week (Monday-Sunday)

### Output Fields
- **predicted_revenue**: Float - Predicted total revenue
- **confidence_score**: Float - Confidence score of the prediction
- **predicted_quantity**: Integer - Predicted number of units ordered
- **estimated_profit**: Float - Estimated profit (revenue - total cost)

## Model Information
- **Algorithm**: XGBoost
- **Features**: Unit Price, Unit Cost, Location, Product ID, Month, Day, Weekday
- **Performance**: R² = 0.9947 (on test set)

See [MODEL_DOCUMENTATION.md](MODEL_DOCUMENTATION.md) for detailed model information.

# IDSS API Documentation

This document provides detailed information about the IDSS API for revenue and quantity prediction.

## Base URL

```
http://localhost:5000
```

## API Status

### Get API Status

**Endpoint:** `/status`  
**Method:** GET  
**Description:** Check the status of the API and the loaded models.

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running",
  "model_status": "healthy",
  "model_message": "Models loaded successfully"
}
```

## Data Management

### Get Available Data Files

**Endpoint:** `/files`  
**Method:** GET  
**Description:** Get a list of available data files for analysis.

**Response:**
```json
{
  "files": [
    "data/Adjusted_Sales_Data_With_Location_100K_ValidDates.csv"
  ]
}
```

### Get Data Sample

**Endpoint:** `/data`  
**Method:** GET  
**Description:** Get a sample of the latest data file (first 100 rows by default).

**Query Parameters:**
- `file` (optional): The specific file to load
- `limit` (optional): Number of rows to return (default: 100)

**Response:**
```json
{
  "data": [
    {
      "Month": 1,
      "Day": 15,
      "Weekday": "Monday",
      "Unit Price": 120.5,
      "Unit Cost": 90.25,
      "Order Quantity": 5,
      "Total Revenue": 602.5,
      "Location": "North",
      "_ProductID": 101
    },
    ...
  ],
  "count": 100,
  "file": "data/Adjusted_Sales_Data_With_Location_100K_ValidDates.csv"
}
```

## Revenue Prediction (with Quantity)

### Predict Revenue

**Endpoint:** `/predict-revenue`  
**Method:** POST  
**Description:** Predict the revenue for a given input set with Order Quantity.

**Request:**
```json
{
  "Unit Price": 100,
  "Unit Cost": 50,
  "Order Quantity": 5,
  "Month": 6,
  "Day": 15,
  "Weekday": "Friday",
  "Location": "North",
  "_ProductID": 12
}
```

**Response:**
```json
{
  "predicted_revenue": 1054.21,
  "order_quantity": 5,
  "profit": 804.21
}
```

### Simulate Revenue with Price Variations

**Endpoint:** `/simulate-revenue`  
**Method:** POST  
**Description:** Simulate revenue and profit for different price points.

**Request:**
```json
{
  "Unit Price": 100,
  "Unit Cost": 50,
  "Order Quantity": 5,
  "Month": 6,
  "Day": 15,
  "Weekday": "Friday",
  "Location": "North",
  "_ProductID": 12,
  "price_variations": [80, 90, 100, 110, 120]
}
```

**Response:**
```json
{
  "base_price": 100,
  "base_quantity": 5,
  "elasticity": -1.5,
  "variations": [
    {"unit_price": 80, "revenue": 1030.77, "quantity": 8, "profit": 830.77},
    {"unit_price": 90, "revenue": 1049.52, "quantity": 6, "profit": 799.52},
    {"unit_price": 100, "revenue": 1054.21, "quantity": 5, "profit": 804.21},
    {"unit_price": 110, "revenue": 1035.92, "quantity": 4, "profit": 835.92},
    {"unit_price": 120, "revenue": 1000.56, "quantity": 3, "profit": 850.56}
  ],
  "optimal_revenue_price": {
    "price": 100,
    "revenue": 1054.21,
    "quantity": 5,
    "profit": 804.21
  },
  "optimal_profit_price": {
    "price": 120,
    "revenue": 1000.56,
    "quantity": 3,
    "profit": 850.56
  }
}
```

## Direct Revenue Prediction (without Quantity)

### Predict Revenue Directly

**Endpoint:** `/predict-revenue-direct`  
**Method:** POST  
**Description:** Predict the revenue for a given input set without requiring Order Quantity.

**Request:**
```json
{
  "Unit Price": 100,
  "Unit Cost": 50,
  "Month": 6,
  "Day": 15,
  "Weekday": "Friday",
  "Location": "North",
  "_ProductID": 12
}
```

**Response:**
```json
{
  "predicted_revenue": 8423.50,
  "estimated_quantity": 84,
  "profit": 4223.50
}
```

### Simulate Revenue with Price Variations

**Endpoint:** `/simulate-revenue-direct`  
**Method:** POST  
**Description:** Simulate revenue and profit for different price points without requiring Order Quantity.

**Request:**
```json
{
  "Unit Price": 100,
  "Unit Cost": 50,
  "Month": 6,
  "Day": 15,
  "Weekday": "Friday",
  "Location": "North",
  "_ProductID": 12,
  "price_variations": [50, 70, 90, 100, 120, 150, 200]
}
```

**Response:**
```json
{
  "base_price": 100,
  "unit_cost": 50,
  "model_type": "direct prediction (no quantity input)",
  "variations": [
    {"unit_price": 50.00, "quantity": 120, "revenue": 6000.00, "profit": 0.00},
    {"unit_price": 70.00, "quantity": 95, "revenue": 6650.00, "profit": 1900.00},
    {"unit_price": 90.00, "quantity": 82, "revenue": 7380.00, "profit": 3280.00},
    {"unit_price": 100.00, "quantity": 84, "revenue": 8400.00, "profit": 4200.00},
    {"unit_price": 120.00, "quantity": 73, "revenue": 8760.00, "profit": 5140.00},
    {"unit_price": 150.00, "quantity": 58, "revenue": 8700.00, "profit": 5800.00},
    {"unit_price": 200.00, "quantity": 38, "revenue": 7600.00, "profit": 5700.00}
  ],
  "optimal_revenue_price": {
    "price": 120.00,
    "revenue": 8760.00,
    "quantity": 73,
    "profit": 5140.00
  },
  "optimal_profit_price": {
    "price": 150.00,
    "revenue": 8700.00,
    "quantity": 58,
    "profit": 5800.00
  }
}
```

## Quantity Prediction

### Predict Quantity

**Endpoint:** `/predict-quantity`  
**Method:** POST  
**Description:** Predict the order quantity for a given input set.

**Request:**
```json
{
  "Unit Price": 100,
  "Unit Cost": 50,
  "Month": 6,
  "Day": 15,
  "Weekday": "Friday",
  "Location": "North",
  "_ProductID": 12
}
```

**Response:**
```json
{
  "predicted_quantity": 5,
  "unit_price": 100,
  "predicted_revenue": 500,
  "profit": 250
}
```

### Simulate Quantity with Price Variations

**Endpoint:** `/simulate-quantity`  
**Method:** POST  
**Description:** Simulate order quantity for different price points.

**Request:**
```json
{
  "Unit Price": 100,
  "Unit Cost": 50,
  "Month": 6,
  "Day": 15,
  "Weekday": "Friday",
  "Location": "North",
  "_ProductID": 12,
  "price_variations": [80, 90, 100, 110, 120]
}
```

**Response:**
```json
{
  "base_price": 100,
  "variations": [
    {"unit_price": 80, "quantity": 8, "revenue": 640, "profit": 240},
    {"unit_price": 90, "quantity": 6, "revenue": 540, "profit": 240},
    {"unit_price": 100, "quantity": 5, "revenue": 500, "profit": 250},
    {"unit_price": 110, "quantity": 4, "revenue": 440, "profit": 240},
    {"unit_price": 120, "quantity": 3, "revenue": 360, "profit": 210}
  ],
  "optimal_revenue_price": {
    "price": 80,
    "quantity": 8,
    "revenue": 640,
    "profit": 240
  },
  "optimal_profit_price": {
    "price": 100,
    "quantity": 5,
    "revenue": 500,
    "profit": 250
  }
}
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- 200: Success
- 400: Bad request (missing or invalid parameters)
- 404: Endpoint not found
- 500: Server error

Error responses include a descriptive message:

```json
{
  "error": "Missing required field: Unit Price"
}
```

## Comparison of Prediction Methods

The IDSS system supports three approaches to revenue prediction:

1. **Quantity-First Approach**: 
   - First predict quantity, then calculate revenue as `Unit Price × Predicted Quantity`
   - Endpoints: `/predict-quantity`, `/simulate-quantity`
   - Best used when: You want to understand demand sensitivity to price changes

2. **Revenue Prediction with Quantity**: 
   - Directly predict revenue using Order Quantity as an input feature
   - Endpoints: `/predict-revenue`, `/simulate-revenue`
   - Best used when: You have a known quantity and need precise revenue prediction

3. **Direct Revenue Prediction (No Quantity)**: 
   - Directly predict revenue without requiring Order Quantity
   - Endpoints: `/predict-revenue-direct`, `/simulate-revenue-direct`
   - Best used when: You need to forecast revenue without knowing the quantity in advance

Each approach has different performance characteristics:
- Quantity-First: R² ≈ 0.25 (quantity model)
- Revenue with Quantity: R² ≈ 1.00
- Direct Revenue without Quantity: R² ≈ 0.49

## API Testing

To test the API, you can use the provided test scripts:

- `test_api.py`: Tests basic API functionality
- `test_revenue_api.py`: Tests revenue prediction endpoints
- `test_direct_revenue_api.py`: Tests direct revenue prediction endpoints

Run these scripts after starting the API server to ensure everything is working properly.

---
*API Documentation last updated: [current_date]* 