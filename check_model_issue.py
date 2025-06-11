#!/usr/bin/env python3
"""
Script to diagnose why the ML model produces constant predictions
"""

import joblib
import pandas as pd
import numpy as np

def check_model_health():
    """Check what's wrong with the ML model"""
    print("🔍 Diagnosing ML Model Issue")
    print("=" * 50)
    
    try:
        # Load model
        model_data = joblib.load('revenue_model_time_enhanced_ethical.pkl')
        encoders = joblib.load('revenue_encoders_time_enhanced_ethical.pkl')
        
        model = model_data['model']
        print(f"✅ Model loaded: {type(model)}")
        
        # Check feature names
        feature_names = model_data.get('features', model_data.get('feature_names', []))
        print(f"✅ Feature count: {len(feature_names)}")
        
        # Check if it's a valid model
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            print(f"✅ Feature importances available: {len(importances)} features")
            
            # Show top 10 most important features
            if len(feature_names) == len(importances):
                feature_importance = list(zip(feature_names, importances))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                
                print("\\n📊 Top 10 Most Important Features:")
                for i, (feature, importance) in enumerate(feature_importance[:10]):
                    print(f"{i+1:2d}. {feature:<30} {importance:.4f}")
                    
                # Check if any features have zero importance
                zero_importance = [f for f, imp in feature_importance if imp == 0]
                print(f"\\n⚠️ Features with zero importance: {len(zero_importance)}")
                
                # Check time features specifically  
                time_features = [f for f in feature_names if any(time_word in f.lower() 
                                for time_word in ['month', 'day', 'week', 'season', 'holiday', 'weekend', 'quarter'])]
                time_importances = [(f, dict(feature_importance)[f]) for f in time_features]
                
                print(f"\\n🕐 Time Features Found: {len(time_features)}")
                if time_importances:
                    time_importances.sort(key=lambda x: x[1], reverse=True)
                    print("Top 5 Time Features:")
                    for i, (feature, importance) in enumerate(time_importances[:5]):
                        print(f"   {feature:<30} {importance:.4f}")
                        
                    max_time_importance = max([imp for _, imp in time_importances])
                    print(f"\\n⚠️ Max time feature importance: {max_time_importance:.4f}")
                    
                    if max_time_importance < 0.01:
                        print("❌ PROBLEM: Time features have very low importance!")
                        print("   The model is ignoring time-based variations.")
                else:
                    print("❌ PROBLEM: No time features found in the model!")
                    
            else:
                print("❌ Feature names and importances don't match")
        else:
            print("❌ Model doesn't have feature importances")
            
        # Check encoders
        print(f"\\n🔤 Encoders available: {list(encoders.keys())}")
        
        # Check location encoder specifically
        if 'Location' in encoders:
            location_classes = encoders['Location'].classes_
            print(f"📍 Location classes: {list(location_classes)}")
        else:
            print("❌ No Location encoder found")
            
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Model files not found: {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def test_model_predictions():
    """Test what the model is actually predicting for different inputs"""
    print("\\n🧪 Testing Model Predictions")
    print("=" * 30)
    
    try:
        from revenue_predictor_time_enhanced_ethical import predict_revenue
        
        # Test extreme variations
        test_cases = [
            {'Unit Price': 1000, 'Unit Cost': 500, 'Month': 1, 'Day': 1, 'Weekday': 'Monday'},
            {'Unit Price': 10000, 'Unit Cost': 2000, 'Month': 12, 'Day': 31, 'Weekday': 'Sunday'},
            {'Unit Price': 100, 'Unit Cost': 50, 'Month': 6, 'Day': 15, 'Weekday': 'Wednesday'},
        ]
        
        for i, case in enumerate(test_cases):
            test_data = {
                '_ProductID': '1',
                'Location': 'North',
                'Year': 2024,
                **case
            }
            
            prediction = predict_revenue(test_data)
            revenue = prediction.get('predicted_revenue', 0)
            
            print(f"{i+1}. Price=${case['Unit Price']}, Month={case['Month']}, Day={case['Weekday']}: ${revenue:,.2f}")
            
    except Exception as e:
        print(f"❌ Error testing predictions: {e}")

if __name__ == "__main__":
    if check_model_health():
        test_model_predictions() 