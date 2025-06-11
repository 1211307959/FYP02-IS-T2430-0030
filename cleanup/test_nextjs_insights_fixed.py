#!/usr/bin/env python3
"""
Test the NextJS insights API route to verify it connects to Flask properly
"""

import requests
import json

def test_nextjs_insights():
    """Test the NextJS /api/insights endpoint"""
    try:
        print('🔍 Testing NextJS /api/insights endpoint...')
        
        # Test the NextJS API route (assuming Next.js runs on 3000)
        response = requests.get('http://localhost:3000/api/insights', timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f'✅ NextJS API Response Success: {data.get("success", False)}')
            print(f'📊 Total Insights: {data.get("total_insights", 0)}')
            print(f'🎯 Max Shown: {data.get("max_insights_shown", 0)}')
            
            insights = data.get('insights', [])
            print(f'\n🏆 Insights from NextJS (showing first 3):')
            for i, insight in enumerate(insights[:3]):
                title = insight.get('title', 'Unknown')
                score = insight.get('priority_score', 0)
                severity = insight.get('severity', 'unknown')
                category = insight.get('category', 'unknown')
                ml_flag = '🤖' if insight.get('ml_integrated', False) else '📊'
                description = insight.get('description', 'No description')[:100] + '...'
                print(f'{i+1:2d}. [{score:5.1f}] {severity.upper():8s} | {category:10s} | {ml_flag} {title}')
                print(f'    Description: {description}')
            
            note = data.get('note', 'No note')
            print(f'\n💡 Note: {note}')
            
            if 'fallback' in note.lower():
                print('⚠️  WARNING: NextJS is using fallback data - not connecting to Flask!')
                print('    This means the frontend will show generic insights instead of real data.')
                return False
            else:
                print('✅ NextJS API route successfully connecting to Flask backend!')
                return True
        else:
            print(f'❌ NextJS API returned status code: {response.status_code}')
            print(f'Response: {response.text[:200]}...')
            return False
            
    except requests.exceptions.ConnectionError:
        print('🔌 Connection error - NextJS server may not be running on port 3000')
        print('    Make sure to run "npm run dev" to start the NextJS server')
        return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    test_nextjs_insights() 