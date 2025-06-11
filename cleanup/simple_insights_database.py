import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class InsightSeverity(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class InsightCategory(Enum):
    FINANCIAL = "financial"
    PRODUCT = "product"
    LOCATION = "location"
    PRICING = "pricing"

@dataclass
class SimpleInsight:
    """A simple, actionable business insight"""
    id: str
    title: str
    category: str
    severity: str
    description: str
    recommendation: str
    impact: str
    priority_score: float

class SimpleInsightsDatabase:
    """Simplified insights database with only truly useful insights"""
    
    def __init__(self):
        pass
    
    def generate_insights(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate 3-5 truly useful insights"""
        insights = []
        
        # Calculate basic stats
        stats = self._calculate_stats(df)
        
        # Revenue Opportunity Insight
        if stats['avg_revenue'] < 15000:
            insights.append({
                'id': 'REV001',
                'title': 'Revenue Growth Opportunity',
                'category': 'financial',
                'severity': 'high' if stats['avg_revenue'] < 8000 else 'medium',
                'description': f"Your average transaction value is ${stats['avg_revenue']:,.0f}. With {stats['total_transactions']:,} transactions generating ${stats['total_revenue']:,.0f}, there's clear opportunity to increase per-transaction value.",
                'recommendation': f"Test 10-15% price increases on your top 5 products using the Scenario Planner. Focus on products that customers buy regularly and have good margins.",
                'impact': f"A 15% price increase could generate an additional ${stats['total_revenue'] * 0.15:,.0f} annually",
                'priority_score': 100 + (15000 - stats['avg_revenue']) / 100
            })
        
        # Product Performance Gap
        if stats['product_performance_gap'] > 50:
            insights.append({
                'id': 'PROD001',
                'title': 'Product Performance Imbalance',
                'category': 'product',
                'severity': 'high' if stats['product_performance_gap'] > 80 else 'medium',
                'description': f"Product {stats['top_product']} generates ${stats['top_product_revenue']:,.0f} while Product {stats['worst_product']} only generates ${stats['worst_product_revenue']:,.0f}. This {stats['product_performance_gap']:.0f}% gap needs attention.",
                'recommendation': f"Investigate why Product {stats['worst_product']} underperforms. Consider discontinuing it or improving its marketing. Put more resources behind Product {stats['top_product']}.",
                'impact': f"Optimizing product mix could improve revenue by ${stats['total_revenue'] * 0.1:,.0f}",
                'priority_score': 80 + stats['product_performance_gap']
            })
        
        # Location Performance Gap  
        if stats['location_performance_gap'] > 15:
            insights.append({
                'id': 'LOC001',
                'title': 'Location Performance Gap',
                'category': 'location',
                'severity': 'high' if stats['location_performance_gap'] > 40 else 'medium',
                'description': f"{stats['top_location']} generates ${stats['top_location_revenue']:,.0f} while {stats['worst_location']} generates ${stats['worst_location_revenue']:,.0f}. This {stats['location_performance_gap']:.1f}% gap indicates operational differences.",
                'recommendation': f"Visit {stats['worst_location']} to understand what {stats['top_location']} does better. Look at staffing, customer service, inventory management, and local marketing.",
                'impact': f"Bringing {stats['worst_location']} up to average could add ${(stats['avg_location_revenue'] - stats['worst_location_revenue']):,.0f}",
                'priority_score': 70 + stats['location_performance_gap']
            })
        
        # Pricing Consistency
        if stats['price_cv'] > 0.15:
            insights.append({
                'id': 'PRICE001', 
                'title': 'Pricing Inconsistency',
                'category': 'pricing',
                'severity': 'medium' if stats['price_cv'] > 0.25 else 'low',
                'description': f"Your pricing shows {stats['price_cv']:.1%} variation across products. Inconsistent pricing can confuse customers and reduce profitability.",
                'recommendation': "Create clear pricing tiers or categories. Review why similar products have different prices. Use the Scenario Planner to test standardized pricing.",
                'impact': f"Better pricing consistency could improve revenue predictability and margins",
                'priority_score': 60 + (stats['price_cv'] * 100)
            })
        
        # Profit Excellence (positive insight)
        if stats['avg_margin'] > 0.4:
            insights.append({
                'id': 'MARGIN001',
                'title': 'Excellent Profit Margins',
                'category': 'financial', 
                'severity': 'low',  # This is good news
                'description': f"Your business shows exceptional {stats['avg_margin']:.1%} profit margins, well above typical industry averages. This represents a strong competitive advantage.",
                'recommendation': "Consider strategic investments in growth, new products, or market expansion. Your strong margins give you flexibility to invest in opportunities.",
                'impact': f"Strong margins provide ${stats['total_revenue'] * (stats['avg_margin'] - 0.2):,.0f} in strategic investment capacity",
                'priority_score': 50  # Lower priority since it's good news
            })
        
        # Sort by priority and return top insights
        insights.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Add ranking
        for i, insight in enumerate(insights[:5], 1):
            insight['rank'] = i
            insight['is_top_insight'] = i <= 3
            
        return insights[:5]  # Return max 5 insights
    
    def _calculate_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic statistics for insights"""
        # Add derived columns
        df = df.copy()
        df['Quantity'] = df['Total Revenue'] / df['Unit Price']
        df['Total Cost'] = df['Quantity'] * df['Unit Cost']
        df['Profit'] = df['Total Revenue'] - df['Total Cost']
        df['Profit_Margin'] = df['Profit'] / df['Total Revenue']
        
        # Basic stats
        stats = {
            'total_revenue': df['Total Revenue'].sum(),
            'total_transactions': len(df),
            'avg_revenue': df['Total Revenue'].mean(),
            'avg_margin': df['Profit_Margin'].mean(),
            'price_cv': df['Unit Price'].std() / df['Unit Price'].mean()
        }
        
        # Product analysis
        product_revenue = df.groupby('_ProductID')['Total Revenue'].sum().sort_values(ascending=False)
        stats['top_product'] = int(product_revenue.index[0])
        stats['top_product_revenue'] = float(product_revenue.iloc[0])
        stats['worst_product'] = int(product_revenue.index[-1])
        stats['worst_product_revenue'] = float(product_revenue.iloc[-1])
        stats['product_performance_gap'] = ((product_revenue.iloc[0] - product_revenue.iloc[-1]) / product_revenue.iloc[0]) * 100
        
        # Location analysis
        location_revenue = df.groupby('Location')['Total Revenue'].sum().sort_values(ascending=False)
        stats['top_location'] = location_revenue.index[0]
        stats['top_location_revenue'] = float(location_revenue.iloc[0])
        stats['worst_location'] = location_revenue.index[-1]
        stats['worst_location_revenue'] = float(location_revenue.iloc[-1])
        stats['avg_location_revenue'] = float(location_revenue.mean())
        
        if len(location_revenue) > 1:
            stats['location_performance_gap'] = ((location_revenue.iloc[0] - location_revenue.iloc[-1]) / location_revenue.iloc[0]) * 100
        else:
            stats['location_performance_gap'] = 0
            
        return stats 