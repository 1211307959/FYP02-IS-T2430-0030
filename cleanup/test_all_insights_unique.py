#!/usr/bin/env python3
"""
Test script to verify all 50 insights have unique, dynamic content
"""

import pandas as pd
import business_insights_database

def test_all_insights_unique():
    print("🔍 Testing All 50 Insights for Unique Dynamic Content\n")
    
    # Load sample data
    try:
        df = pd.read_csv('trainingdataset.csv')
        print(f"✅ Loaded {len(df):,} transaction records")
    except:
        print("❌ Could not load data file")
        return
    
    # Initialize insights database
    db = business_insights_database.BusinessInsightsDatabase()
    
    # Generate insights
    insights = db.generate_insights(df)
    print(f"📊 Generated {len(insights)} insights from data\n")
    
    # Test each insight for unique content
    detailed_analyses = []
    kpi_targets = []
    implementation_plans = []
    expected_outcomes = []
    
    print("🧪 Testing Dynamic Content Generation:\n")
    
    for insight in insights:
        insight_id = insight.get('id', 'Unknown')
        
        # Check detailed analysis
        detailed_analysis = insight.get('detailed_analysis', '')
        detailed_analyses.append(detailed_analysis)
        
        # Check KPI targets
        kpi_targets_list = insight.get('kpi_targets', [])
        kpi_targets.extend([kpi.get('target', '') for kpi in kpi_targets_list])
        
        # Check implementation plan  
        impl_plan = insight.get('implementation_plan', [])
        implementation_plans.extend([step.get('action', '') for step in impl_plan])
        
        # Check expected outcome
        expected_outcome = insight.get('expected_outcome', '')
        expected_outcomes.append(expected_outcome)
        
        print(f"   {insight_id}: {insight.get('title', 'No title')}")
        print(f"      📝 Analysis: {len(detailed_analysis)} chars")
        print(f"      🎯 KPIs: {len(kpi_targets_list)} targets")
        print(f"      📋 Steps: {len(impl_plan)} implementation steps")
        print(f"      💡 Outcome: {len(expected_outcome)} chars")
        
        # Check for generic content
        if "This insight requires" in detailed_analysis or len(detailed_analysis) < 50:
            print(f"      ⚠️  Generic/Short detailed analysis detected")
        if len(expected_outcome) < 50:
            print(f"      ⚠️  Generic/Short expected outcome detected")
        
        print()
    
    # Check for duplicates
    print("🔍 Checking for Duplicate Content:\n")
    
    unique_analyses = len(set(detailed_analyses))
    unique_outcomes = len(set(expected_outcomes))
    unique_kpis = len(set(kpi_targets))
    unique_steps = len(set(implementation_plans))
    
    print(f"📊 Content Uniqueness Results:")
    print(f"   Detailed Analyses: {unique_analyses}/{len(detailed_analyses)} unique ({unique_analyses/len(detailed_analyses)*100:.1f}%)")
    print(f"   Expected Outcomes: {unique_outcomes}/{len(expected_outcomes)} unique ({unique_outcomes/len(expected_outcomes)*100:.1f}%)")
    print(f"   KPI Targets: {unique_kpis}/{len(kpi_targets)} unique ({unique_kpis/len(kpi_targets)*100:.1f}%)")
    print(f"   Implementation Steps: {unique_steps}/{len(implementation_plans)} unique ({unique_steps/len(implementation_plans)*100:.1f}%)")
    
    # Overall assessment
    print(f"\n🎯 ASSESSMENT:")
    if unique_analyses == len(detailed_analyses) and unique_outcomes == len(expected_outcomes):
        print(f"✅ PASS: All insights have unique content!")
    else:
        print(f"❌ FAIL: Some insights have duplicate content!")
        print(f"🔧 NEEDED: Extend dynamic content generation to support all 50 insight IDs")
    
    return insights

if __name__ == "__main__":
    test_all_insights_unique() 