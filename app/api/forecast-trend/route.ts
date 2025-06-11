import { NextResponse } from 'next/server';

// API base URL - adjust as needed for your environment
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5000';

export async function POST(request: Request) {
  try {
    // Get request body
    const body = await request.json();
    
    // Validate required fields
    const { product_id, location, base_price, unit_cost, start_date, end_date } = body;
    if (!product_id || !location || !base_price || !unit_cost || !start_date || !end_date) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }
    
    // Transform fields to match what the Flask API expects
    const transformedBody = {
      '_ProductID': product_id,
      'Location': location,
      'Unit Price': base_price, // The API expects 'Unit Price' not 'base_price'
      'Unit Cost': unit_cost,
      'start_date': start_date,
      'end_date': end_date,
      'price_variations': body.price_variations || [0.8, 0.9, 1.0, 1.1, 1.2],
      'frequency': body.frequency || 'D'
    };
    
    console.log('Sending to Flask API:', transformedBody);
    
    // Forward request to Flask API with the correct endpoint
    const response = await fetch(`${API_BASE_URL}/forecast-trend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(transformedBody),
    });
    
    if (!response.ok) {
      console.error(`API returned status ${response.status}: ${response.statusText}`);
      const errorText = await response.text();
      console.error('Error response:', errorText);
      return NextResponse.json(
        { error: `API returned status ${response.status}` },
        { status: response.status }
      );
    }
    
    // Get response data
    const data = await response.json();
    
    // Return response from API
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in forecast-trend API route:', error);
    return NextResponse.json(
      { error: 'Failed to forecast product trend' },
      { status: 500 }
    );
  }
} 