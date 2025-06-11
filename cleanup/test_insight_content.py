import pandas as pd
from business_insights_database import BusinessInsightsDatabase

# Load the data
df = pd.read_csv('trainingdataset.csv')
print(f"✅ Data loaded: {len(df)} records")

# Initialize the insights database
insights_db = BusinessInsightsDatabase()

# Generate insights
insights = insights_db.generate_insights(df)

print(f"\n🎯 Generated {len(insights)} insights")
print(f"Now testing their content...")

for i, insight in enumerate(insights[:5], 1):  # Test top 5
    print(f"\n{'='*60}")
    print(f"INSIGHT {i}: {insight['id']} - {insight['title']}")
    print(f"Category: {insight['category']} | Severity: {insight['severity']} | Score: {insight.get('priority_score', 0):.1f}")
    print(f"{'='*60}")
    
    print(f"\n📝 DESCRIPTION:")
    print(insight.get('description', 'N/A'))
    
    print(f"\n🔍 DETAILED ANALYSIS:")
    print(insight.get('detailed_analysis', 'N/A'))
    
    print(f"\n💡 RECOMMENDATION:")
    print(insight.get('recommendation', 'N/A'))
    
    print(f"\n📊 KPI TARGETS:")
    for j, kpi in enumerate(insight.get('kpi_targets', [])[:3], 1):  # Show top 3 KPIs
        print(f"  {j}. {kpi.get('kpi', 'N/A')}: {kpi.get('current', 'N/A')} → {kpi.get('target', 'N/A')}")
    
    print(f"\n🎯 EXPECTED OUTCOME:")
    print(insight.get('expected_outcome', 'N/A'))

print(f"\n{'='*60}")
print("✅ Content test complete! Each insight should have unique content.") 