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

// Add this near the top of the file
let cachedProducts: any[] | null = null;
let cachedLocations: any[] | null = null;
let cachedProductData: any | null = null;
let lastCacheTime = 0;

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
    // First try to get the list of available CSV files
    let csvFileName = null;
    
    try {
      // Try to get available data files first
      const dataFiles = await getDataFiles();
      if (dataFiles && dataFiles.files && dataFiles.files.length > 0) {
        csvFileName = dataFiles.files[0];
      }
    } catch (error) {
      console.warn('Could not fetch data files list, will try with default approach');
    }
    
    // If we couldn't get a file from the API, try with a direct request to the data directory
    if (!csvFileName) {
      try {
        const response = await fetch('/api/data-files');
        if (response.ok) {
          const data = await response.json();
          if (data && data.files && data.files.length > 0) {
            csvFileName = data.files[0];
          }
        }
      } catch (e) {
        console.warn('Could not get file list from API, will use default fetch approach');
      }
    }
    
    // If we still don't have a filename, just try to fetch any CSV file
    const fileUrl = csvFileName 
      ? `/data/${csvFileName}` 
      : '/data/sample.csv'; // Fallback to a generic name
    
    const response = await fetch(fileUrl);
    
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
  // Use cached data if available and less than 1 minute old
  const now = Date.now();
  if (cachedLocations && (now - lastCacheTime < 60000)) {
    console.log("Using cached location data");
    return cachedLocations;
  }

  try {
    const response = await fetch('/api/locations');
    if (!response.ok) {
      throw new Error(`Failed to fetch locations: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Update cache
    cachedLocations = data;
    lastCacheTime = now;
    
    return data;
  } catch (error) {
    console.error('Error fetching locations:', error);
    return [];
  }
}

/**
 * Fetches products from the API
 */
export async function getProducts() {
  // Use cached data if available and less than 1 minute old
  const now = Date.now();
  if (cachedProducts && (now - lastCacheTime < 60000)) {
    console.log("Using cached product data");
    return cachedProducts;
  }

  try {
    const response = await fetch('/api/products');
    if (!response.ok) {
      throw new Error(`Failed to fetch products: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Raw product data:", data);
    
    // Transform product data to ensure consistent format
    const transformedProducts = data.map((product: any) => {
      // Handle different response formats
      if (typeof product === 'object' && product !== null) {
        // Already an object, just ensure it has the right properties
        return {
          id: String(product.id || product.productId || ''),
          name: product.name || `Product ${product.id || product.productId || ''}`
        };
      } else {
        // It's a primitive (likely a number), create an object
        return {
          id: String(product),
          name: `Product ${product}`
        };
      }
    });
    
    console.log("Transformed products:", transformedProducts);
    
    // Update cache
    cachedProducts = transformedProducts;
    lastCacheTime = now;
    
    return transformedProducts;
  } catch (error) {
    console.error("Error fetching products:", error);
    // Return empty array on error
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
  // Use cached data if available and less than 1 minute old
  const now = Date.now();
  if (cachedProductData && (now - lastCacheTime < 60000)) {
    console.log("Using cached product price/cost data");
    return cachedProductData;
  }

  try {
    const response = await fetch('/api/product-data');
    if (!response.ok) {
      throw new Error(`Failed to fetch product data: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Update cache
    cachedProductData = data;
    lastCacheTime = now;
    
    return data;
  } catch (error) {
    console.error('Error fetching product data:', error);
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
export async function simulateScenarios(data: any) {
  console.log('simulateScenarios called with:', data);
  
  try {
    // Ensure Location is capitalized for API
    const formattedData = {
      ...data,
      _timestamp: Date.now() // Add timestamp to avoid caching
    };

    // Direct URL to the simulate-revenue endpoint
    const response = await fetch('/api/simulate-revenue', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formattedData),
    });

    if (!response.ok) {
      console.error(`Simulate scenarios API error: ${response.status} ${response.statusText}`);
      const errorText = await response.text();
      console.error('Error response:', errorText);
      throw new Error(`Failed to simulate scenarios: ${response.status} ${response.statusText}`);
    }

    const jsonResponse = await response.json();
    console.log('simulateScenarios API response:', JSON.stringify(jsonResponse, null, 2));
    
    // Verify the structure of the response
    if (!jsonResponse) {
      console.error('Simulation API returned null or undefined');
      throw new Error('Simulation failed - empty response');
    }
    
    // Check if we have variations
    if (jsonResponse.variations && Array.isArray(jsonResponse.variations)) {
      console.log(`Found ${jsonResponse.variations.length} variations in the response`);
    } else if (Array.isArray(jsonResponse)) {
      console.log(`Response is an array with ${jsonResponse.length} items`);
    } else {
      console.warn('Response has no variations array and is not an array itself');
    }
    
    return jsonResponse;
  } catch (error) {
    console.error('Error in simulateScenarios:', error);
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

// Sales Forecast API Functions

export async function fetchForecastSales(
  productId: string | number,
  location: string,
  unitPrice: number,
  unitCost: number,
  startDate: string,
  endDate: string,
  frequency: 'D' | 'W' | 'M' = 'D',
  includeConfidence: boolean = true
) {
  try {
    const response = await fetch('/api/forecast-sales', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        product_id: productId,
        location,
        unit_price: unitPrice,
        unit_cost: unitCost,
        start_date: startDate,
        end_date: endDate,
        frequency,
        include_confidence: includeConfidence,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching sales forecast:', error);
    throw error;
  }
}

export async function fetchMultipleForecast(
  products: Array<{
    product_id: string | number;
    location: string;
    unit_price: number;
    unit_cost: number;
  }>,
  startDate: string,
  endDate: string,
  frequency: 'D' | 'W' | 'M' = 'D'
) {
  try {
    const response = await fetch('/api/forecast-multiple', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        products,
        start_date: startDate,
        end_date: endDate,
        frequency,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching multiple forecast:', error);
    throw error;
  }
}

export async function fetchProductTrend(
  productId: string | number,
  location: string,
  basePrice: number,
  unitCost: number,
  startDate: string,
  endDate: string,
  priceVariations: number[] = [0.8, 0.9, 1.0, 1.1, 1.2],
  frequency: 'D' | 'W' | 'M' = 'D'
) {
  try {
    const response = await fetch('/api/forecast-trend', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        product_id: productId,
        location,
        base_price: basePrice,
        unit_cost: unitCost,
        price_variations: priceVariations,
        start_date: startDate,
        end_date: endDate,
        frequency,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching product trend:', error);
    throw error;
  }
}

// Helper Functions

export function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function getDefaultDateRange(days: number = 30): { startDate: string; endDate: string } {
  const today = new Date();
  
  // Start date: today
  const startDate = formatDate(today);
  
  // End date: specified days from today
  const endDate = new Date(today);
  endDate.setDate(today.getDate() + days);
  
  return {
    startDate,
    endDate: formatDate(endDate),
  };
}

/**
 * Helper function to get file information without revealing full paths in logs
 * Returns just the filename, not the full path
 */
export function getApiFileInfo(filePath: string): string {
  if (!filePath) return 'unknown';
  
  // Extract just the filename from the path
  const parts = filePath.split(/[/\\]/);
  return parts[parts.length - 1];
}

// Clear cache function to use when data file changes
export function clearDataCache() {
  cachedProducts = null;
  cachedLocations = null;
  cachedProductData = null;
  console.log("Data cache cleared");
} 