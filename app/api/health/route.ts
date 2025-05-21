import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Define base URL for the Flask API
    const apiUrl = process.env.FLASK_API_URL || 'http://localhost:5000';
    
    // Check if the Flask API is running
    const response = await fetch(`${apiUrl}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { status: 'unhealthy', message: 'API service is not responding properly' },
        { status: 503 }
      );
    }
    
    // If we got a successful response, the API is healthy
    return NextResponse.json({ status: 'healthy', message: 'API service is running normally' });
    
  } catch (error) {
    console.error('Error checking API health:', error);
    return NextResponse.json(
      { status: 'unhealthy', message: 'Could not connect to API service' },
      { status: 503 }
    );
  }
} 