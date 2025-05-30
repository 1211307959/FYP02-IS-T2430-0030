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
 * This function is deprecated as the system now uses all data files combined
 * Kept for backward compatibility but will trigger a reload of combined data
 */
export async function selectDataFile(filename: string) {
  try {
    // Instead of selecting a specific file, we'll just reload all files
    const result = await reloadDataFiles();
    
    // Dispatch a global event to notify components that the data has changed
    window.dispatchEvent(new CustomEvent('dataFileChanged', { 
      detail: { message: 'Using combined data from all files', timestamp: new Date().toISOString() } 
    }));
    
    return result;
  } catch (error) {
    console.error('Error reloading data files:', error);
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
 * Fetches locations from the API
 */
export async function getLocations() {
  try {
    const response = await fetch('/api/locations');
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch locations:', error);
    return [];
  }
}

/**
 * Fetches products from the API
 */
export async function getProducts() {
  try {
    const response = await fetch('/api/products');
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch products:', error);
    return [];
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
 * Fetches product price and cost data from the API
 */
export async function getProductData() {
  try {
    const response = await fetch('/api/product-data');
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch product data:', error);
    return { products: [] };
  }
}

/**
 * Maps the frontend order data to the format expected by the API
 */
export function mapToApiOrderFormat(data) {
  // Create a new object to avoid mutating the input
  const apiData = {};
  
  // Handle product ID - convert to numeric format expected by backend
  if (data.productId) {
    apiData._ProductID = parseInt(String(data.productId), 10);
  }
  
  // Handle Location/locationId
  if (data.locationId) {
    apiData.Location = data.locationId;
  }
  
  // Handle unit price
  if (data.unitPrice !== undefined) {
    apiData['Unit Price'] = parseFloat(String(data.unitPrice));
  }
  
  // Handle unit cost
  if (data.unitCost !== undefined) {
    apiData['Unit Cost'] = parseFloat(String(data.unitCost));
  }
  
  // Handle any other fields that might be present
  if (data.Month) apiData.Month = parseInt(String(data.Month), 10);
  if (data.Day) apiData.Day = parseInt(String(data.Day), 10);
  if (data.Year) apiData.Year = parseInt(String(data.Year), 10);
  if (data.Weekday) apiData.Weekday = data.Weekday;
  
  // Add weekday if not present
  if (!apiData.Weekday) {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    apiData.Weekday = days[new Date().getDay()];
  }
  
  // Debug log the mapping
  console.log('Frontend data:', data);
  console.log('Mapped to API format:', apiData);
  
  return apiData;
}

/**
 * Simulates revenue scenarios with different price points
 */
export async function simulateScenarios(data) {
  try {
    // Add timestamp to prevent browser caching
    const timestamp = new Date().getTime();
    data._timestamp = timestamp;
    
    // Convert data to the format expected by the API
    const apiData = typeof data.locationId !== 'undefined' ? mapToApiOrderFormat(data) : data;
    
    // Log request being sent
    console.log('Simulating revenue with data:', apiData);
    
    // Make sure required fields have values (not null or undefined)
    if (apiData._ProductID === null || apiData._ProductID === undefined) {
      apiData._ProductID = 1; // Default product ID
    }
    
    if (apiData['Unit Price'] === null || apiData['Unit Price'] === undefined || isNaN(apiData['Unit Price'])) {
      apiData['Unit Price'] = 100.0; // Default price
    }
    
    if (apiData['Unit Cost'] === null || apiData['Unit Cost'] === undefined || isNaN(apiData['Unit Cost'])) {
      apiData['Unit Cost'] = 50.0; // Default cost
    }
    
    // Ensure values are proper types
    apiData._ProductID = parseInt(String(apiData._ProductID), 10);
    apiData['Unit Price'] = parseFloat(String(apiData['Unit Price']));
    apiData['Unit Cost'] = parseFloat(String(apiData['Unit Cost']));
    
    // Ensure Location is present
    if (!apiData.Location) {
      apiData.Location = 'Central'; // Default location
    }
    
    const response = await fetch('/api/simulate-revenue', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache'
      },
      body: JSON.stringify(apiData),
      cache: 'no-store'
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.error || `API error: ${response.status}`
      );
    }
    
    const result = await response.json();
    
    // Log response for debugging
    console.log('Simulation response:', result);
    
    return result;
  } catch (error) {
    console.error('Failed to simulate scenarios:', error);
    throw error;
  }
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