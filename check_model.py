#!/usr/bin/env python3
"""
Script to check the model characteristics.
"""

import joblib
import numpy as np
import pandas as pd
from pprint import pprint

def main():
    # Load the model
    print("Loading model data...")
    model_data = joblib.load('revenue_model_time_enhanced_ethical.pkl')
    
    # Print model information
    print("\nModel Information:")
    print(f"Model type: {type(model_data['model'])}")
    
    # Print feature names
    feature_names = model_data.get('feature_names')
    if feature_names:
        print(f"\nNumber of features: {len(feature_names)}")
        print(f"First 10 features: {feature_names[:10]}")
    else:
        print("\nFeature names not found in model_data")
        
    # Print target information
    target = model_data.get('target')
    if target:
        print(f"\nTarget: {target}")
    else:
        print("\nTarget information not found in model_data")
        
    # Print target type
    target_type = model_data.get('target_type')
    if target_type:
        print(f"Target type: {target_type}")
    else:
        print("Target type not found in model_data")
    
    # Check if model is trained on log-transformed target
    is_log_target = model_data.get('is_log_target', False)
    print(f"\nIs log-transformed target: {is_log_target}")
    
    # Load reference data if available
    encoders = joblib.load('revenue_encoders_time_enhanced_ethical.pkl')
    reference_data = joblib.load('reference_data_time_enhanced_ethical.pkl')
    
    print("\nEncoders information:")
    for key, encoder in encoders.items():
        if hasattr(encoder, 'classes_'):
            print(f"  {key}: {len(encoder.classes_)} classes")
            
    # Make a sample prediction
    from revenue_predictor_time_enhanced_ethical import predict_revenue
    
    print("\nMaking sample predictions...")
    for product_id in [1, 2, 10, 47]:
        for unit_price in [50.0, 100.0, 200.0]:
            test_data = {
                'Unit Price': unit_price,
                'Unit Cost': unit_price * 0.4,
                'Month': 6,
                'Day': 15,
                'Weekday': 'Friday',
                'Location': 'North',
                '_ProductID': str(product_id),
                'Year': 2023
            }
            
            result = predict_revenue(test_data)
            if 'error' not in result:
                print(f"\nProduct {product_id}, Price ${unit_price}:")
                print(f"  Predicted Revenue: ${result['predicted_revenue']:.2f}")
                print(f"  Estimated Quantity: {result['estimated_quantity']}")
                print(f"  Revenue/Price = {result['predicted_revenue']/unit_price:.2f}")
            else:
                print(f"\nError predicting for Product {product_id}, Price ${unit_price}: {result['error']}")

if __name__ == "__main__":
    main() 