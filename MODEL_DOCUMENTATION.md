# Revenue Prediction Model Documentation (50/50 Split)

## Executive Summary

This documentation describes our revenue prediction system for small businesses, focusing on the **XGBoost Revenue Prediction Model with 50/50 Split**. The system provides accurate revenue predictions and pricing insights for strategic decision-making, achieving an exceptional **R² = 0.9947** on the test set. The system now features automatic multi-file data processing, combining all available CSV files for comprehensive analysis.

## Model Architecture

### Core Model Information
- **Algorithm:** XGBoost Regressor
- **Training Data:** 50% of the dataset (randomly selected)
- **Target Variable:** Total Revenue
- **Training/Test Split:** 50/50 split
- **Cross-Validation:** 5-fold CV
- **Model Files:**
  - `best_revenue_model.pkl` (Trained model)
  - `revenue_encoders.pkl` (Feature encoders)
- **Data Processing:**
  - Automatic combination of all data files
  - Common column detection across files
  - Source tracking for advanced analysis

### Model Performance
- **R² Score:** 0.9947 (test set)
- **Prediction Latency:** <1ms per prediction
- **Price Elasticity:** -0.42 (average)
- **Multi-file Performance:** Scales linearly with data volume

### Key Features
Feature importance ranking:
1. **Price_vs_Product_Avg (18.21%)** - Price relative to product average
2. **Unit Price (9.32%)** - Direct price input
3. **ProductID_Encoded (9.07%)** - Product identifier
4. **Price_Seasonal_Deviation (6.57%)** - Seasonal price patterns
5. **Price_Popularity (6.31%)** - Price-popularity interaction

### Feature Engineering
1. **Price Features**
   - Unit price and cost
   - Price ratios and margins
   - Historical price patterns

2. **Temporal Features**
   - Month and day
   - Weekday encoding
   - Seasonal indicators

3. **Location Features**
   - Regional encoding
   - Location-specific patterns
   - Geographic price variations

4. **Product Features**
   - Product category
   - Historical performance
   - Product popularity metrics

5. **Multi-file Features**
   - Source file tracking
   - Cross-file pattern detection
   - Aggregated metrics across datasets

## Data Handling

### Multi-File Processing
The system now automatically processes all CSV files in the data directory:

1. **Automatic Combination:**
   - All CSV files in the data folder are loaded simultaneously
   - Data is combined into a unified dataset for analysis
   - No manual file selection required

2. **Column Compatibility:**
   - System automatically identifies common columns across all files
   - Only shared columns are used in the combined dataset
   - Source file tracking is maintained for advanced analysis

3. **Benefits:**
   - Work with multiple data sources simultaneously
   - No need to merge files manually
   - Richer dataset for more accurate predictions
   - Maintain historical context across files

4. **Compatibility Requirements:**
   - Files must share core columns (ProductID, Unit Price, etc.)
   - CSV format required for all files
   - Column names must be consistent across files

## Dynamic Data Handling

The system has been designed to be 100% data-driven, without relying on hardcoded values. This ensures that it can adapt to new data and changes in the dataset, such as:

1. **Dynamic Locations**: Locations are read directly from the data files, not hardcoded in the application.
   - Includes an "All Locations" option for aggregated data views
   - Location filtering adapts automatically to the available data

2. **Dynamic Products**: Product IDs and details are extracted from the data files.

3. **Default Values**: When default values are needed, they are sourced from the actual data rather than being hardcoded.

4. **Adaptive UI**: The UI dynamically adjusts to reflect the actual data, including products, locations, prices, and costs.

### All Locations Option

The system provides an "All Locations" option that:

- Appears at the top of the location dropdown for easy access
- Allows users to view data from all locations simultaneously
- Uses default location values for model predictions when necessary
- Provides appropriate UI feedback when "All Locations" is selected
- Maintains the same data format for consistent API integration

This approach offers several benefits:

