import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
from pprint import pprint

print("=== MODEL ANALYSIS ===")

# Load model
try:
    model_data = joblib.load('revenue_model_50_50_split.pkl')
    encoders = joblib.load('revenue_encoders_50_50_split.pkl')
    
    # Analyze model structure
    print(f"Model type: {type(model_data)}")
    if isinstance(model_data, dict):
        print(f"Model keys: {model_data.keys()}")
        
        # Get the actual model
        model = model_data.get('model')
        if model:
            print(f"Model algorithm: {type(model)}")
            
        # Get features
        features = model_data.get('features')
        if features:
            print(f"Number of features: {len(features)}")
            print(f"Features: {features}")
            
            # Analyze time-based features
            time_features = [f for f in features if any(time_kw in f.lower() for time_kw in ['month', 'day', 'year', 'week', 'time', 'date', 'season'])]
            print(f"\nTime-based features: {time_features}")
            
        # Get performance metrics
        r2 = model_data.get('r2')
        mae = model_data.get('mae')
        rmse = model_data.get('rmse')
        if r2 is not None:
            print(f"\nModel Performance:")
            print(f"R² Score: {r2:.4f}")
            print(f"MAE: {mae:.4f}")
            print(f"RMSE: {rmse:.4f}")
            
        # Get hyperparameters
        params = model_data.get('params')
        if params:
            print(f"\nModel Hyperparameters:")
            pprint(params)
    
    # Analyze encoders
    print("\n=== ENCODERS ===")
    print(f"Encoder types: {list(encoders.keys())}")
    
except Exception as e:
    print(f"Error loading model: {str(e)}")

print("\n\n=== DATASET ANALYSIS ===")

# Load dataset
try:
    df = pd.read_csv('trainingdataset.csv')
    
    # Basic dataset info
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nData types:\n{df.dtypes}")
    
    # Display sample data
    print(f"\nSample data (3 rows):")
    print(df.head(3))
    
    # Analyze time-based columns
    time_cols = [col for col in df.columns if any(time_kw in col.lower() for time_kw in ['month', 'day', 'year', 'week', 'time', 'date', 'season'])]
    
    if time_cols:
        print(f"\nTime-based columns: {time_cols}")
        
        # Check distribution of months
        if 'Month' in df.columns:
            month_counts = df['Month'].value_counts().sort_index()
            print(f"\nMonth distribution:")
            for month, count in month_counts.items():
                print(f"  Month {month}: {count} records ({count/len(df)*100:.1f}%)")
        
        # Check distribution of weekdays
        if 'Weekday' in df.columns:
            weekday_counts = df['Weekday'].value_counts().sort_index()
            print(f"\nWeekday distribution:")
            for weekday, count in weekday_counts.items():
                print(f"  Weekday {weekday}: {count} records ({count/len(df)*100:.1f}%)")
    
    # Check if we have temporal patterns in revenue
    if 'Total Revenue' in df.columns and 'Month' in df.columns:
        monthly_avg = df.groupby('Month')['Total Revenue'].mean()
        print(f"\nAverage revenue by month:")
        for month, avg in monthly_avg.items():
            print(f"  Month {month}: ${avg:.2f}")
            
    if 'Total Revenue' in df.columns and 'Weekday' in df.columns:
        weekday_avg = df.groupby('Weekday')['Total Revenue'].mean()
        print(f"\nAverage revenue by weekday:")
        for weekday, avg in weekday_avg.items():
            print(f"  Weekday {weekday}: ${avg:.2f}")
    
except Exception as e:
    print(f"Error analyzing dataset: {str(e)}")

print("\n\n=== MODEL SAVING ANALYSIS ===")
print("When you retrain a model, the changes will only be saved if you explicitly save the model using joblib.dump().")
print("Here's how the process works:")
print("1. Train the model with new features/data")
print("2. Save it with: joblib.dump(model_data, 'revenue_model_50_50_split.pkl')")
print("3. Save encoders with: joblib.dump(encoders, 'revenue_encoders_50_50_split.pkl')")
print("\nIf you modify the code but don't save the model, the .pkl files won't be updated.")
print("You need to run the training script to save the new model to the .pkl files.") 