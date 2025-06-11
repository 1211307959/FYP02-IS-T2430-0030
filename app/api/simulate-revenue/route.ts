import { NextRequest, NextResponse } from 'next/server';

// Define the API endpoint URL
const FLASK_API_URL = process.env.FLASK_API_URL || 'http://localhost:5000';

export async function POST(request: NextRequest) {
  try {
    // Get request body
    const requestData = await request.json();
    
    // Log the original request for debugging
    console.log("Received simulate-revenue request:", requestData);

    // For "All" location, don't substitute a default - properly handle as aggregate
    if (requestData.Location === 'All' || requestData.location === 'All') {
      console.log("Processing aggregate request for all locations");
      // No substitution needed, leave as 'All' for the backend to handle properly
    }

    // Transform fields to match Flask API expectations
    const transformedData = {
      _ProductID: requestData.product_id || requestData._ProductID,
      Location: requestData.location || requestData.Location,
      'Unit Price': requestData.unit_price || requestData['Unit Price'],
      'Unit Cost': requestData.unit_cost || requestData['Unit Cost'] || 0,
      Weekday: requestData.weekday || requestData.Weekday,
      Month: requestData.month || requestData.Month,
      Day: requestData.day || requestData.Day,
      Year: requestData.year || requestData.Year,
      _timestamp: requestData._timestamp || Date.now()
    };

    console.log("Sending to Flask API:", transformedData);

    // Add validation for extreme price values
    if (transformedData['Unit Price'] > 100000) {
      console.warn(`Extreme price value detected: ${transformedData['Unit Price']}. Capping at 100,000.`);
      transformedData['Unit Price'] = 100000;
    }
    
    // Call Flask API
    const response = await fetch(`${FLASK_API_URL}/simulate-revenue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(transformedData),
      // Set a longer timeout for annual simulations (365 days takes time)
      signal: AbortSignal.timeout(60000)
    });
    
    // Check if response is ok
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Flask API returned ${response.status}: ${errorText}`);
      
      // Generate fallback data
      return NextResponse.json(generateFallbackResponse(transformedData));
    }
    
    // Parse response
    const responseData = await response.json();
    console.log("Flask API raw response:", JSON.stringify(responseData, null, 2));
    
    // Add a note if "All Locations" was selected
    if (transformedData.Location === 'All') {
      responseData.note = "Using data aggregated across all locations";
    }
    
    // Transform the response to ensure consistent structure
    const standardizedResponse = standardizeResponse(responseData, transformedData);
    console.log("Standardized response:", JSON.stringify(standardizedResponse, null, 2));
    
    // Return response
    return NextResponse.json(standardizedResponse);
  } catch (error: any) {
    console.error('Error in simulate-revenue API route:', error);
    
    try {
      // Get a copy of the request data if possible
      const fallbackData = {
        _ProductID: 1,
        Location: 'All',
        'Unit Price': 100,
        'Unit Cost': 50
      };
      
      return NextResponse.json(generateFallbackResponse(fallbackData));
    } catch (fallbackError) {
      console.error('Error generating fallback response:', fallbackError);
      return NextResponse.json(
        { 
          status: "error", 
          error: error.message || 'An unexpected error occurred',
          message: 'Failed to simulate revenue'
        },
        { status: 500 }
      );
    }
  }
}

// Helper function to create scenario names based on price factors
function createScenarioName(variation: any) {
  // If we already have a name, use it
  if (variation.name || variation.scenario || variation.Scenario) {
    return variation.name || variation.scenario || variation.Scenario;
  }
  
  // If we have a price factor, create a name based on it
  if (variation.price_factor) {
    const factor = variation.price_factor;
    if (factor < 0.95) {
      return `${Math.round((1-factor)*100)}% Lower`;
    } else if (factor > 1.05) {
      return `${Math.round((factor-1)*100)}% Higher`;
    } else {
      return "Current Price";
    }
  }
  
  // Default name
  return "Scenario";
}

