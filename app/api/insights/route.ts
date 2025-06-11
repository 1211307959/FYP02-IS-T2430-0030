import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic'; // Disable static caching of this route

/**
 * Handles GET requests to fetch business insights data
 */
export async function GET(request: NextRequest) {
  try {
    // Get the Flask backend URL
    const backendUrl = process.env.FLASK_BACKEND_URL || 'http://127.0.0.1:5000';
    
    // Parse URL to get query parameters
    const { searchParams } = new URL(request.url);
    const category = searchParams.get('category') || '';
    
    // Forward request to Flask backend
    const flaskUrl = `${backendUrl}/insights${category ? `?category=${category}` : ''}`;
    
    const response = await fetch(flaskUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Flask API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching insights:', error);
    
    // Return fallback insights with ML integration indicators
    const fallbackInsights = [
      {
        id: 'F001',
        title: 'Revenue Performance Alert',
        description: 'Total revenue analysis shows current business performance metrics.',
        category: 'financial',
        severity: 'medium',
        impact: 'high',
        priority: 85.5,
        recommendation: 'Monitor revenue trends and identify growth opportunities.',
        ml_integrated: false
      },
      {
        id: 'PR001', 
        title: 'ML Pricing Optimization',
        description: 'ML analysis identifies significant pricing optimization opportunities.',
        category: 'pricing',
        severity: 'high',
        impact: 'high',
        priority: 92.3,
        recommendation: 'Use scenario planner to test ML-recommended price adjustments.',
        ml_integrated: true
      },
      {
        id: 'P003',
        title: 'ML Product Optimization',
        description: 'ML model identifies optimization opportunities for multiple products.',
        category: 'product',
        severity: 'medium',
        impact: 'medium',
        priority: 78.9,
        recommendation: 'Use scenario planner to test ML-recommended optimizations.',
        ml_integrated: true
      }
    ];

    return NextResponse.json({
      success: true,
      insights: fallbackInsights,
      total_insights: fallbackInsights.length,
      note: "Using fallback insights - Flask backend unavailable"
    });
  }
} 