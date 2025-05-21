# Revenue Prediction Model for Small Businesses

This project provides an ethical machine learning model for predicting revenue for small businesses. It uses advanced feature engineering techniques while eliminating target leakage.

## Features

- **Direct Revenue Prediction**: Model predicts revenue without requiring quantity as an input
- **Ethical Modeling**: Designed without target leakage features for regulatory compliance
- **Advanced Feature Engineering**: Sophisticated temporal features, interaction terms, and statistical aggregates
- **Price Optimization**: Simulate different price points to find optimal pricing strategies
- **REST API**: Ready-to-use Flask API with endpoints for prediction and simulation

## Model Performance

| Model | Dataset Used | Target Leakage | Performance (R²) | MAE | RMSE |
|-------|-------------|----------------|-----------------|-----|------|
| Enhanced Ethical | 100% | No | 0.5897 (CV) | 5,630.96 | 7,767.13 |

The relatively lower R² value compared to models with target leakage reflects the realistic constraints of ethical prediction, where we cannot use features derived from the target variable.

## Key Features by Importance

1. ProductID_Encoded (12.39%)
2. Product_Month_Unit Price_mean (5.77%) 
3. Unit Price (5.66%)
4. Unit Cost (5.51%)
5. Price_to_Cost_Ratio (5.23%)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/revenue-prediction.git
cd revenue-prediction
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests to verify the model:
```bash
python test_ethical_model.py
```

4. Start the API:
```bash
python combined_revenue_api.py
```

## Usage

### Making Predictions with Python

```python
from enhanced_ethical_predictor import predict_revenue

# Input data
input_data = {
    'Unit Price': 100,
    'Unit Cost': 50,
    'Month': 6,
    'Day': 15,
    'Weekday': 'Friday',
    'Location': 'North',
    '_ProductID': 12,
    'Year': 2023
}

# Make a prediction
result = predict_revenue(input_data)
print(result)
# Output: {
#   "predicted_revenue": 265.45,
#   "estimated_quantity": 3,
#   "total_cost": 150.0,
#   "profit": 115.45,
#   "profit_margin_pct": 43.49,
#   "unit_price": 100,
#   "unit_cost": 50
# }
```

### Simulating Different Price Points

```python
from enhanced_ethical_predictor import simulate_price_variations

# Using the same input data
simulation = simulate_price_variations(input_data)
print(simulation)
```

### Finding the Optimal Price

```python
from enhanced_ethical_predictor import optimize_price

# Find optimal price for profit maximization
optimization = optimize_price(input_data, metric="profit")
print(optimization)
```

### Using the API

The API includes the following endpoints:

#### Basic Endpoints
- `/health`: Check if the API is running
- `/model-info`: Get information about the model

#### Prediction Endpoints
- `/predict-revenue`: Prediction with the enhanced ethical model

#### Price Simulation Endpoints
- `/simulate-revenue`: Price simulation with the enhanced ethical model

#### Advanced Endpoints
- `/optimize-price`: Find optimal pricing for revenue or profit

#### Example API Request
```python
import requests
import json

data = {
    'Unit Price': 100,
    'Unit Cost': 50,
    'Month': 6,
    'Day': 15,
    'Weekday': 'Friday',
    'Location': 'North',
    '_ProductID': 12,
    'Year': 2023
}

response = requests.post('http://localhost:5000/predict-revenue', json=data)
result = response.json()
print(result)
```

## Documentation

For detailed information about the model, features, and implementation, see:
- [MODEL_DOCUMENTATION.md](MODEL_DOCUMENTATION.md): Comprehensive model documentation

## Project Structure

- `minimal_enhanced_ethical_model.py`: Script to train the enhanced ethical model
- `enhanced_ethical_predictor.py`: Prediction module for the enhanced ethical model
- `ethical_revenue_model.py`: Base ethical model training script (for reference)
- `combined_revenue_api.py`: API implementation
- `test_ethical_model.py`: Testing script for model verification
- `MODEL_DOCUMENTATION.md`: Detailed model documentation

## Requirements

- Python 3.7+
- pandas
- numpy
- scikit-learn
- lightgbm
- joblib
- matplotlib
- flask

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dataset source: [trainingdataset.csv]
- Special thanks to contributors and reviewers 