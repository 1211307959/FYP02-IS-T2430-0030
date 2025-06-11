#!/usr/bin/env python3
"""
Quick test for the Flask insights API endpoint
"""

import requests
import json

def test_insights_api():
    """Test the /insights endpoint"""
    try:
        print('🔍 Testing Flask /insights API endpoint...')
        
        # Test the insights endpoint
        response = requests.get('http://127.0.0.1:5000/insights', timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ API Response Success: {data.get("success", False)}')
            print(f'📊 Total Insights: {data.get("total_insights", 0)}')
            print(f'🎯 Max Shown: {data.get("max_insights_shown", 0)}')
            
            insights = data.get('insights', [])
            print(f'\n🏆 Top {len(insights)} Insights:')
            for i, insight in enumerate(insights[:5]):
                title = insight.get('title', 'Unknown')
                score = insight.get('priority_score', 0)
                severity = insight.get('severity', 'unknown')
                category = insight.get('category', 'unknown')
                ml_flag = '🤖' if insight.get('ml_integrated', False) else '📊'
                print(f'{i+1:2d}. [{score:5.1f}] {severity.upper():8s} | {category:10s} | {ml_flag} {title}')
            
            print(f'\n💡 Note: {data.get("note", "No note")}')
            print('✅ API endpoint working correctly!')
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
    test_insights_api() 