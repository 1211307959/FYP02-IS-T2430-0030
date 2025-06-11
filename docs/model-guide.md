# Model Guide - Ethical Time-Enhanced Revenue Prediction

## Overview
This documentation describes the **Ethical Time-Enhanced LightGBM Revenue Model** - our production-ready machine learning model that provides high-accuracy revenue predictions while maintaining strict ethical standards by eliminating all target leakage.

## Current Production Model

**Ethical Time-Enhanced Model** - The production-ready model that eliminates target leakage while maintaining exceptional accuracy (R² = 0.9937). This is the recommended model for all production use cases.

## Model Architecture

### Core Model Information
- **Algorithm:** LightGBM Regressor
- **Training Data:** 50% of the dataset (randomly selected)
- **Target Variable:** Total Revenue (log-transformed)
- **Training/Test Split:** 50/50 split
- **Model Files:**
  - `revenue_model_time_enhanced_ethical.pkl` (Trained model)
  - `revenue_encoders_time_enhanced_ethical.pkl` (Feature encoders)
  - `reference_data_time_enhanced_ethical.pkl` (Reference statistics)

### Model Performance
- **R² Score:** 0.9937 (test set)
- **MAE:** 48.0644
- **RMSE:** 238.3702
- **Prediction Latency:** <1ms per prediction
- **Price Elasticity:** Dynamic elasticity that varies by price level

### Key Features
Feature importance ranking:
1. **Price_vs_Product_Avg (37.81%)** - Price relative to product average
2. **Unit Price (19.56%)** - Direct price input
3. **Price_Seasonal_Deviation (18.86%)** - Seasonal price variation
4. **Price_Popularity (18.06%)** - Price-popularity interaction
5. **Price_to_Cost_Ratio (12.79%)** - Price/cost relationship

## Time-Based Features
The model includes sophisticated temporal features without using target leakage:

### 1. Cyclical Time Encodings
- Month sine/cosine transformations
- Day of year sine/cosine
- Week of year sine/cosine
- Proper handling of cyclical time patterns

### 2. Calendar Features
- Day of year (1-366)
- Week of year (1-53)
- Quarter
- Seasons (Winter, Spring, Summer, Fall)

### 3. Special Period Detection
- Holiday season flag
- Weekend detection
- Specific holiday flags

### 4. Temporal Interactions
- Product-Month price patterns
- Product-Quarter price patterns
- Location-Month price patterns
- Weekend-Location price patterns
- Product-Weekend price patterns

## Ethical vs. Non-Ethical Model

The previous model achieved a perfect R² = 1.0000 but did so by using target leakage features. This ethical model specifically removes these problematic features:

### Removed Leaking Features
- `Revenue_Weekday_Ratio` - Used target (revenue) to create a ratio
- `Revenue_Month_Ratio` - Used target (revenue) to create a ratio
- `Location_Weekend_Revenue_mean` - Used revenue in group statistics
- `Product_Weekend_Revenue_mean` - Used revenue in group statistics

### Performance Comparison
- **Non-Ethical Model:** R² = 1.0000, MAE = 4.2224, RMSE = 7.6776
- **Ethical Model:** R² = 0.9937, MAE = 48.0644, RMSE = 238.3702

### Importance Shift
- Non-ethical model relied heavily on direct revenue-derived features
- Ethical model focuses on price relationships and temporal patterns

## Enhanced Feature Engineering

### Advanced Time Features
The ethical time-enhanced model introduces sophisticated temporal feature engineering:

#### 1. Cyclical Encoding
```python
df['Month_Sin'] = np.sin(2 * np.pi * df['Month'] / 12)
df['Month_Cos'] = np.cos(2 * np.pi * df['Month'] / 12)
```
This prevents the model from seeing December and January as vastly different, capturing the cyclical nature of time.

#### 2. Seasonal Indicators
```python
df['Is_Winter'] = ((df['Month'] == 12) | (df['Month'] == 1) | (df['Month'] == 2)).astype(int)
df['Is_Spring'] = ((df['Month'] == 3) | (df['Month'] == 4) | (df['Month'] == 5)).astype(int)
```
These features explicitly encode seasonal patterns.

#### 3. Holiday Detection
```python
holidays = [(1, 1), (7, 4), (12, 25), ...]  # Key dates
df['Is_Holiday'] = df.apply(lambda row: 1 if (row['Month'], row['Day']) in holidays else 0, axis=1)
```
The model recognizes special holidays that may affect business patterns.

### Ethical Interaction Features
The model creates powerful interaction features without using the target variable:

