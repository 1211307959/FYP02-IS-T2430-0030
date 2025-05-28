# Revenue Prediction API Documentation

## Overview
This API provides revenue prediction services for small businesses. It uses an XGBoost model trained on a 50/50 split of historical sales data to predict revenue based on various inputs such as product information, pricing, and location data. The model achieves 99.4% accuracy (R² = 0.9947) on the test set. The system now automatically combines all CSV files in the data directory for comprehensive analysis.

## Base URL
```
http://localhost:5000
```

## Authentication
Currently, the API does not require authentication as it is designed for internal use only.

## Data Processing
The system now automatically processes all CSV files in the data directory:

1. **Automatic Combination:**
   - All CSV files in the data folder are loaded simultaneously
   - Data is combined into a unified dataset for analysis
   - No manual file selection required

2. **Column Compatibility:**
   - System automatically identifies common columns across all files
   - Only shared columns are used in the combined dataset
   - Source file tracking is maintained for advanced analysis

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
  "data_message": "Combined data loaded successfully from 3 files",
  "files_count": 3,
  "combined_rows": 250000
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

Lists all available data files in the data directory that are being combined for predictions.

**Response:**
```json
{
  "status": "success",
  "files": [
    "Adjusted_Sales_Data_With_Location_100K_ValidDates.csv",
    "Adjusted_Sales_Data_Original.csv",
    "seasonal_data.csv"
  ],
  "current_mode": "combined",
  "message": "Using combined data from 3 files"
}
```

### Reload Data Files
**GET /reload**

Reloads all data files from the data directory and rebuilds the combined dataset.

**Response:**
```json
{
  "status": "success",
  "message": "Combined data loaded from 3 files with 250000 total rows",
  "files": [
    "Adjusted_Sales_Data_With_Location_100K_ValidDates.csv",
    "Adjusted_Sales_Data_Original.csv",
    "seasonal_data.csv"
  ]
}
```

### Get Products
**GET /products**

Returns a list of unique products from the combined dataset.

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

Returns a list of unique locations from the combined dataset.

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

Returns aggregated data for dashboard visualizations from the combined dataset.

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

Predicts revenue using the 50/50 split XGBoost model based on the combined dataset.

**Request:**
```json
{
  "Unit Price": 100.00,
  "Unit Cost": 50.00,
  "Location": "North",
  "_ProductID": 12,
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

Simulates revenue for different price points using the 50/50 split model with insights from the combined dataset.

**Request:**
```json
{
  "Unit Price": 100.00,
  "Unit Cost": 50.00,
  "Location": "North",
  "_ProductID": 12,
  "Month": 6,
  "Day": 15,
  "Weekday": "Friday",
  "min_price_factor": 0.5,
  "max_price_factor": 2.0,
  "steps": 7
}
```

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "Scenario": "50% of Price",
      "Unit Price": 50.00,
      "Predicted Revenue": 850.00,
      "Predicted Quantity": 17,
      "Profit": 450.00
    },
    {
      "Scenario": "75% of Price",
      "Unit Price": 75.00,
      "Predicted Revenue": 975.00,
      "Predicted Quantity": 13,
      "Profit": 525.00
    },
    {
      "Scenario": "100% of Price",
      "Unit Price": 100.00,
      "Predicted Revenue": 1054.21,
      "Predicted Quantity": 10,
      "Profit": 500.00
    },
    {
      "Scenario": "125% of Price",
      "Unit Price": 125.00,
      "Predicted Revenue": 1087.50,
      "Predicted Quantity": 8,
      "Profit": 600.00
    },
    {
      "Scenario": "150% of Price",
      "Unit Price": 150.00,
      "Predicted Revenue": 1050.00,
      "Predicted Quantity": 7,
      "Profit": 700.00
    },
    {
      "Scenario": "175% of Price",
      "Unit Price": 175.00,
      "Predicted Revenue": 875.00,
      "Predicted Quantity": 5,
      "Profit": 625.00
    },
    {
      "Scenario": "200% of Price",
      "Unit Price": 200.00,
      "Predicted Revenue": 600.00,
      "Predicted Quantity": 3,
      "Profit": 450.00
    }
  ],
  "simulations": [
    // Same content as results
  ]
}
```

### Get Data
**GET /data**

Returns a sample of the current combined dataset.

**Response:**
```json
{
  "count": 250000,
  "combined_from": 3,
  "sample": [
    {
      "Location": "North",
      "_ProductID": 12,
      "Unit Price": 100.00,
      "Unit Cost": 50.00,
      "Month": 6,
      "Day": 15,
      "Weekday": "Friday",
      "Year": 2022,
      "Total Revenue": 1050.00,
      "Quantity": 10,
      "_source_file": "Adjusted_Sales_Data_With_Location_100K_ValidDates.csv"
    },
    // More samples...
  ]
}
```

### Upload File
**POST /upload-file**

Uploads a new CSV file to the data directory. The file will be automatically included in the combined dataset.

**Request:**
Form data with file field containing a CSV file.

**Response:**
```json
{
  "status": "success",
  "filename": "new_sales_data.csv",
  "message": "File uploaded successfully: new_sales_data.csv"
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad request (e.g., invalid input)
- 404: Resource not found
- 500: Server error

Error responses have the following format:
```json
{
  "error": "Detailed error message"
}
```

## Data Requirements

For optimal performance when adding new CSV files, ensure they include the following columns:
- `_ProductID`: Product identifier (required)
- `Unit Price`: Price of the product (required)
- `Unit Cost`: Cost of the product (required)
- `Location`: Geographic region (required)
- `Month`: Month of transaction (1-12)
- `Day`: Day of month (1-31)
- `Weekday`: Day of week (e.g., "Monday")
- `Year`: Year of transaction
- `Total Revenue`: Total revenue for the transaction (for training data)
- `Quantity`: Number of units sold (for training data)

The system will automatically identify common columns across all files and use them in the combined dataset.

## Best Practices

1. **Data Files:**
   - Use consistent column names across all CSV files
   - Ensure date-related fields are properly formatted
   - Include all required columns for best prediction results

2. **API Usage:**
   - Use the `/health` endpoint to verify API status before making predictions
   - Regularly check `/data-files` to confirm which files are being used
   - After uploading new files, call `/reload` to ensure data is refreshed

3. **Predictions:**
   - Use the `/simulate-revenue` endpoint to test different price points
   - Include all context fields (location, dates, etc.) for most accurate predictions
   - For new products, use similar existing products as references

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