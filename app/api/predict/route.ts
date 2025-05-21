import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    // Parse the request body
    const body = await request.json();
    
    // Define base URL for the Flask API
    const apiUrl = process.env.FLASK_API_URL || 'http://localhost:5000';
    
    // Make request to the Flask API's predict-revenue endpoint
    const response = await fetch(`${apiUrl}/predict-revenue`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to predict revenue');
    }
    
    const prediction = await response.json();
    
    // Return the prediction results
    return NextResponse.json(prediction);
    
  } catch (error) {
    console.error('Error in prediction API route:', error);
    return NextResponse.json(
      { error: 'Failed to predict revenue' },
      { status: 500 }
    );
  }
} 