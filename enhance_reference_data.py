#!/usr/bin/env python3
"""
Script to enhance reference data with month-specific statistics
WITHOUT changing the existing working model
"""

import pandas as pd
import joblib
import numpy as np

def enhance_reference_data():
    """Add month-specific statistics to reference data"""
    print("🔧 Enhancing Reference Data with Month-Specific Statistics")
    print("=" * 60)
    
    # Load existing reference data
    try:
        reference_data = joblib.load('reference_data_time_enhanced_ethical.pkl')
        print("✅ Loaded existing reference data")
        print(f"Current keys: {list(reference_data.keys())}")
    except FileNotFoundError:
        print("❌ Reference data not found, creating new one...")
        reference_data = {}
    
    # Load the training dataset to calculate month-specific stats
    try:
        print("\n📊 Loading training dataset...")
        df = pd.read_csv('public/data/trainingdataset.csv')
        print(f"✅ Loaded dataset: {df.shape} rows")
    except FileNotFoundError:
        print("❌ Training dataset not found, trying alternate location...")
        try:
            df = pd.read_csv('trainingdataset.csv')
            print(f"✅ Loaded dataset: {df.shape} rows")
        except FileNotFoundError:
            print("❌ Cannot find training dataset!")
            return
    
    # Create derived columns if they don't exist
    if 'Total Cost' not in df.columns:
        df['Quantity'] = df['Total Revenue'] / df['Unit Price']
        df['Total Cost'] = df['Quantity'] * df['Unit Cost']
        df['Profit'] = df['Total Revenue'] - df['Total Cost']
        df['Profit Margin (%)'] = (df['Profit'] / df['Total Revenue']) * 100
        print("✅ Created derived columns")
    
    # Extract time components if needed
    if 'Month' not in df.columns:
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df['Year'] = df['Date'].dt.year
            df['Month'] = df['Date'].dt.month
            df['Day'] = df['Date'].dt.day
            df['Weekday'] = df['Date'].dt.day_name()
            print("✅ Extracted time components from Date column")
        else:
            print("❌ No time information available")
            return
    
    print(f"\n🔍 Data columns: {list(df.columns)}")
    print(f"Sample data shape: {df.shape}")
    
    # Calculate month-specific product statistics
    print("\n📈 Calculating Product-Month Statistics...")
    product_month_stats = df.groupby(['_ProductID', 'Month'])['Unit Price'].agg(['mean', 'std', 'count']).reset_index()
    product_month_dict = {}
    
    for _, row in product_month_stats.iterrows():
        product_id = str(row['_ProductID'])
        month = int(row['Month'])
        key = f"{product_id}_{month}"
        product_month_dict[key] = {
            'mean': float(row[('Unit Price', 'mean')]),
            'std': float(row[('Unit Price', 'std')]) if not pd.isna(row[('Unit Price', 'std')]) else 0.0,
            'count': int(row[('Unit Price', 'count')])
        }
    
    reference_data['product_month_price_stats'] = product_month_dict
    print(f"✅ Added {len(product_month_dict)} product-month combinations")
    
    # Calculate quarter-specific product statistics
    print("\n📊 Calculating Product-Quarter Statistics...")
    df['Quarter'] = (df['Month'] - 1) // 3 + 1
    product_quarter_stats = df.groupby(['_ProductID', 'Quarter'])['Unit Price'].agg(['mean', 'std', 'count']).reset_index()
    product_quarter_dict = {}
    
    for _, row in product_quarter_stats.iterrows():
        product_id = str(row['_ProductID'])
        quarter = int(row['Quarter'])
        key = f"{product_id}_{quarter}"
        product_quarter_dict[key] = {
            'mean': float(row[('Unit Price', 'mean')]),
            'std': float(row[('Unit Price', 'std')]) if not pd.isna(row[('Unit Price', 'std')]) else 0.0,
            'count': int(row[('Unit Price', 'count')])
        }
    
    reference_data['product_quarter_price_stats'] = product_quarter_dict
    print(f"✅ Added {len(product_quarter_dict)} product-quarter combinations")
    
    # Calculate location-month statistics
    print("\n🌍 Calculating Location-Month Statistics...")
    location_month_stats = df.groupby(['Location', 'Month'])['Unit Price'].agg(['mean', 'std', 'count']).reset_index()
    location_month_dict = {}
    
    for _, row in location_month_stats.iterrows():
        location = str(row['Location'])
        month = int(row['Month'])
        key = f"{location}_{month}"
        location_month_dict[key] = {
            'mean': float(row[('Unit Price', 'mean')]),
            'std': float(row[('Unit Price', 'std')]) if not pd.isna(row[('Unit Price', 'std')]) else 0.0,
            'count': int(row[('Unit Price', 'count')])
        }
    
    reference_data['location_month_price_stats'] = location_month_dict
    print(f"✅ Added {len(location_month_dict)} location-month combinations")
    
    # Calculate weekend-specific statistics
    print("\n🎯 Calculating Weekend-Specific Statistics...")
    df['Is_Weekend'] = df['Weekday'].isin(['Saturday', 'Sunday']).astype(int)
    
    # Product-Weekend stats
    product_weekend_stats = df.groupby(['_ProductID', 'Is_Weekend'])['Unit Price'].agg(['mean']).reset_index()
    product_weekend_dict = {}
    
    for _, row in product_weekend_stats.iterrows():
        product_id = str(row['_ProductID'])
        is_weekend = int(row['Is_Weekend'])
        key = f"{product_id}_{is_weekend}"
        product_weekend_dict[key] = float(row[('Unit Price', 'mean')])
    
    reference_data['product_weekend_price_stats'] = product_weekend_dict
    print(f"✅ Added {len(product_weekend_dict)} product-weekend combinations")
    
    # Location-Weekend stats
    location_weekend_stats = df.groupby(['Location', 'Is_Weekend'])['Unit Price'].agg(['mean']).reset_index()
    location_weekend_dict = {}
    
    for _, row in location_weekend_stats.iterrows():
        location = str(row['Location'])
        is_weekend = int(row['Is_Weekend'])
        key = f"{location}_{is_weekend}"
        location_weekend_dict[key] = float(row[('Unit Price', 'mean')])
    
    reference_data['location_weekend_price_stats'] = location_weekend_dict
    print(f"✅ Added {len(location_weekend_dict)} location-weekend combinations")
    
    # Save enhanced reference data
    joblib.dump(reference_data, 'reference_data_time_enhanced_ethical.pkl')
    print(f"\n💾 Saved enhanced reference data")
    print(f"Final keys: {list(reference_data.keys())}")
    
    # Show sample statistics
    print("\n📋 Sample Statistics:")
    if 'product_month_price_stats' in reference_data:
        sample_keys = list(reference_data['product_month_price_stats'].keys())[:3]
        for key in sample_keys:
            stats = reference_data['product_month_price_stats'][key]
            print(f"  {key}: ${stats['mean']:.2f} avg, {stats['count']} transactions")
    
    print("\n✅ Reference data enhancement complete!")
    print("🎯 Now forecasting should show proper date variation!")

if __name__ == "__main__":
    enhance_reference_data() 