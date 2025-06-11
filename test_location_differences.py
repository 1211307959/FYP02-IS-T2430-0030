#!/usr/bin/env python3
"""
Test Location-Specific Predictions
Check if different locations produce genuinely different predictions
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from revenue_predictor_time_enhanced_ethical import predict_revenue_for_forecasting

def test_location_specific_predictions():
    """Test predictions for each individual location"""
    print("🌍 TESTING LOCATION-SPECIFIC PREDICTIONS")
    print("=" * 60)
    
    # Base test data
    base_data = {
        'Unit Price': 5000.0,
        'Unit Cost': 2000.0,
        '_ProductID': 1,
        'Year': 2023,
        'Month': 6,
        'Day': 15,
        'Weekday': 'Thursday'
    }
    
    # Test each location individually
    locations = ['North', 'Central', 'South', 'East', 'West']
    location_results = {}
    
    print("Individual location predictions:")
    total_sum = 0
    
    for location in locations:
        test_data = base_data.copy()
        test_data['Location'] = location
        
        try:
            result = predict_revenue_for_forecasting(test_data)
            
            if 'error' not in result:
                revenue = result.get('predicted_revenue', 0)
                location_results[location] = revenue
                total_sum += revenue
                print(f"  {location:8}: ${revenue:,.2f}")
            else:
                print(f"  {location:8}: ERROR - {result['error']}")
                location_results[location] = 0
                
        except Exception as e:
            print(f"  {location:8}: EXCEPTION - {str(e)}")
            location_results[location] = 0
    
    print(f"\nTotal sum of individual locations: ${total_sum:,.2f}")
    
    # Test "All" location aggregation
    print(f"\n'All' location aggregation:")
    all_data = base_data.copy()
    all_data['Location'] = 'All'
    
    try:
        all_result = predict_revenue_for_forecasting(all_data)
        
        if 'error' not in all_result:
            all_revenue = all_result.get('predicted_revenue', 0)
            locations_count = all_result.get('location_count', 0)
            print(f"  All locations: ${all_revenue:,.2f}")
            print(f"  Locations included: {locations_count}")
            
            # Compare
            difference = abs(all_revenue - total_sum)
            print(f"\nComparison:")
            print(f"  Individual sum: ${total_sum:,.2f}")
            print(f"  'All' aggregate: ${all_revenue:,.2f}")
            print(f"  Difference: ${difference:,.2f}")
            
            if difference < 1:  # Within $1
                print("✅ SUCCESS: 'All' location matches sum of individuals")
            else:
                print("⚠️ WARNING: 'All' location doesn't match individual sum")
                
            # Check if locations are actually different
            revenues = list(location_results.values())
            unique_revenues = len(set(revenues))
            print(f"\nLocation variation analysis:")
            print(f"  Unique revenue values: {unique_revenues} out of {len(revenues)}")
            
            if unique_revenues == 1:
                print("⚠️ WARNING: All locations have identical predictions")
                print("   This suggests location features may not be working properly")
            elif unique_revenues == len(revenues):
                print("✅ EXCELLENT: All locations have different predictions")
            else:
                print("✅ GOOD: Some location variation detected")
                
        else:
            print(f"  ERROR: {all_result['error']}")
            
    except Exception as e:
        print(f"  EXCEPTION: {str(e)}")

def test_what_affects_location_predictions():
    """Test what makes location predictions different"""
    print("\n🔍 TESTING LOCATION FEATURE IMPACT")
    print("=" * 60)
    
    # Test if location encoding is working by checking location statistics
    try:
        from revenue_predictor_time_enhanced_ethical import load_model
        
        model_data, encoders, reference_data = load_model()
        
        print("Available encoders:")
        for key in encoders.keys():
            print(f"  {key}: {type(encoders[key])}")
            
        # Check location encoder
        if 'Location' in encoders:
            location_encoder = encoders['Location']
            if hasattr(location_encoder, 'classes_'):
                print(f"\nLocation encoder classes: {list(location_encoder.classes_)}")
            else:
                print(f"\nLocation encoder type: {type(location_encoder)}")
        
        # Check reference data for location-specific statistics
        print(f"\nReference data keys: {list(reference_data.keys())}")
        
        # Look for location-specific features
        location_features = [key for key in reference_data.keys() if 'location' in key.lower()]
        if location_features:
            print(f"Location-specific features found: {location_features}")
            for feature in location_features:
                print(f"  {feature}: {len(reference_data[feature])} entries")
        else:
            print("⚠️ No location-specific features found in reference data")
            
    except Exception as e:
        print(f"❌ Error checking location features: {str(e)}")

if __name__ == "__main__":
    test_location_specific_predictions()
    test_what_affects_location_predictions() 