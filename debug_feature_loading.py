#!/usr/bin/env python3
"""
Debug script to track what happens during feature loading
"""

from revenue_predictor_time_enhanced_ethical import load_model

def debug_feature_loading():
    """Debug the feature loading process"""
    print("🔍 Debugging Feature Loading")
    print("=" * 40)
    
    # Load model data
    model_data, encoders, reference_data = load_model()
    
    print("✅ Model loaded successfully")
    print(f"Model data keys: {list(model_data.keys())}")
    
    # Check feature names step by step
    feature_names = None
    
    if 'features' in model_data:
        feature_names = model_data['features']
        print(f"✅ Found 'features' key: {len(feature_names)} features")
        print(f"First 5 features: {feature_names[:5]}")
    elif 'feature_names' in model_data:
        feature_names = model_data['feature_names']
        print(f"✅ Found 'feature_names' key: {len(feature_names)} features")
    else:
        print("❌ No feature names found!")
        
    # Check model attributes
    model = model_data['model']
    if hasattr(model, 'feature_name_'):
        print(f"Model has feature_name_: {len(model.feature_name_)}")
    if hasattr(model, 'feature_names_'):
        print(f"Model has feature_names_: {len(model.feature_names_)}")
        
    print(f"\\nFinal feature_names variable: {type(feature_names)}")
    if feature_names:
        print(f"Length: {len(feature_names)}")
    else:
        print("feature_names is None or empty!")
        
    return feature_names

if __name__ == "__main__":
    features = debug_feature_loading() 