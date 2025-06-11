import pandas as pd
from simple_insights_database import SimpleInsightsDatabase

# Load the data
df = pd.read_csv('trainingdataset.csv')
print(f"✅ Data loaded: {len(df)} records")

# Initialize the simple insights database
insights_db = SimpleInsightsDatabase()

# Generate insights
insights = insights_db.generate_insights(df)

print(f"\n🎯 Generated {len(insights)} insights")
print("="*70)

for insight in insights:
    print(f"\n📊 {insight['title']} ({insight['id']})")
    print(f"Category: {insight['category']} | Severity: {insight['severity']} | Score: {insight['priority_score']:.1f}")
    print(f"Description: {insight['description']}")
    print(f"Recommendation: {insight['recommendation']}")
    print(f"Impact: {insight['impact']}")
    print("-" * 70)

print("\n✅ Simple insights test complete!") 