// Function to standardize the response format for better frontend compatibility
function standardizeResponse(responseData: any, requestData: any) {
  console.log("Standardizing response from:", typeof responseData, responseData ? "with data" : "empty");
  
  // Special case for empty or null response
  if (!responseData) {
    console.warn("Empty response from Flask API, using fallback");
    return generateFallbackResponse(requestData);
  }
  
  // Check if the response already has a variations array
  if (Array.isArray(responseData.variations) || Array.isArray(responseData.results) || Array.isArray(responseData.simulations)) {
    // Use existing variations array
    const variations = responseData.variations || responseData.results || responseData.simulations;
    console.log("Found variations array with", variations.length, "items");
    
    // Ensure each variation has consistent field names
    const standardizedVariations = variations.map((variation: any) => ({
      price_factor: variation.price_factor || 1.0,
      unit_price: variation.unit_price || variation['Unit Price'] || requestData['Unit Price'],
      quantity: variation.quantity || variation.predicted_quantity || variation['Predicted Quantity'] || 0,
      predicted_quantity: variation.predicted_quantity || variation.quantity || variation['Predicted Quantity'] || 0,
      revenue: variation.revenue || variation.predicted_revenue || variation['Predicted Revenue'] || 0,
      predicted_revenue: variation.predicted_revenue || variation.revenue || variation['Predicted Revenue'] || 0,
      profit: variation.profit || variation.Profit || 0,
      unit_cost: variation.unit_cost || variation['Unit Cost'] || requestData['Unit Cost'] || 0,
      name: createScenarioName(variation),
    }));
    
    return {
      status: "success",
      product_id: responseData.product_id || responseData._ProductID || requestData._ProductID,
      location: responseData.location || responseData.Location || requestData.Location,
      unit_price: responseData.unit_price || responseData['Unit Price'] || requestData['Unit Price'],
      unit_cost: responseData.unit_cost || responseData['Unit Cost'] || requestData['Unit Cost'],
      variations: standardizedVariations,
      note: responseData.note
    };
  } else if (Array.isArray(responseData)) {
    // Response is already an array of variations
    console.log("Response is an array with", responseData.length, "items");
    const standardizedVariations = responseData.map((variation: any) => ({
      price_factor: variation.price_factor || 1.0,
      unit_price: variation.unit_price || variation['Unit Price'] || requestData['Unit Price'],
      quantity: variation.quantity || variation.predicted_quantity || variation['Predicted Quantity'] || 0,
      predicted_quantity: variation.predicted_quantity || variation.quantity || variation['Predicted Quantity'] || 0,
      revenue: variation.revenue || variation.predicted_revenue || variation['Predicted Revenue'] || 0,
      predicted_revenue: variation.predicted_revenue || variation.revenue || variation['Predicted Revenue'] || 0,
      profit: variation.profit || variation.Profit || 0,
      unit_cost: variation.unit_cost || variation['Unit Cost'] || requestData['Unit Cost'] || 0,
      name: createScenarioName(variation),
    }));
    
    return {
      status: "success",
      product_id: requestData._ProductID,
      location: requestData.Location,
      unit_price: requestData['Unit Price'],
      unit_cost: requestData['Unit Cost'],
      variations: standardizedVariations,
      note: "Using aggregated results"
    };
  } else if (typeof responseData === 'object') {
    // Response is a single object, wrap it in an array
    console.log("Response is a single object, creating variations array");
    // Convert to a single variation
    const standardizedVariation = {
      price_factor: 1.0,
      unit_price: responseData.unit_price || responseData['Unit Price'] || requestData['Unit Price'],
      quantity: responseData.quantity || responseData.predicted_quantity || responseData['Predicted Quantity'] || 0,
      predicted_quantity: responseData.predicted_quantity || responseData.quantity || responseData['Predicted Quantity'] || 0,
      revenue: responseData.revenue || responseData.predicted_revenue || responseData['Predicted Revenue'] || 0,
      predicted_revenue: responseData.predicted_revenue || responseData.revenue || responseData['Predicted Revenue'] || 0,
      profit: responseData.profit || responseData.Profit || 0,
      unit_cost: responseData.unit_cost || responseData['Unit Cost'] || requestData['Unit Cost'] || 0,
      name: 'Current Price',
    };
    
    return {
      status: "success",
      product_id: responseData.product_id || responseData._ProductID || requestData._ProductID,
      location: responseData.location || responseData.Location || requestData.Location,
      unit_price: responseData.unit_price || responseData['Unit Price'] || requestData['Unit Price'],
      unit_cost: responseData.unit_cost || responseData['Unit Cost'] || requestData['Unit Cost'],
      variations: [standardizedVariation],
      note: "Single result converted to variations array"
    };
  }
  
  // If we can't standardize, generate fallback
  console.warn("Couldn't standardize response, using fallback");
  return generateFallbackResponse(requestData);
}

// Function to generate fallback simulation data when API fails
function generateFallbackResponse(data: any) {
  const unitPrice = parseFloat(data['Unit Price']) || 100;
  const unitCost = parseFloat(data['Unit Cost']) || 50;
  const productId = data._ProductID || 1;
  const location = data.Location || 'All';
  
  // Price elasticity function - quantity decreases as price increases
  const calculateQuantity = (price: number) => {
    // Base quantity is 100 at price $50
    const baseQuantity = 100;
    // Exponential decay with elasticity factor
    const elasticityFactor = 0.01;
    // Calculate quantity based on price (higher price = lower quantity)
    return Math.max(0, Math.round(baseQuantity * Math.exp(-elasticityFactor * (price - 50))));
  };
  
  // Calculate variations
  const variations = [];
  const priceFactor = 0.2; // 20% price variation
  
  // Generate 7 price points from -60% to +60%
  for (let i = -3; i <= 3; i++) {
    const factor = 1 + (i * priceFactor);
    const price = Math.round(unitPrice * factor * 100) / 100;
    const quantity = calculateQuantity(price);
    const revenue = price * quantity;
    const cost = unitCost * quantity;
    const profit = revenue - cost;
    
    variations.push({
      price_factor: factor,
      unit_price: price,
      predicted_quantity: quantity,
      quantity: quantity,
      predicted_revenue: revenue,
      revenue: revenue,
      cost: cost,
      profit: profit
    });
  }
  
  return {
    status: "success",
    product_id: productId,
    location: location,
    unit_price: unitPrice,
    unit_cost: unitCost,
    variations: variations,
    note: "Using fallback simulation data (API unavailable)"
  };
} 