#!/usr/bin/env python3
import joblib

# Load and inspect model file
model_data = joblib.load('revenue_model_time_enhanced_ethical.pkl')

print("Keys in model_data:", list(model_data.keys()))
print("Features key exists:", 'features' in model_data)

if 'features' in model_data:
    features = model_data['features']
    print("Features length:", len(features))
    print("First 5 features:", features[:5])
    print("Last 5 features:", features[-5:])
else:
    print("No 'features' key found!")
    
print("Feature importances shape:", len(model_data['model'].feature_importances_)) 