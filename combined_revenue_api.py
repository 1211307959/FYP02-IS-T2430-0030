from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import os
import traceback

# Import the enhanced ethical model predictor functions
from enhanced_ethical_predictor import predict_revenue, simulate_price_variations, optimize_price

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({"status": "healthy", "message": "Enhanced ethical revenue prediction API is running"}), 200

@app.route('/predict-revenue', methods=['POST'])
def predict_revenue_endpoint():
    """Endpoint for the enhanced ethical revenue prediction model."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        # Make prediction using the enhanced ethical model
        result = predict_revenue(data)
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Error in predict-revenue: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/simulate-revenue', methods=['POST'])
def simulate_revenue_endpoint():
    """Endpoint for price simulation with the enhanced ethical model."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        # Get optional parameters
        min_factor = data.pop('min_price_factor', 0.5)
        max_factor = data.pop('max_price_factor', 2.0)
        steps = data.pop('steps', 7)
        
        # Simulate price variations using the enhanced ethical model
        result = simulate_price_variations(data, min_factor, max_factor, steps)
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Error in simulate-revenue: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/optimize-price', methods=['POST'])
def optimize_price_endpoint():
    """Endpoint to find optimal pricing using the enhanced ethical model."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        # Get optional parameters
        min_factor = data.pop('min_price_factor', 0.5)
        max_factor = data.pop('max_price_factor', 2.0)
        steps = data.pop('steps', 20)
        metric = data.pop('metric', 'profit')
        
        # Optimize price using the enhanced ethical model
        result = optimize_price(data, min_factor, max_factor, steps, metric)
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Error in optimize-price: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/model-info', methods=['GET'])
def model_info():
    """Endpoint to get information about the enhanced ethical model."""
    try:
        model = {
            "model": "Enhanced Ethical Revenue Prediction Model",
            "description": "LightGBM model with advanced feature engineering and no target leakage",
            "performance": {
                "R2": 0.5897,
                "MAE": 5630.96,
                "RMSE": 7767.13
            },
            "key_features": [
                "ProductID_Encoded (12.4%)",
                "Product_Month_Unit Price_mean (5.8%)",
                "Unit Price (5.7%)",
                "Unit Cost (5.5%)",
                "Price_to_Cost_Ratio (5.2%)"
            ],
            "endpoints": {
                "prediction": "/predict-revenue",
                "simulation": "/simulate-revenue",
                "optimization": "/optimize-price"
            }
        }
        
        return jsonify(model), 200
    
    except Exception as e:
        print(f"Error in model-info: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Default to port 5000 if PORT environment variable is not set
    port = int(os.environ.get('PORT', 5000))
    # Use 0.0.0.0 to make the server accessible externally
    app.run(host='0.0.0.0', port=port, debug=False) 