- **Flexibility**: The system can handle new locations or products added to the dataset without code changes.
- **Maintainability**: No need to update hardcoded values when the data changes.
- **Consistency**: Ensures that all parts of the application use the same data source.
- **Future-proofing**: Makes it easier to adapt the system for different datasets or business scenarios.

The dynamic approach is implemented at multiple levels:

- **Backend API**: Reads data directly from CSV files and model encoders.
- **Next.js API Routes**: Source data from the backend API and provide fallbacks only as a last resort.
- **Frontend Components**: Load data dynamically from API endpoints with proper error handling.

This design ensures that adding new data (such as a new location or product) requires no code changes - the system will automatically incorporate the new data throughout the application.

## API Integration

### Revenue Prediction
**Endpoint:** `/predict-revenue`
```json
// Request
{
  "Unit Price": 100.00,
  "Unit Cost": 50.00,
  "Location": "North",
  "ProductID": 12,
  "Month": 6,
  "Day": 15,
  "Weekday": "Friday"
}

// Response
{
  "predicted_revenue": 1054.21,
  "confidence_score": 0.994,
  "predicted_quantity": 5,
  "estimated_profit": 250.00
}
```

### Price Simulation
**Endpoint:** `/simulate-revenue`
```json
// Request
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

// Response
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
    // ... additional variations ...
  ],
  "optimal_price": 120.00,
  "optimal_profit": 560.00,
  "price_elasticity": -0.42
}
```

### Multi-File Data Access
**Endpoint:** `/data-files`
```json
// Response
{
  "status": "success",
  "files": ["sales_2022.csv", "sales_2023.csv", "seasonal_data.csv"],
  "current_mode": "combined",
  "message": "Using combined data from 3 files"
}
```

## Business Benefits

1. **High Accuracy**
   - 99.4% accuracy in revenue predictions
   - Robust performance across different scenarios

2. **Price Optimization**
   - Automatic optimal price discovery
   - Profit margin analysis
   - Price elasticity insights

3. **Business Intelligence**
   - Location-based insights
   - Seasonal trend analysis
   - Product performance metrics

4. **Fast Predictions**
   - Sub-millisecond response time
   - Suitable for real-time applications
   - Batch prediction support

5. **Multi-file Analysis**
   - Work with all data sources simultaneously
   - No need for manual data merging
   - Comprehensive view across different periods and sources

## Usage Examples

```python
from revenue_predictor_50_50 import RevenuePredictor

# Initialize predictor
predictor = RevenuePredictor()

# Make prediction
result = predictor.predict({
    'Unit Price': 100.00,
    'Unit Cost': 50.00,
    'Location': 'North',
    'ProductID': 12,
    'Month': 6,
    'Day': 15,
    'Weekday': 'Friday'
})

# Simulate prices
simulation = predictor.simulate_prices({
    'base_price': 100.00,
    'unit_cost': 50.00,
    'variations': [-20, -10, 0, 10, 20]
})
```

## Model Limitations

1. **Price Range**
   - Most accurate for prices within ±50% of historical average
   - May need recalibration for extreme price points

2. **Seasonal Patterns**
   - Requires sufficient historical data per season
   - Best performance with complete yearly cycles

3. **New Products**
   - Limited accuracy for entirely new products
   - Requires similar product history for best results

4. **Multi-file Requirements**
   - Files must share common core columns
   - Performance may degrade with highly inconsistent data formats
   - Large combined datasets may require more memory

## Future Improvements

1. **Model Updates**
   - Regular retraining with new data
   - Automated feature selection
   - Dynamic hyperparameter optimization

2. **Additional Features**
   - Market competition data
   - Economic indicators
   - Weather patterns

3. **Enhanced Analytics**
   - Confidence intervals
   - Risk assessment
   - Anomaly detection

4. **Advanced Multi-file Processing**
   - Intelligent column mapping for inconsistent files
   - Automated data quality assessment
   - Cross-file pattern recognition

## Maintenance

The model should be:
1. Retrained monthly with new data
2. Validated against actual revenues
3. Updated for new products/locations
4. Monitored for drift and performance
5. Data directory should be regularly backed up

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API usage. 