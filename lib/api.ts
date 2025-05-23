/**
 * API client for connecting to the Revenue Prediction Flask API
 */

// Use the Next.js proxy path instead of direct API URL
const API_BASE_URL = '/api';

// Common fetch options with timeout
const fetchWithTimeout = async (url: string, options: RequestInit = {}, timeout = 15000) => {
  const controller = new AbortController();
  const { signal } = controller;
  
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, { ...options, signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
};

/**
 * Check if the API is healthy
 */
export async function checkApiHealth() {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      return { status: 'unhealthy', message: 'API returned an error status' };
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error checking API health:', error);
    
    if (error instanceof DOMException && error.name === 'AbortError') {
      return { status: 'unhealthy', message: 'API request timed out' };
    }
    
    return { status: 'unhealthy', message: 'Could not connect to API' };
  }
}

/**
 * Get available data files
 */
export async function getDataFiles() {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/data-files`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch data files');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching data files:', error);
    throw error;
  }
}

/**
 * Select a data file to use
 */
export async function selectDataFile(filename: string) {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/select-data-file`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ filename }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to select data file');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error selecting data file:', error);
    throw error;
  }
}

/**
 * Load CSV data from the data directory (for testing purposes)
 */
export async function loadSampleCsvData() {
  try {
    const response = await fetch('/data/Adjusted_Sales_Data_With_Time_Features.csv');
    
    if (!response.ok) {
      throw new Error(`Failed to load sample CSV data: ${response.statusText}`);
    }
    
    const csvText = await response.text();
    return csvText;
  } catch (error) {
    console.error('Error loading sample CSV data:', error);
    throw error;
  }
}

/**
 * Get all products from the dataset
 */
export async function getProducts() {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/products`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch products');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
}

/**
 * Get all locations from the dataset
 */
export async function getLocations() {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/locations`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch locations');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching locations:', error);
    throw error;
  }
}

/**
 * Legacy function for backwards compatibility
 * @deprecated Use getLocations() instead
 */
export async function getCustomers() {
  return getLocations();
}

/**
 * Get dashboard data
 */
export async function getDashboardData(cacheBustQuery?: string) {
  try {
    // Fix the URL construction - don't append query string directly
    const baseUrl = `${API_BASE_URL}/dashboard-data`;
    
    // If we have a query string that starts with ?, use it, otherwise create one
    const queryString = cacheBustQuery && cacheBustQuery.startsWith('?') 
      ? cacheBustQuery 
      : `?_=${new Date().getTime()}`;
    
    const url = `${baseUrl}${queryString}`;
    console.log(`Fetching dashboard data from: ${url}`);
    
    const response = await fetchWithTimeout(url, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch dashboard data');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
}

/**
 * Make a revenue prediction
 */
export async function predictRevenue(orderData: any) {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to predict revenue');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error predicting revenue:', error);
    throw error;
  }
}

/**
 * Simulate different scenarios
 */
export async function simulateScenarios(baseData: any, scenarios?: any[]) {
  try {
    // Fix any potential format issues with the data
    const fixedBaseData = { ...baseData };
    
    // Ensure ProductID is properly formatted as a number
    if (fixedBaseData._ProductID && typeof fixedBaseData._ProductID === 'string') {
      fixedBaseData._ProductID = parseInt(fixedBaseData._ProductID, 10);
    }
    
    // Ensure required numeric fields are numbers
    if (typeof fixedBaseData['Unit Price'] === 'string') {
      fixedBaseData['Unit Price'] = parseFloat(fixedBaseData['Unit Price']);
    }
    if (typeof fixedBaseData['Unit Cost'] === 'string') {
      fixedBaseData['Unit Cost'] = parseFloat(fixedBaseData['Unit Cost']);
    }
    
    // Create the request body
    const requestBody = fixedBaseData;
    
    // Add optional parameters
    if (scenarios && scenarios.length > 0) {
      // The API doesn't use the scenarios property directly
      // Just add min/max price factors and steps
      requestBody.min_price_factor = 0.5;
      requestBody.max_price_factor = 2.0;
      requestBody.steps = 7;
    }
    
    console.log('Sending request to simulate-revenue endpoint:', JSON.stringify(requestBody, null, 2));
    
    // Use a longer timeout for simulation requests (15 seconds)
    const response = await fetchWithTimeout(`${API_BASE_URL}/simulate-revenue`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    }, 15000);
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Error from simulate-revenue endpoint:', errorData);
      throw new Error(errorData.error || 'Failed to simulate scenarios');
    }
    
    // Parse response text first to check for valid JSON
    const responseText = await response.text();
    let responseData;
    
    try {
      responseData = JSON.parse(responseText);
    } catch (e) {
      console.error('Invalid JSON response:', responseText);
      throw new Error('Invalid response format from API');
    }
    
    console.log('Response from simulate-revenue endpoint:', JSON.stringify(responseData, null, 2));
    return responseData;
  } catch (error) {
    console.error('Error simulating scenarios:', error);
    // Check for timeout errors
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. The server took too long to respond.');
    }
    throw error;
  }
}

/**
 * Helper function to map frontend order data to the API format
 */
export function mapToApiOrderFormat(frontendData: any) {
  // Get weekday as string (Sunday, Monday, etc.)
  const weekdays = [
    "Sunday", "Monday", "Tuesday", "Wednesday", 
    "Thursday", "Friday", "Saturday"
  ];
  const weekday = weekdays[new Date().getDay()];
  
  // The API expects specific field names
  return {
    "Location": frontendData.locationId || "North", // Use the location directly from dropdown
    "_ProductID": parseInt(frontendData.productId) || 1, // Use numeric ID value
    "Unit Cost": parseFloat(frontendData.unitCost) || 0,
    "Unit Price": parseFloat(frontendData.unitPrice) || 0,
    "Month": new Date().getMonth() + 1, // Current month
    "Day": new Date().getDate(), // Current day
    "Weekday": weekday, // Current weekday as string
    "Year": new Date().getFullYear() // Current year
  };
}

/**
 * Reload API data files
 */
export async function reloadDataFiles() {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/reload`);
    
    if (!response.ok) {
      throw new Error('Failed to reload data files');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error reloading data files:', error);
    throw error;
  }
}

/**
 * Get API information
 */
export async function getApiInfo() {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/api-info`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch API information');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching API information:', error);
    throw error;
  }
}

/**
 * Upload a file to the API
 */
export async function uploadFile(file: File) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/upload-file`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to upload file');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
}

/**
 * Get product price and cost data directly from the data file
 */
export async function getProductData() {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/product-data`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch product data');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching product data:', error);
    throw error;
  }
} 