import { NextRequest, NextResponse } from 'next/server';

// Define the API endpoint URL
const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000';

export async function POST(request: NextRequest) {
  // Declare variables outside try block so they're accessible in catch block
  let transformedProducts: any[] = [];
  
  try {
    // Get request body
    const requestData = await request.json();
    
    // Log the original request data for debugging
    console.log("Received forecast-multiple request:", requestData);

    // Ensure products is an array
    if (!requestData.products || !Array.isArray(requestData.products) || requestData.products.length === 0) {
      return NextResponse.json(
        { error: "Missing or invalid products array" },
        { status: 400 }
      );
    }

    // Transform product data to match Flask API expectations
    // Keep the "All" location if specified, don't replace it
    transformedProducts = requestData.products.map((product: any) => {
      // Map frontend field names to backend expectations
      return {
        _ProductID: product.product_id || product._ProductID,
        Location: product.location || product.Location,
        'Unit Price': product.unit_price || product['Unit Price'],
        'Unit Cost': product.unit_cost || product['Unit Cost']
      };
    });

    console.log("Sending to Flask API:", { 
      products: transformedProducts,
      start_date: requestData.start_date,
      end_date: requestData.end_date,
      frequency: requestData.frequency,
      include_confidence: requestData.include_confidence !== false,
      aggregate_all_locations: true // Add flag to indicate we want proper aggregation
    });

    // All products processing with smart backend selection
    const isAutomaticForecast = requestData.products.length > 5; // Heuristic: many products = automatic forecast
    
    // Use all products - backend will choose fast aggregated vs detailed approach
    const productsToProcess = transformedProducts;
    
    console.log(`Processing forecast for all ${productsToProcess.length} products (automatic: ${isAutomaticForecast})`);
    
    // Removed timeout - let the ML processing complete naturally
    console.log("Processing without timeout restrictions");
    
    const response = await fetch(`${FLASK_API_URL}/forecast-multiple`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Connection': 'keep-alive'
      },
      body: JSON.stringify({
        products: productsToProcess, // Use optimized product selection
        start_date: requestData.start_date,
        end_date: requestData.end_date,
        frequency: requestData.frequency,
        include_confidence: requestData.include_confidence !== false
      }),
      // Extended timeouts for ML processing
      keepalive: true
    });

    // Check if response is ok
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Flask API returned ${response.status}: ${errorText}`);
      return NextResponse.json(
        { error: `Flask API error: ${response.status} - ${errorText}` },
        { status: response.status }
      );
    }

    // Parse response
    const responseData = await response.json();
    
    // Validate the response structure - update to handle both aggregated_forecast and forecasts
    if (!responseData.aggregated_forecast && (!responseData.forecasts || !Array.isArray(responseData.forecasts))) {
      console.error("Invalid response format from Flask API:", responseData);
      return NextResponse.json(
        { error: "Invalid response format from Flask API" },
        { status: 500 }
      );
    }
    
    // Log successful response
    const dataCount = responseData.aggregated_forecast 
      ? responseData.aggregated_forecast.length 
      : responseData.forecasts?.length || 0;
    console.log(`Received forecast data with ${dataCount} items`);

    // Return response
    return NextResponse.json(responseData);
  } catch (error: any) {
    console.error('Error in forecast-multiple API route:', error);
    
    // Return actual error (no timeout handling since timeout is removed)
    return NextResponse.json(
      { error: `Internal server error: ${error.message}` },
      { status: 500 }
    );
  }
} 