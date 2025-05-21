import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    // Define base URL for the Flask API
    const apiUrl = process.env.FLASK_API_URL || 'http://localhost:5000';
    
    // Get the request body
    const requestData = await request.json();
    
    // Log request data for debugging
    console.log('Request to simulate-revenue endpoint:', JSON.stringify(requestData, null, 2));
    
    // Forward the request to the Flask API
    const response = await fetch(`${apiUrl}/simulate-revenue`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
      // Add timeout
      signal: AbortSignal.timeout(20000),
    }).catch(error => {
      console.error('Fetch error in simulate-revenue:', error);
      throw error;
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      let errorData;
      
      try {
        errorData = JSON.parse(errorText);
      } catch (e) {
        console.error('Failed to parse error response as JSON:', errorText);
        errorData = { error: `HTTP ${response.status}: ${errorText}` };
      }
      
      console.error('Flask API error:', errorData);
      throw new Error(errorData.error || `Failed to simulate revenue scenarios: HTTP ${response.status}`);
    }
    
    // Get the response text first
    const responseText = await response.text();
    
    // Try to parse as JSON
    let responseData;
    try {
      responseData = JSON.parse(responseText);
    } catch (e) {
      console.error('Failed to parse response as JSON:', responseText);
      throw new Error('Invalid JSON response from API');
    }
    
    // Log response for debugging
    console.log('Response from Flask API:', JSON.stringify(responseData, null, 2));
    
    // Check for required fields
    if (responseData.status === 'success') {
      // Handle different response formats
      const results = responseData.results || responseData.simulations || [];
      
      // Format the response consistently
      return NextResponse.json({
        status: 'success',
        results: results
      });
    } else {
      throw new Error(responseData.error || 'Unknown error in API response');
    }
    
  } catch (error) {
    console.error('Error in simulate revenue endpoint:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to simulate revenue scenarios' },
      { status: 500 }
    );
  }
} 