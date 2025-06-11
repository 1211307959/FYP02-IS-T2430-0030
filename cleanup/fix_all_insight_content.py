#!/usr/bin/env python3
"""
Comprehensive fix for all 50 insights to have unique, dynamic content
"""

import pandas as pd
import business_insights_database

def generate_missing_content():
    """Generate the missing KPI targets, implementation plans, and expected outcomes for all 50 insights"""
    
    print("🔧 Fixing All 50 Insights for Complete Dynamic Content\n")
    
    # Load insights database
    db = business_insights_database.BusinessInsightsDatabase()
    insights_db = db._initialize_insights_database()
    
    print(f"📋 Total insights in database: {len(insights_db)}")
    
    # Check which insight IDs need content generation
    all_insight_ids = list(insights_db.keys())
    
    # Current supported insight IDs in content generation functions
    supported_ids = ['PR001', 'PR002', 'P001', 'P002', 'G001', 'F001', 'F002', 'F003', 'F004', 'L001']
    
    missing_ids = [id for id in all_insight_ids if id not in supported_ids]
    
    print(f"✅ Currently supported: {len(supported_ids)} insights")
    print(f"❌ Missing content generation: {len(missing_ids)} insights")
    print(f"🎯 Missing IDs: {missing_ids}\n")
    
    print("📝 Content Generation Requirements:")
    print("   - KPI Targets: Each insight needs 3 unique KPI targets with current/target values")
    print("   - Implementation Plan: Each insight needs 3-4 unique steps with specific timelines")
    print("   - Expected Outcome: Each insight needs unique outcome with specific percentages/values")
    
    return missing_ids

def test_current_content():
    """Test current content generation coverage"""
    try:
        df = pd.read_csv('trainingdataset.csv')
        db = business_insights_database.BusinessInsightsDatabase()
        insights = db.generate_insights(df)
        
        print(f"\n🧪 Current Test Results:")
        print(f"   Generated insights: {len(insights)}")
        
        for insight in insights:
            insight_id = insight.get('id', 'Unknown')
            
            # Check content types
            detailed_analysis = insight.get('detailed_analysis', '')
            kpi_targets = insight.get('kpi_targets', [])
            impl_plan = insight.get('implementation_plan', [])
            expected_outcome = insight.get('expected_outcome', '')
            
            # Check for generic content indicators
            is_generic_analysis = len(detailed_analysis) < 200 or "This insight requires" in detailed_analysis
            is_generic_outcome = len(expected_outcome) < 200 or "improvement through" in expected_outcome
            has_generic_kpis = len(kpi_targets) < 3 or any("Baseline" in str(kpi) for kpi in kpi_targets)
            
            status = "❌ GENERIC" if (is_generic_analysis or is_generic_outcome or has_generic_kpis) else "✅ UNIQUE"
            print(f"   {insight_id}: {status}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    missing_ids = generate_missing_content()
    test_current_content()
    
    print(f"\n🎯 ACTION NEEDED:")
    print(f"   Extend _generate_kpi_targets() to support {len(missing_ids)} additional insight IDs")
    print(f"   Extend _generate_implementation_plan() to support {len(missing_ids)} additional insight IDs") 
    print(f"   Extend _generate_expected_outcome() to support {len(missing_ids)} additional insight IDs")
    print(f"   This will achieve 100% unique content across all 50 insights") 