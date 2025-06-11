#!/usr/bin/env python3
"""
Debug script to check preprocessing of time features
"""

from revenue_predictor_time_enhanced_ethical import load_model, validate_and_convert_input, preprocess, add_enhanced_time_features

def debug_preprocessing():
    """Debug the preprocessing of time features"""
    print("🔍 Debugging Preprocessing of Time Features")
    print("=" * 50)
    
    # Load model components
    model_data, encoders, reference_data = load_model()
    feature_names = model_data.get('features', [])
    
    # Test different dates
    test_cases = [
        {'Month': 6, 'Day': 12, 'Weekday': 'Monday'},
        {'Month': 6, 'Day': 13, 'Weekday': 'Tuesday'},
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
    
    for i, case in enumerate(test_cases):
        test_data = {**base_data, **case}
        
        print(f"\\n--- Test Case {i+1}: {case['Weekday']} {case['Month']}/{case['Day']} ---")
        
        # Step 1: Enhanced time features
        enhanced_data = add_enhanced_time_features(test_data.copy())
        time_features_subset = {k: v for k, v in enhanced_data.items() 
                              if any(kw in k.lower() for kw in ['month', 'day', 'week', 'season', 'holiday', 'weekend'])}
        print(f"Time features: {time_features_subset}")
        
        # Step 2: Validation
        validated = validate_and_convert_input(test_data)
        
        # Step 3: Full preprocessing  
        processed = preprocess(validated, model_data, encoders, reference_data)
        
        # Check key time-related features that have high importance
        important_time_features = [
            'Price_Seasonal_Deviation', 'Product_Month_Unit Price_mean',
            'Product_Quarter_Unit Price_mean', 'Is_Holiday', 'Is_Weekend'
        ]
        
        print("Important time features in processed data:")
        for feature in important_time_features:
            if feature in processed.columns:
                value = processed[feature].iloc[0]
                print(f"  {feature}: {value}")
            else:
                print(f"  {feature}: MISSING")
                
        # Get the features used for prediction
        if feature_names:
            # Check if we're using the right features
            missing_features = set(feature_names) - set(processed.columns)
            if missing_features:
                print(f"\\n❌ Missing features: {len(missing_features)}")
                print(f"First 5 missing: {list(missing_features)[:5]}")
            else:
                print("\\n✅ All features present")
                
            X = processed[feature_names]
            print(f"X shape for prediction: {X.shape}")
            
            # Show some key feature values
            key_features = ['Unit Price', 'Month', 'Day', 'Is_Weekend', 'Is_Holiday']
            print("Key feature values:")
            for feature in key_features:
                if feature in X.columns:
                    print(f"  {feature}: {X[feature].iloc[0]}")
        else:
            print("\\n❌ No feature names available")

if __name__ == "__main__":
    debug_preprocessing() 