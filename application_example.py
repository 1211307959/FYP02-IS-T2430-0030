"""
Revenue Prediction Application Example

This script demonstrates how to use the 50/50 split revenue prediction model 
in a real-world business application. It shows how to:

1. Make predictions for a new product
2. Find optimal pricing for different business objectives
3. Create a simple pricing strategy based on model predictions

Usage:
    python application_example.py
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from revenue_predictor_50_50 import predict_revenue, simulate_price_variations, optimize_price

class RevenuePredictionApp:
    def __init__(self):
        """Initialize the application"""
        # Sample product data
        self.product = {
            'name': 'Premium Widget XL',
            'product_id': 12,
            'base_cost': 75,
            'current_price': 150,
            'location': 'North'
        }
        
        # Current date/time context
        self.context = {
            'month': 6,  # June
            'day': 15,
            'weekday': 'Wednesday',
            'year': 2023,
            'is_holiday_season': False
        }
    
    def prepare_model_input(self, price=None):
        """Prepare the input data for the model"""
        if price is None:
            price = self.product['current_price']
            
        # Format input for the model
        return {
            'Unit Price': price,
            'Unit Cost': self.product['base_cost'],
            'Month': self.context['month'],
            'Day': self.context['day'],
            'Weekday': self.context['weekday'],
            'Location': self.product['location'],
            '_ProductID': self.product['product_id'],
            'Year': self.context['year']
        }
    
    def predict_current_revenue(self):
        """Predict revenue with the current price"""
        print(f"\n===== CURRENT PRICE ANALYSIS: ${self.product['current_price']} =====")
        
        # Prepare input data
        input_data = self.prepare_model_input()
        
        # Make prediction
        result = predict_revenue(input_data)
        
        # Print results
        print(f"Product: {self.product['name']} (ID: {self.product['product_id']})")
        print(f"Location: {self.product['location']}")
        print(f"Date: {self.context['month']}/{self.context['day']}/{self.context['year']} ({self.context['weekday']})")
        print(f"\nCurrent Price: ${self.product['current_price']:.2f}")
        print(f"Unit Cost: ${self.product['base_cost']:.2f}")
        print(f"Predicted Revenue: ${result['predicted_revenue']:.2f}")
        print(f"Estimated Quantity: {result['estimated_quantity']}")
        print(f"Expected Profit: ${result['profit']:.2f}")
        print(f"Profit Margin: {result['profit_margin_pct']:.2f}%")
        
        return result
    
    def find_optimal_pricing(self):
        """Find the optimal pricing for revenue and profit"""
        print("\n===== PRICING OPTIMIZATION =====")
        
        # Prepare input data
        input_data = self.prepare_model_input()
        
        # Find optimal pricing for revenue
        revenue_opt = optimize_price(input_data, metric="revenue")
        
        # Find optimal pricing for profit
        profit_opt = optimize_price(input_data, metric="profit")
        
        # Print results
        print("\nREVENUE OPTIMIZATION:")
        print(f"Optimal Price: ${revenue_opt['unit_price']:.2f}")
        print(f"Expected Revenue: ${revenue_opt['revenue']:.2f}")
        print(f"Expected Quantity: {revenue_opt['quantity']}")
        print(f"Expected Profit: ${revenue_opt['profit']:.2f}")
        print(f"Profit Margin: {(revenue_opt['profit'] / revenue_opt['revenue'] * 100):.2f}%")
        
        print("\nPROFIT OPTIMIZATION:")
        print(f"Optimal Price: ${profit_opt['unit_price']:.2f}")
        print(f"Expected Profit: ${profit_opt['profit']:.2f}")
        print(f"Expected Revenue: ${profit_opt['revenue']:.2f}")
        print(f"Expected Quantity: {profit_opt['quantity']}")
        print(f"Profit Margin: {(profit_opt['profit'] / profit_opt['revenue'] * 100):.2f}%")
        
        return {
            'revenue_optimization': revenue_opt,
            'profit_optimization': profit_opt
        }
    
    def analyze_price_sensitivity(self):
        """Analyze price sensitivity and create a visualization"""
        print("\n===== PRICE SENSITIVITY ANALYSIS =====")
        
        # Prepare input data
        input_data = self.prepare_model_input()
        
        # Simulate different price points
        variations = simulate_price_variations(
            input_data, 
            min_price_factor=0.5, 
            max_price_factor=2.0, 
            steps=16
        )
        
        # Create pandas DataFrame for analysis
        df = pd.DataFrame(variations)
        
        # Calculate margins
        df['profit_margin_pct'] = (df['profit'] / df['revenue']) * 100
        
        # Print results
        print("\nPrice Sensitivity Table:")
        print(f"{'Price ($)':10} {'Quantity':10} {'Revenue ($)':15} {'Profit ($)':15} {'Margin (%)':10}")
        print("-" * 65)
        
        for _, row in df.iterrows():
            print(f"${row['unit_price']:9.2f} {row['quantity']:<10} ${row['revenue']:<14.2f} ${row['profit']:<14.2f} {row['profit_margin_pct']:9.2f}%")
        
        # Create visualization
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Revenue and Profit vs Price
            ax1.plot(df['unit_price'], df['revenue'], 'b-', marker='o', label='Revenue')
            ax1.plot(df['unit_price'], df['profit'], 'g-', marker='s', label='Profit')
            ax1.set_xlabel('Unit Price ($)')
            ax1.set_ylabel('Amount ($)')
            ax1.set_title('Revenue and Profit vs Price')
            ax1.legend()
            ax1.grid(True)
            
            # Quantity and Margin vs Price
            ax2.plot(df['unit_price'], df['quantity'], 'r-', marker='o', label='Quantity')
            ax2.set_xlabel('Unit Price ($)')
            ax2.set_ylabel('Quantity')
            ax2.set_title('Quantity vs Price')
            ax2.grid(True)
            
            # Add profit margin as a secondary y-axis
            ax3 = ax2.twinx()
            ax3.plot(df['unit_price'], df['profit_margin_pct'], 'm--', marker='s', label='Profit Margin')
            ax3.set_ylabel('Profit Margin (%)')
            
            # Combine legends
            lines1, labels1 = ax2.get_legend_handles_labels()
            lines2, labels2 = ax3.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
            
            plt.tight_layout()
            plt.savefig('application_price_analysis.png')
            print("\nPrice sensitivity graph saved to 'application_price_analysis.png'")
            
        except Exception as e:
            print(f"Could not create visualization: {e}")
        
        return df
    
    def create_pricing_strategy(self, optimization_results):
        """Create a pricing strategy based on model predictions"""
        print("\n===== PRICING STRATEGY RECOMMENDATIONS =====")
        
        current_price = self.product['current_price']
        revenue_optimal = optimization_results['revenue_optimization']['unit_price']
        profit_optimal = optimization_results['profit_optimization']['unit_price']
        
        # Analyze the current price compared to optimal
        revenue_difference = ((revenue_optimal - current_price) / current_price) * 100
        profit_difference = ((profit_optimal - current_price) / current_price) * 100
        
        print(f"Current Price: ${current_price:.2f}")
        print(f"Revenue-optimal Price: ${revenue_optimal:.2f} ({revenue_difference:+.2f}%)")
        print(f"Profit-optimal Price: ${profit_optimal:.2f} ({profit_difference:+.2f}%)")
        
        # Make strategic recommendations
        print("\nSTRATEGIC RECOMMENDATIONS:")
        
        if abs(revenue_difference) < 5 and abs(profit_difference) < 10:
            print("✓ Current price is near optimal for both revenue and profit.")
            print("   Recommendation: Maintain current pricing.")
            strategy = "maintain"
        
        elif revenue_difference > 10 and profit_difference > 10:
            print("! Current price is significantly below optimal levels.")
            print(f"   Recommendation: Increase price to ${(current_price * 1.05):.2f} (+5%) and monitor results.")
            print(f"   Target optimal price: ${profit_optimal:.2f} over time.")
            strategy = "increase"
            
        elif revenue_difference < -10 and profit_difference < -10:
            print("! Current price is significantly above optimal levels.")
            print(f"   Recommendation: Decrease price to ${(current_price * 0.95):.2f} (-5%) and monitor results.")
            print(f"   Target optimal price: ${revenue_optimal:.2f} over time.")
            strategy = "decrease"
            
        elif profit_difference > 10:
            print("! Current price is below profit-optimal but near revenue-optimal.")
            print(f"   Recommendation: Consider gradual increases toward ${profit_optimal:.2f} to maximize profit.")
            print("   Monitor quantity changes closely to ensure revenue isn't negatively impacted.")
            strategy = "increase_gradually"
            
        else:
            print("! Current price requires balancing multiple factors.")
            print("   Recommendation: Consider testing different price points to gather actual market data.")
            print(f"   Test a slightly higher price (${(current_price * 1.03):.2f}) for profit optimization.")
            strategy = "test"
        
        # Seasonal adjustments
        if self.context['is_holiday_season']:
            print("\nSEASONAL ADJUSTMENT:")
            print("   Holiday season detected - consider a 10% premium on recommended prices")
            print("   due to increased demand during this period.")
        
        return {
            'current_price': current_price,
            'revenue_optimal': revenue_optimal,
            'profit_optimal': profit_optimal,
            'revenue_difference_pct': revenue_difference,
            'profit_difference_pct': profit_difference,
            'recommendation': strategy
        }
    
    def run_application(self):
        """Run the complete business application"""
        print("=" * 80)
        print(f"REVENUE PREDICTION & PRICING STRATEGY FOR {self.product['name']}")
        print("=" * 80)
        
        try:
            # Step 1: Predict revenue with current price
            current_results = self.predict_current_revenue()
            
            # Step 2: Find optimal pricing
            optimization_results = self.find_optimal_pricing()
            
            # Step 3: Analyze price sensitivity
            sensitivity_results = self.analyze_price_sensitivity()
            
            # Step 4: Create pricing strategy
            strategy = self.create_pricing_strategy(optimization_results)
            
            print("\n" + "=" * 80)
            print("APPLICATION COMPLETED SUCCESSFULLY")
            print("=" * 80)
            
            return {
                'product': self.product,
                'context': self.context,
                'current_results': current_results,
                'optimization_results': optimization_results,
                'strategy': strategy
            }
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

# -------------------------------------------------------------------------
# Run the application if executed as a script
# -------------------------------------------------------------------------

if __name__ == "__main__":
    app = RevenuePredictionApp()
    results = app.run_application()
    
    # Save results to JSON for future reference
    try:
        with open('pricing_strategy_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print("\nResults saved to 'pricing_strategy_results.json'")
    except Exception as e:
        print(f"Could not save results: {e}") 