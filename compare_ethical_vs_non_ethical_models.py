# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import joblib
from tabulate import tabulate
import matplotlib.pyplot as plt

print("=== MODEL COMPARISON - ETHICAL VS NON-ETHICAL ===")

# Load models
time_enhanced_model = joblib.load('revenue_model_time_enhanced.pkl')
time_enhanced_ethical_model = joblib.load('revenue_model_time_enhanced_ethical.pkl')

# Print performance metrics
print("\nPerformance Metrics:")
print(f"Non-Ethical Model R²: {time_enhanced_model.get('r2', 'N/A'):.4f}")
print(f"Non-Ethical Model MAE: {time_enhanced_model.get('mae', 'N/A'):.4f}")
print(f"Non-Ethical Model RMSE: {time_enhanced_model.get('rmse', 'N/A'):.4f}")

print(f"Ethical Model R²: {time_enhanced_ethical_model.get('r2', 'N/A'):.4f}")
print(f"Ethical Model MAE: {time_enhanced_ethical_model.get('mae', 'N/A'):.4f}")
print(f"Ethical Model RMSE: {time_enhanced_ethical_model.get('rmse', 'N/A'):.4f}")

# Compare features
non_ethical_features = time_enhanced_model.get('features', [])
ethical_features = time_enhanced_ethical_model.get('features', [])

print(f"\nNon-Ethical Model Features: {len(non_ethical_features)}")
print(f"Ethical Model Features: {len(ethical_features)}")

# Find leaking features (in non-ethical but not in ethical)
leaking_features = set(non_ethical_features) - set(ethical_features)
print(f"\nPotential Leaking Features: {len(leaking_features)}")
if leaking_features:
    print("Top leaking features:")
    for feature in sorted(list(leaking_features))[:10]:
        print(f"- {feature}")

# Create feature importance comparison
print("\nTop 10 Features by Importance:")
print("\nNon-Ethical Model:")
non_ethical_importance = pd.DataFrame({
    'Feature': non_ethical_features,
    'Importance': time_enhanced_model['model'].feature_importances_
}).sort_values('Importance', ascending=False)

for i, row in non_ethical_importance.head(10).iterrows():
    print(f"{row['Feature']}: {row['Importance'] * 100:.2f}%")

print("\nEthical Model:")
ethical_importance = pd.DataFrame({
    'Feature': ethical_features,
    'Importance': time_enhanced_ethical_model['model'].feature_importances_
}).sort_values('Importance', ascending=False)

for i, row in ethical_importance.head(10).iterrows():
    print(f"{row['Feature']}: {row['Importance'] * 100:.2f}%")

# Create comparison plot
plt.figure(figsize=(12, 10))
plt.subplot(2, 1, 1)
non_ethical_importance.head(10).sort_values('Importance').plot(
    kind='barh', x='Feature', y='Importance', legend=False
)
plt.title('Top 10 Features (Non-Ethical Model)')

plt.subplot(2, 1, 2)
ethical_importance.head(10).sort_values('Importance').plot(
    kind='barh', x='Feature', y='Importance', legend=False
)
plt.title('Top 10 Features (Ethical Model)')

plt.tight_layout()
plt.savefig('model_comparison_ethical_vs_non_ethical.png')
print("Comparison plot saved as: model_comparison_ethical_vs_non_ethical.png")

print("\nComparison complete!")
