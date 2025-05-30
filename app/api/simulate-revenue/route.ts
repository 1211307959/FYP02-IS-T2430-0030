import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Get request body
    const data = await request.json();
    
    // Add timestamp to prevent caching
    const timestamp = new Date().getTime();
    const requestData = { ...data, _timestamp: timestamp };
    
    // Log incoming request for debugging
    console.log('Simulate revenue request:', requestData);
    
    // Define Flask API URL from environment variables
    const apiUrl = process.env.FLASK_API_URL || 'http://localhost:5000';
    
    // Handle missing or null values
    const processedData = { ...requestData };
    
    // Check if this is an "All Locations" request and mark it specially
    const isAllLocations = processedData.locationId === 'All';
    
    // Convert locationId to Location format expected by backend
    if (processedData.locationId) {
      processedData.Location = processedData.locationId;
      delete processedData.locationId;
    }
    
    // Convert productId to _ProductID format expected by backend
    if (processedData.productId) {
      processedData._ProductID = processedData.productId ? parseInt(String(processedData.productId), 10) : 1;
      delete processedData.productId;
    }
    
    // Ensure Unit Price is correctly formatted
    if (processedData.unitPrice !== undefined) {
      processedData['Unit Price'] = processedData.unitPrice;
      delete processedData.unitPrice;
    }
    
    // Ensure Unit Cost is correctly formatted
    if (processedData.unitCost !== undefined) {
      processedData['Unit Cost'] = processedData.unitCost;
      delete processedData.unitCost;
    }
    
    // Handle null/undefined values for required fields
    if (processedData._ProductID === null || processedData._ProductID === undefined) {
      processedData._ProductID = 1; // Default product ID
    }
    
    if (processedData['Unit Price'] === null || processedData['Unit Price'] === undefined) {
      processedData['Unit Price'] = 100.0; // Default price
    }
    
    if (processedData['Unit Cost'] === null || processedData['Unit Cost'] === undefined) {
      processedData['Unit Cost'] = 50.0; // Default cost
    }
    
    // Ensure numeric fields are properly typed
    processedData._ProductID = parseInt(String(processedData._ProductID), 10);
    processedData['Unit Price'] = parseFloat(String(processedData['Unit Price']));
    processedData['Unit Cost'] = parseFloat(String(processedData['Unit Cost']));
    
    // Add current date if missing
    const today = new Date();
    if (!processedData.Month) {
      processedData.Month = today.getMonth() + 1; // Months are 0-indexed in JS
    }
    if (!processedData.Day) {
      processedData.Day = today.getDate();
    }
    if (!processedData.Year) {
      processedData.Year = today.getFullYear();
    }
    
    // Handle Weekday formatting
    if (!processedData.Weekday && processedData.Day) {
      // Generate weekday from date if possible
      const date = new Date(processedData.Year, processedData.Month - 1, processedData.Day);
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      processedData.Weekday = days[date.getDay()];
    } else if (!processedData.Weekday) {
      // Default to current day of week if not provided
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      processedData.Weekday = days[today.getDay()];
    }
    
    // Check for extreme price values that might cause backend errors
    if (processedData['Unit Price'] > 100000) {
      return NextResponse.json({
        status: 'error',
        error: 'Unit Price exceeds maximum allowed value (100000)'
      }, { status: 400 });
    }
    
    // Log the transformed data being sent to Flask
    console.log('Sending to Flask API:', processedData);
    
    // Call Flask API
    const flaskResponse = await fetch(`${apiUrl}/simulate-revenue`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache'
      },
      body: JSON.stringify(processedData),
      // Set a reasonable timeout
      signal: AbortSignal.timeout(15000)
    });
    
    // Check for errors
    if (!flaskResponse.ok) {
      const errorText = await flaskResponse.text();
      console.error('Flask API error:', errorText);
      throw new Error(`Flask API returned ${flaskResponse.status}: ${errorText}`);
    }
    
    // Parse response
    const responseData = await flaskResponse.json();
    
    // Log response for debugging
    console.log('Flask API response status:', responseData.status);
    console.log('Results count:', 
      responseData.results?.length || responseData.simulations?.length || 0);
    
    // Handle both possible field names for compatibility
    const resultData = responseData.results || responseData.simulations || [];
    
    // Normalize the response to ensure consistent field names
    // This ensures the frontend always gets predictable field names regardless of backend changes
    const normalizedResults = resultData.map((item: any) => ({
      Scenario: item.Scenario || item.scenario || 'Unknown',
      'Unit Price': item['Unit Price'] || item.unitPrice || 0,
      'Predicted Revenue': item['Predicted Revenue'] || item.revenue || item.predicted_revenue || 0,
      'Predicted Quantity': item['Predicted Quantity'] || item.quantity || item.predicted_quantity || 0,
      'Profit': item.Profit || item.profit || 0,
      // Include these fields for compatibility with different consumers
      revenue: item['Predicted Revenue'] || item.revenue || item.predicted_revenue || 0,
      quantity: item['Predicted Quantity'] || item.quantity || item.predicted_quantity || 0,
      profit: item.Profit || item.profit || 0,
      // Include location-specific metadata if available
      locations_averaged: item.locations_averaged,
    }));
    
    // Create a consistent response structure
    const responsePayload = {
      status: responseData.status || 'success',
      results: normalizedResults,
      simulations: normalizedResults, // Include both field names for compatibility
      note: responseData.note, // Preserve any notes from backend
      isAllLocations: isAllLocations, // Add this flag to the response
    };
    
    // If this was an "All Locations" request and there's no note from the backend, add a default note
    if (isAllLocations && !responsePayload.note) {
      responsePayload.note = "Using combined data from all locations. Results represent the sum across all regions.";
    }
    
    // Return normalized response with cache control headers
    return NextResponse.json(responsePayload, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
    
  } catch (error: any) {
    console.error('Error in simulate-revenue route:', error);
    
    // Return a structured error response
    return NextResponse.json({
      status: 'error',
      error: error.message || 'An unexpected error occurred',
      details: error.toString()
    }, { status: 500 });
  }
} 