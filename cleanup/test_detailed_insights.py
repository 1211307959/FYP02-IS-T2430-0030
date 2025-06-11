#!/usr/bin/env python3
"""
Detailed insights test to show full content of insights
"""

import requests
import json

def test_detailed_insights():
    """Test and display full insight details"""
    try:
        print('🔍 Testing Flask /insights API with full details...\n')
        
        # Test the insights endpoint
        response = requests.get('http://127.0.0.1:5000/insights', timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ API Response Success: {data.get("success", False)}')
            print(f'📊 Total Insights Generated: {data.get("total_insights", 0)}')
            print(f'🎯 Max Insights Shown: {data.get("max_insights_shown", 0)}')
            print(f'📈 Data Source: {data.get("note", "No note")}')
            print('=' * 80)
            
            insights = data.get('insights', [])
            
            for i, insight in enumerate(insights):
                print(f'\n🏆 INSIGHT #{i+1} - RANK {insight.get("rank", "N/A")}')
                print(f'📊 Title: {insight.get("title", "Unknown")}')
                print(f'🎯 Category: {insight.get("category", "unknown").upper()}')
                print(f'⚡ Severity: {insight.get("severity", "unknown").upper()}')
                print(f'🎲 Priority Score: {insight.get("priority_score", 0)}')
                ml_flag = '🤖 ML-POWERED' if insight.get('ml_integrated', False) else '📊 DATA-DRIVEN'
                print(f'🔧 Type: {ml_flag}')
                print(f'🌟 Featured: {"YES" if insight.get("is_top_insight", False) else "NO"}')
                
                print(f'\n📝 DESCRIPTION:')
                print(f'{insight.get("description", "No description available")}')
                
                print(f'\n💡 RECOMMENDATIONS:')
                print(f'{insight.get("recommendation", "No recommendations available")}')
                
                print('\n' + '─' * 80)
            
            print(f'\n✅ Successfully displayed {len(insights)} detailed insights!')
            return True
        else:
            print(f'❌ API returned status code: {response.status_code}')
            print(f'Response: {response.text[:200]}...')
            return False
            
    except requests.exceptions.Timeout:
        print('⏰ Request timed out - API may be slow or not responding')
        return False
    except requests.exceptions.ConnectionError:
        print('🔌 Connection error - Flask server may not be running')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    test_detailed_insights() 