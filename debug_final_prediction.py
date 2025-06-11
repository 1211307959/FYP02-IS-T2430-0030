#!/usr/bin/env python3
"""
Debug script to identify which features are causing constant predictions
"""

from revenue_predictor_time_enhanced_ethical import load_model, validate_and_convert_input, preprocess, add_enhanced_time_features
import pandas as pd

def debug_final_prediction():
    """Debug what's causing identical predictions"""
    print("🔍 Debugging Final ML Predictions")
    print("=" * 50)
    
    # Load model components
    model_data, encoders, reference_data = load_model()
    model = model_data['model']
    feature_names = model_data.get('features', [])
    
    # Test different dates with same base data
    test_cases = [
        {'Month': 6, 'Day': 12, 'Weekday': 'Monday'},
        {'Month': 7, 'Day': 12, 'Weekday': 'Friday'},
        {'Month': 12, 'Day': 25, 'Weekday': 'Sunday'}  # Christmas
    ]
    
    base_data = {
        '_ProductID': '1',
        'Location': 'North',
        'Unit Price': 5000,
        'Unit Cost': 2000,
        'Year': 2024
    }
    
    processed_data = []
    predictions = []
    
    for i, case in enumerate(test_cases):
        test_data = {**base_data, **case}
        
        print(f"\\n--- Case {i+1}: {case['Weekday']} {case['Month']}/{case['Day']} ---")
        
        # Full preprocessing  
        validated = validate_and_convert_input(test_data)
        processed = preprocess(validated, model_data, encoders, reference_data)
        X = processed[feature_names]
        
        # Make prediction
        prediction = model.predict(X)[0]
        predictions.append(prediction)
        processed_data.append(X)
        
        print(f"Raw ML prediction (log): {prediction:.6f}")
        
        # Check top importance features for differences
        important_features = [
            'Price_vs_Product_Avg', 'Unit Price', 'Price_Seasonal_Deviation', 
            'Price_Popularity', 'Price_to_Cost_Ratio', 'Product_Unit Price_min'
        ]
        
        print("Top feature values:")
        for feature in important_features:
            if feature in X.columns:
                value = X[feature].iloc[0]
                print(f"  {feature}: {value}")
    
    print(f"\\n📊 Final Analysis:")
    print(f"Raw predictions: {predictions}")
    print(f"Unique predictions: {len(set(predictions))}")
    
    if len(set(predictions)) == 1:
        print("❌ ALL PREDICTIONS IDENTICAL - checking feature differences...")
        
        # Compare feature vectors
        df1 = processed_data[0]
        df2 = processed_data[1] 
        df3 = processed_data[2]
        
        different_features = []
        same_features = []
        
        for feature in feature_names:
            val1 = df1[feature].iloc[0]
            val2 = df2[feature].iloc[0] 
            val3 = df3[feature].iloc[0]
            
            if val1 != val2 or val2 != val3 or val1 != val3:
                different_features.append((feature, val1, val2, val3))
            else:
                same_features.append((feature, val1))
        
        print(f"\\n🔄 Features that VARY: {len(different_features)}")
        for feature, v1, v2, v3 in different_features[:10]:  # Show top 10
            print(f"  {feature}: {v1:.4f} → {v2:.4f} → {v3:.4f}")
            
        print(f"\\n⚠️ Features that are IDENTICAL: {len(same_features)}")
        print(f"Sample identical features: {[f[0] for f in same_features[:5]]}")
        
        # Check if any critical features are constant
        critical_features = ['Price_vs_Product_Avg', 'Unit Price', 'Price_Seasonal_Deviation', 'Price_Popularity']
        print(f"\\n🚨 Critical Feature Status:")
        for feature in critical_features:
            if feature in [f[0] for f in same_features]:
                val = next(f[1] for f in same_features if f[0] == feature)
                print(f"  ❌ {feature}: CONSTANT at {val}")
            elif feature in [f[0] for f in different_features]:
                values = next(f[1:] for f in different_features if f[0] == feature)
                print(f"  ✅ {feature}: VARYING {values}")
    else:
        print("✅ Predictions vary correctly!")
        
if __name__ == "__main__":
    debug_final_prediction() 