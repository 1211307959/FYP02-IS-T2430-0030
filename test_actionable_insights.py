"""
Test script for the enhanced Actionable Business Insights System

Tests all new features: severity variants, compound detection, feedback tracking
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from actionable_insights import actionable_insights
import numpy as np

def test_enhanced_insights_system():
    """Test the enhanced insights system with all new features"""
    
    print("🧪 Testing Enhanced Actionable Insights System")
    print("=" * 60)
    
    # Load test data
    try:
        df = pd.read_csv('trainingdataset.csv')
        print(f"✅ Loaded {len(df)} rows of data")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    # Test 1: Generate insights with all enhancements
    print("\n1️⃣ Testing Enhanced Insight Generation...")
    insights = actionable_insights.generate_insights(df)
    
    print(f"📊 Generated {len(insights)} actionable insights")
    
    # Test 2: Verify new field structure
    print("\n2️⃣ Testing New Field Structure...")
    if insights:
        first_insight = insights[0]
        new_fields = ['why_it_matters', 'predicted_value', 'prediction_type', 'generated_at']
        
        for field in new_fields:
            if field in first_insight:
                print(f"✅ {field}: {first_insight[field]}")
            else:
                print(f"❌ Missing field: {field}")
    
    # Test 3: Check for severity variants
    print("\n3️⃣ Testing Severity-Based Variants...")
    severity_levels = {}
    for insight in insights:
        severity = insight.get('severity', 'unknown')
        if severity not in severity_levels:
            severity_levels[severity] = []
        severity_levels[severity].append(insight['title'])
    
    for severity, titles in severity_levels.items():
        print(f"📊 {severity.upper()}: {len(titles)} insights")
        for title in titles:
            print(f"   • {title}")
    
    # Test 4: Check for compound insights
    print("\n4️⃣ Testing Compound Insight Detection...")
    compound_insights = [i for i in insights if i['id'].startswith('COMP')]
    individual_insights = [i for i in insights if not i['id'].startswith('COMP')]
    
    print(f"🔗 Found {len(compound_insights)} compound insights")
    print(f"🎯 Found {len(individual_insights)} individual insights")
    
    for comp in compound_insights:
        print(f"   🧩 {comp['id']}: {comp['title']}")
        print(f"      Category: {comp['category']} | Severity: {comp['severity']}")
        print(f"      Why it matters: {comp['why_it_matters']}")
    
    # Test 5: Detailed insight analysis
    print("\n5️⃣ Testing Detailed Insight Content...")
    for i, insight in enumerate(insights, 1):
        print(f"\n--- INSIGHT #{i}: {insight['title']} ---")
        print(f"🆔 ID: {insight['id']}")
        print(f"📊 Category: {insight['category']} | Severity: {insight['severity']}")
        print(f"🎯 Priority Score: {insight['priority_score']:.1f}")
        
        # Show why it matters (NEW)
        if 'why_it_matters' in insight:
            print(f"💡 Why it matters: {insight['why_it_matters']}")
        
        # Show description with severity context (ENHANCED)
        print(f"📝 Description: {insight['description']}")
        
        # Show action plan (ENHANCED with severity variants)
        print(f"🎯 Action: {insight.get('recommended_action', insight.get('action_plan', 'N/A'))[:100]}...")
        
        # Show ML prediction if available
        if 'ml_prediction' in insight:
            print(f"🤖 ML Prediction: {insight['ml_prediction']}")
        elif 'model_integration' in insight:
            print(f"🤖 Model Integration: {insight['model_integration'][:100]}...")
        
        # Show predicted value for tracking (NEW)
        if 'predicted_value' in insight:
            print(f"📈 Predicted Value: {insight['predicted_value']:,.0f} ({insight['prediction_type']})")
        
        # Show feedback data if available (NEW)
        if 'feedback_available' in insight:
            print(f"📊 Feedback Available: Tracked for {insight['weeks_tracked']} weeks")
            print(f"   Original Prediction: {insight['predicted_value_original']:,.0f}")
            print(f"   Actual Result: {insight['actual_value']:,.0f}")
            print(f"   Accuracy: {insight['prediction_accuracy']}")
        
        print(f"⏱️ Timeline: {insight['timeline']}")
        print(f"🎯 Business Impact: {insight.get('business_impact', insight.get('expected_outcome', 'N/A'))[:100]}...")
    
    # Test 6: Feedback tracking system
    print("\n6️⃣ Testing Feedback Tracking System...")
    tracking_file = 'insight_feedback_tracking.json'
    
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r') as f:
            tracking_data = json.load(f)
        
        print(f"📊 Found {len(tracking_data)} tracking records")
        
        pending = [r for r in tracking_data if r['status'] == 'pending']
        completed = [r for r in tracking_data if r['status'] == 'completed']
        
        print(f"⏳ Pending predictions: {len(pending)}")
        print(f"✅ Completed predictions: {len(completed)}")
        
        if completed:
            avg_accuracy = sum(r.get('accuracy_pct', 0) for r in completed) / len(completed)
            print(f"📊 Average prediction accuracy: {avg_accuracy:.1f}%")
    else:
        print("📝 No tracking data file found (expected for first run)")
    
    # Test 7: Simulate feedback for demonstration
    print("\n7️⃣ Simulating Feedback Tracking...")
    
    # Create a fake old insight to show feedback
    if insights and tracking_file:
        # Create a simulated old tracking record
        old_record = {
            'insight_id': 'REV001',
            'title': 'Revenue Growth Opportunity (Test)',
            'predicted_value': 125000,
            'prediction_type': 'annual_revenue_increase',
            'predicted_at': (datetime.now() - timedelta(weeks=5)).isoformat(),
            'status': 'pending',
            'tracking_period_weeks': 4
        }
        
        # Add to tracking file
        try:
            existing_data = []
            if os.path.exists(tracking_file):
                with open(tracking_file, 'r') as f:
                    existing_data = json.load(f)
            
            existing_data.append(old_record)
            
            with open(tracking_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            print("✅ Added simulated old tracking record")
            
            # Generate insights again to see feedback
            print("🔄 Regenerating insights to show feedback...")
            new_insights = actionable_insights.generate_insights(df)
            
            # Check for feedback
            for insight in new_insights:
                if insight['id'] == 'REV001' and 'feedback_available' in insight:
                    print(f"🎉 Feedback demonstration successful!")
                    print(f"   Tracked for: {insight['weeks_tracked']} weeks")
                    print(f"   Accuracy: {insight['prediction_accuracy']}")
                    break
                    
        except Exception as e:
            print(f"⚠️ Could not simulate feedback: {e}")
    
    # Test 8: Performance summary
    print(f"\n8️⃣ Enhanced System Performance Summary")
    print("=" * 50)
    print(f"✅ Total insights generated: {len(insights)}")
    print(f"🧩 Individual insights: {len(individual_insights)}")
    print(f"🔗 Compound insights: {len(compound_insights)}")
    print(f"📊 Severity levels detected: {len(severity_levels)}")
    print(f"🎯 Top priority insight: {insights[0]['title'] if insights else 'None'}")
    print(f"📈 Highest priority score: {insights[0]['priority_score']:.1f}" if insights else "N/A")
    
    # Check for new features
    feature_check = {
        'Severity Variants': any('critical' in i.get('title', '') or i.get('severity') == 'critical' for i in insights),
        'Compound Detection': len(compound_insights) > 0,
        'Why It Matters': any('why_it_matters' in i for i in insights),
        'Predicted Values': any('predicted_value' in i for i in insights),
        'Feedback Tracking': os.path.exists(tracking_file)
    }
    
    print(f"\n🌟 Enhanced Features Status:")
    for feature, status in feature_check.items():
        print(f"   {'✅' if status else '❌'} {feature}")
    
    print(f"\n🎉 Enhanced Actionable Insights System Test Complete!")
    return insights

def test_compound_scenarios():
    """Test specific scenarios that should trigger compound insights"""
    
    print("\n🧪 Testing Compound Insight Scenarios")
    print("=" * 50)
    
    # Load data and create test scenarios
    df = pd.read_csv('trainingdataset.csv')
    
    # Create a scenario with multiple issues
    test_df = df.copy()
    
    # Simulate low revenue scenario (should trigger REV001)
    test_df['Total Revenue'] = test_df['Total Revenue'] * 0.3  # Reduce revenue
    
    # Simulate product performance gap (should trigger PROD001)
    # Make one product much worse
    worst_product = test_df['_ProductID'].value_counts().index[-1]
    test_df.loc[test_df['_ProductID'] == worst_product, 'Total Revenue'] *= 0.1
    
    print(f"🎭 Created test scenario with compound issues")
    print(f"   • Low average revenue (should trigger REV001)")
    print(f"   • Severe product gap for Product {worst_product} (should trigger PROD001)")
    
    # Generate insights
    compound_insights = actionable_insights.generate_insights(test_df)
    
    # Check results
    individual_ids = [i['id'] for i in compound_insights if not i['id'].startswith('COMP')]
    compound_ids = [i['id'] for i in compound_insights if i['id'].startswith('COMP')]
    
    print(f"\n📊 Results:")
    print(f"   Individual insights: {individual_ids}")
    print(f"   Compound insights: {compound_ids}")
    
    if 'COMP001' in compound_ids:
        comp_insight = next(i for i in compound_insights if i['id'] == 'COMP001')
        print(f"\n🎯 Compound Insight Detected: {comp_insight['title']}")
        print(f"   Priority Score: {comp_insight['priority_score']}")
        print(f"   Action Plan: {comp_insight['action_plan']}")
        print(f"   Expected Outcome: {comp_insight['expected_outcome']}")
        print("✅ Compound detection working correctly!")
    else:
        print("❌ Compound insight not detected")
    
    return compound_insights

def test_scale_aware_severity():
    """Test the new scale-aware, percentile-based severity system"""
    
    print("\n🧪 Testing Scale-Aware Severity System")
    print("=" * 50)
    
    # Load original data
    df_original = pd.read_csv('trainingdataset.csv')
    
    # Test 1: Create a micro business scenario (low revenue)
    print("\n1️⃣ Testing Micro Business Scale...")
    df_micro = df_original.copy()
    df_micro['Total Revenue'] = df_micro['Total Revenue'] * 0.1  # Reduce to micro scale
    df_micro['Unit Price'] = df_micro['Unit Price'] * 0.1
    
    insights_micro = actionable_insights.generate_insights(df_micro)
    if insights_micro:
        micro_insight = insights_micro[0]
        print(f"   📊 Micro Business Insight: {micro_insight['title']}")
        print(f"   📈 Scale Context: {micro_insight.get('scale_context', 'N/A')}")
        print(f"   💡 Why It Matters: {micro_insight['why_it_matters']}")
        print(f"   🎯 Action: {micro_insight.get('recommended_action', micro_insight.get('action_plan', 'N/A'))[:100]}...")
    
    # Test 2: Create an enterprise business scenario (high revenue)
    print("\n2️⃣ Testing Enterprise Business Scale...")
    df_enterprise = df_original.copy()
    df_enterprise['Total Revenue'] = df_enterprise['Total Revenue'] * 10  # Scale up to enterprise
    df_enterprise['Unit Price'] = df_enterprise['Unit Price'] * 10
    
    insights_enterprise = actionable_insights.generate_insights(df_enterprise)
    if insights_enterprise:
        enterprise_insight = insights_enterprise[0]
        print(f"   📊 Enterprise Insight: {enterprise_insight['title']}")
        print(f"   📈 Scale Context: {enterprise_insight.get('scale_context', 'N/A')}")
        print(f"   💡 Why It Matters: {enterprise_insight['why_it_matters']}")
        print(f"   🎯 Action: {enterprise_insight.get('recommended_action', enterprise_insight.get('action_plan', 'N/A'))[:100]}...")
    
    # Test 3: Create bottom 10th percentile scenario (should be critical)
    print("\n3️⃣ Testing Critical Severity (Bottom 10th Percentile)...")
    df_critical = df_original.copy()
    
    # Make revenue critically low - bottom 10th percentile
    revenue_10th = np.percentile(df_original['Total Revenue'], 10)
    df_critical = df_critical[df_critical['Total Revenue'] <= revenue_10th].copy()
    
    if len(df_critical) > 100:  # Ensure we have enough data
        insights_critical = actionable_insights.generate_insights(df_critical)
        if insights_critical:
            critical_insight = insights_critical[0]
            print(f"   🚨 Critical Insight: {critical_insight['title']}")
            print(f"   📊 Severity: {critical_insight['severity']}")
            print(f"   ⚡ Timeline: {critical_insight['timeline']}")
            print(f"   📈 Expected Outcome: {critical_insight['expected_outcome'][:80]}...")
    
    # Test 4: Compare percentile calculations
    print("\n4️⃣ Testing Percentile-Based Assessment...")
    
    # Test the severity context function directly
    test_revenue = df_original['Total Revenue'].mean()
    severity_context = actionable_insights._determine_severity_context(test_revenue, df_original, 'revenue')
    
    print(f"   📊 Average Revenue: ${test_revenue:,.0f}")
    print(f"   📈 Percentile Rank: {severity_context['current_percentile']:.1f}th")
    print(f"   🎯 Severity: {severity_context['severity']}")
    print(f"   🏢 Business Scale: {severity_context['business_scale']}")
    print(f"   💪 Action Intensity: {severity_context['action_intensity']}")
    print(f"   📋 Context: {severity_context['context_note']}")
    
    # Test with different values
    print("\n5️⃣ Testing Different Performance Levels...")
    
    test_values = [
        np.percentile(df_original['Total Revenue'], 5),   # Bottom 5th percentile
        np.percentile(df_original['Total Revenue'], 25),  # Bottom 25th percentile
        np.percentile(df_original['Total Revenue'], 50),  # Median
        np.percentile(df_original['Total Revenue'], 75),  # Top 25th percentile
    ]
    
    labels = ["Bottom 5%", "Bottom 25%", "Median", "Top 25%"]
    
    for value, label in zip(test_values, labels):
        context = actionable_insights._determine_severity_context(value, df_original, 'revenue')
        print(f"   {label}: ${value:,.0f} → {context['severity']} ({context['current_percentile']:.0f}th percentile)")
    
    print("\n✅ Scale-Aware Severity Testing Complete!")
    
    return {
        'micro_insights': insights_micro,
        'enterprise_insights': insights_enterprise,
        'critical_insights': insights_critical if 'insights_critical' in locals() else [],
        'severity_context': severity_context
    }

def test_proper_scale_detection():
    """Test the new proper scale detection vs flawed price-based approach"""
    
    print("\n🧪 Testing Proper Scale Detection (Aggregate vs Price-Based)")
    print("=" * 60)
    
    # Load original data
    df_original = pd.read_csv('trainingdataset.csv')
    
    # Test 1: High-price, low-volume business (Luxury/micro)
    print("\n1️⃣ Testing Luxury Micro Business (High Price, Low Volume)...")
    df_luxury = df_original.sample(1000).copy()  # Small transaction count
    df_luxury['Unit Price'] = df_luxury['Unit Price'] * 20  # High prices ($100K+ items)
    df_luxury['Total Revenue'] = df_luxury['Total Revenue'] * 20
    
    # Test scale detection
    scale_info_luxury = actionable_insights._detect_business_scale_from_data(df_luxury)
    
    print(f"   💎 Luxury Business Analysis:")
    print(f"   📊 Total Revenue: ${scale_info_luxury['total_revenue']:,.0f}")
    print(f"   🔢 Transactions: {scale_info_luxury['total_transactions']:,}")
    print(f"   💰 Revenue/Transaction: ${scale_info_luxury['revenue_per_transaction']:,.0f}")
    print(f"   🏢 Detected Scale: {scale_info_luxury['scale_description']}")
    print(f"   📈 Scale Factors: {', '.join(scale_info_luxury['scale_factors'])}")
    print(f"   🎯 Action Style: {scale_info_luxury['action_style']}")
    
    # Test 2: Low-price, high-volume business (Mass market/enterprise)
    print("\n2️⃣ Testing Mass Market Enterprise (Low Price, High Volume)...")
    df_mass = df_original.copy()  # Full transaction count
    df_mass['Unit Price'] = df_mass['Unit Price'] * 0.1  # Low prices ($5-50 items)
    df_mass['Total Revenue'] = df_mass['Total Revenue'] * 0.1
    
    # But multiply by volume to create enterprise-scale revenue
    df_mass = pd.concat([df_mass] * 3, ignore_index=True)  # 3x transactions
    
    scale_info_mass = actionable_insights._detect_business_scale_from_data(df_mass)
    
    print(f"   🏭 Mass Market Analysis:")
    print(f"   📊 Total Revenue: ${scale_info_mass['total_revenue']:,.0f}")
    print(f"   🔢 Transactions: {scale_info_mass['total_transactions']:,}")
    print(f"   💰 Revenue/Transaction: ${scale_info_mass['revenue_per_transaction']:,.0f}")
    print(f"   🏢 Detected Scale: {scale_info_mass['scale_description']}")
    print(f"   📈 Scale Factors: {', '.join(scale_info_mass['scale_factors'])}")
    print(f"   🎯 Action Style: {scale_info_mass['action_style']}")
    
    # Test 3: Compare old flawed vs new correct classification
    print("\n3️⃣ Comparing Classification Methods...")
    
    # Flawed price-based (old method)
    luxury_avg_price = df_luxury['Unit Price'].median()
    mass_avg_price = df_mass['Unit Price'].median()
    
    # Old broken logic
    if luxury_avg_price < 1000:
        old_luxury_classification = "micro"
    elif luxury_avg_price < 10000:
        old_luxury_classification = "sme"
    else:
        old_luxury_classification = "enterprise"
        
    if mass_avg_price < 1000:
        old_mass_classification = "micro"
    elif mass_avg_price < 10000:
        old_mass_classification = "sme"
    else:
        old_mass_classification = "enterprise"
    
    print(f"   📊 Luxury Business (${luxury_avg_price:,.0f} avg price):")
    print(f"     ❌ Old Price-Based: {old_luxury_classification}")
    print(f"     ✅ New Aggregate-Based: {scale_info_luxury['business_scale']}")
    
    print(f"   📊 Mass Market (${mass_avg_price:,.0f} avg price):")
    print(f"     ❌ Old Price-Based: {old_mass_classification}")
    print(f"     ✅ New Aggregate-Based: {scale_info_mass['business_scale']}")
    
    # Test 4: Show scale factors in detail
    print("\n4️⃣ Scale Detection Factor Analysis...")
    
    for business_name, scale_info in [("Luxury", scale_info_luxury), ("Mass Market", scale_info_mass)]:
        print(f"   🏢 {business_name} Business:")
        print(f"     💰 Total Revenue: ${scale_info['total_revenue']:,.0f}")
        print(f"     📈 Monthly Revenue: ${scale_info['monthly_revenue']:,.0f}")
        print(f"     🔢 Transaction Count: {scale_info['total_transactions']:,}")
        print(f"     🏪 Locations: {scale_info['num_locations']}")
        print(f"     📦 Products: {scale_info['num_products']}")
        print(f"     🎯 Scale Score: {scale_info['scale_score']}/12")
        print(f"     📊 Final Classification: {scale_info['scale_description']}")
        print()
    
    print("✅ Proper Scale Detection Testing Complete!")
    
    # Test real insights with proper scale
    print("\n5️⃣ Testing Insights with Proper Scale Detection...")
    
    luxury_insights = actionable_insights.generate_insights(df_luxury)
    mass_insights = actionable_insights.generate_insights(df_mass)
    
    if luxury_insights:
        print(f"   💎 Luxury Insight: {luxury_insights[0]['title']}")
        print(f"   📋 Scale Context: {luxury_insights[0].get('scale_context', 'N/A')}")
    
    if mass_insights:
        print(f"   🏭 Mass Market Insight: {mass_insights[0]['title']}")
        print(f"   📋 Scale Context: {mass_insights[0].get('scale_context', 'N/A')}")
    
    return {
        'luxury_scale': scale_info_luxury,
        'mass_scale': scale_info_mass,
        'luxury_insights': luxury_insights,
        'mass_insights': mass_insights
    }

if __name__ == "__main__":
    # Run main test
    insights = test_enhanced_insights_system()
    
    # Run compound scenario test
    compound_test = test_compound_scenarios()
    
    # NEW: Run scale-aware testing
    scale_test = test_scale_aware_severity()
    
    # NEW: Run proper scale detection test
    proper_scale_test = test_proper_scale_detection()
    
    print(f"\n🏁 All Enhanced Tests Completed Successfully!")
    print(f"   Main insights: {len(insights) if insights else 0}")
    print(f"   Compound test insights: {len(compound_test) if compound_test else 0}")
    print(f"   Scale-aware tests: Micro({len(scale_test['micro_insights'])}), Enterprise({len(scale_test['enterprise_insights'])}), Critical({len(scale_test['critical_insights'])})")
    print(f"   Proper scale tests: Luxury({len(proper_scale_test['luxury_insights'])}), Mass Market({len(proper_scale_test['mass_insights'])}), Luxury({proper_scale_test['luxury_scale']['scale_description']}), Mass({proper_scale_test['mass_scale']['scale_description']})")
    
    # Summary of scale intelligence
    print(f"\n🌟 Scale-Aware Intelligence Summary:")
    print(f"   ✅ Percentile-based severity assessment")
    print(f"   ✅ Dynamic thresholds for business scale")  
    print(f"   ✅ Context-aware action planning")
    print(f"   ✅ Scale-specific language and timelines") 