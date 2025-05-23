# Revenue Prediction Model Documentation (50/50 Split)

## Executive Summary

This documentation describes our revenue prediction system for small businesses, focusing on the **XGBoost Revenue Prediction Model with 50/50 Split**. The system provides accurate revenue predictions and pricing insights for strategic decision-making, achieving an exceptional **R² = 0.9947** on the test set.

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

### Model Performance
- **R² Score:** 0.9947 (test set)
- **Prediction Latency:** <1ms per prediction
- **Price Elasticity:** -0.42 (average)

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

## Maintenance

The model should be:
1. Retrained monthly with new data
2. Validated against actual revenues
3. Updated for new products/locations
4. Monitored for drift and performance

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API usage. 