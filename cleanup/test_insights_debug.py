import pandas as pd
from business_insights_database import BusinessInsightsDatabase

# Load the data
try:
    df = pd.read_csv('trainingdataset.csv')
    print(f"✅ Data loaded: {len(df)} records")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit(1)

# Initialize the insights database
insights_db = BusinessInsightsDatabase()

# Calculate base statistics
stats = insights_db._calculate_base_statistics(df)

print("\n📊 Key Statistics:")
print(f"- Total Revenue: ${stats['total_revenue']:,.0f}")
print(f"- Average Revenue: ${stats['avg_revenue']:,.2f}")
print(f"- Average Margin: {stats['avg_margin']:.3f}")
print(f"- Price CV: {stats['price_cv']:.3f}")
print(f"- Top 3 Concentration: {stats['top_3_concentration']:.1f}%")
print(f"- Revenue Volatility: {stats['revenue_volatility']:.3f}")
print(f"- Location Performance Gap: {stats['location_performance_gap']:.1f}%")
print(f"- Product Performance Gap: {stats['product_performance_gap']:.1f}%")

print(f"\n🔍 Checking all {len(insights_db.insights_db)} insights:")

triggered_count = 0
not_triggered_count = 0

for insight_id, definition in insights_db.insights_db.items():
    try:
        # Check trigger condition
        triggered = insights_db._evaluate_trigger(definition.trigger_condition, stats)
        
        if triggered:
            triggered_count += 1
            # Calculate severity
            severity = insights_db._calculate_dynamic_severity(definition, stats)
            print(f"✅ {insight_id}: {definition.title} [TRIGGERED - {severity.upper()}]")
            print(f"    Trigger: {definition.trigger_condition}")
        else:
            not_triggered_count += 1
            print(f"❌ {insight_id}: {definition.title} [NOT TRIGGERED]")
            print(f"    Trigger: {definition.trigger_condition}")
            
    except Exception as e:
        print(f"⚠️ {insight_id}: Error - {e}")

print(f"\n📈 Summary:")
print(f"- Triggered insights: {triggered_count}")
print(f"- Not triggered insights: {not_triggered_count}")
print(f"- Total insights in database: {len(insights_db.insights_db)}")

# Test with actual generation
print(f"\n🎯 Actual generated insights:")
insights = insights_db.generate_insights(df)
for insight in insights:
    print(f"- {insight['id']}: {insight['title']} (Score: {insight.get('priority_score', 0):.1f})") 