#### 1. Product-Time Interactions
```python
# Product-Month interactions (seasonal product patterns) - using price, not revenue
product_month_stats = df.groupby(['_ProductID', 'Month'])['Unit Price'].agg(['mean']).reset_index()
```
These capture how product pricing varies throughout the year.

#### 2. Location-Time Interactions
```python
# Location-Month interactions (regional seasonal patterns) - using price, not revenue
location_month_stats = df.groupby(['Location', 'Month'])['Unit Price'].agg(['mean']).reset_index()
```
Different locations may have different seasonal pricing patterns.

#### 3. Weekend Effects
```python
# Weekend-Product interactions - using price, not revenue
weekend_product_stats = df.groupby(['_ProductID', 'Is_Weekend'])['Unit Price'].agg(['mean']).reset_index()
```
Captures how product pricing varies between weekdays and weekends.

## Price Elasticity Modeling

The ethical time-enhanced model implements a sophisticated price elasticity approach:

### 1. Dynamic Elasticity
- Different elasticity factors based on price ranges
- Strong elasticity (-1.8) for very high prices
- Moderate elasticity (-0.8) for above-average prices
- Milder elasticity (-0.6) for below-average prices

### 2. Price Ratio Based
```python
price_ratio = unit_price / avg_price
predicted_revenue = predicted_revenue * (price_ratio ** elasticity)
```

### 3. Zero Quantity Handling
- Ensures zero revenue for zero quantity predictions
- Maintains economic consistency

## Model Training

### Training Script
Use `train_time_enhanced_ethical_model.py` to train the model:

```bash
python train_time_enhanced_ethical_model.py
```

This script will:
- Load and preprocess the training data
- Create advanced temporal features
- Train the LightGBM model with optimized hyperparameters
- Save the model, encoders, and reference data

### Model Files Generated
- `revenue_model_time_enhanced_ethical.pkl` - The trained model
- `revenue_encoders_time_enhanced_ethical.pkl` - Feature encoders
- `reference_data_time_enhanced_ethical.pkl` - Reference statistics

## Model Usage

### Loading the Model
```python
from revenue_predictor_time_enhanced_ethical import load_model

model_data, encoders, reference_data = load_model()
```

### Making Predictions
```python
from revenue_predictor_time_enhanced_ethical import predict_revenue

# Example prediction
result = predict_revenue({
    "Unit Price": 150.0,
    "Unit Cost": 75.0,
    "_ProductID": "12",
    "Location": "North",
    "Month": 6,
    "Day": 15,
    "Weekday": "Friday",
    "Year": 2023
})

print(f"Predicted Revenue: ${result['predicted_revenue']:.2f}")
print(f"Estimated Quantity: {result['estimated_quantity']}")
print(f"Profit: ${result['profit']:.2f}")
```

### Price Simulation
```python
from revenue_predictor_time_enhanced_ethical import simulate_price_variations

# Simulate different price points
variations = simulate_price_variations(
    base_data={
        "Unit Price": 100.0,
        "Unit Cost": 50.0,
        "_ProductID": "12",
        "Location": "North",
        "Month": 6,
        "Day": 15,
        "Weekday": "Friday",
        "Year": 2023
    },
    min_price_factor=0.5,
    max_price_factor=2.0,
    steps=7
)
```

## Model Validation

### Performance Metrics
Run comprehensive model validation:

```bash
python test_ethical_time_enhanced_model.py
```

Expected validation results:
- R² score ≥ 0.99
- MAE < 50
- RMSE < 250
- Prediction latency < 100ms

### Feature Importance
The model automatically calculates and logs feature importance during training, helping you understand which factors most influence revenue predictions.

## Best Practices

### Data Quality
- Ensure consistent product and location naming
- Validate price and cost ranges
- Check for missing or invalid dates
- Monitor for data anomalies

### Model Monitoring
- Regular validation against new data
- Performance metric tracking
- Feature drift detection
- Periodic model retraining

### Ethical Considerations
- No target leakage in features
- Transparent prediction methodology
- Explainable feature importance
- Fair treatment across all segments

## Troubleshooting

### Common Issues

#### Model Loading Errors
```bash
# Check if model files exist
ls -la *.pkl

# Verify file integrity
python -c "from revenue_predictor_time_enhanced_ethical import load_model; load_model()"
```

#### Poor Predictions
- Check input data format and ranges
- Validate feature encoding
- Ensure temporal features are correctly calculated
- Review price elasticity parameters

#### Performance Issues
- Monitor memory usage during prediction
- Check for large batch sizes
- Optimize feature calculation
- Consider model caching strategies

For additional support, refer to the testing guide and API documentation. 