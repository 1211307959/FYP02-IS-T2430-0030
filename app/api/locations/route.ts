import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

// In-memory cache for responses to avoid duplicate processing during development
let responseCache: {
  data: any;
  timestamp: number;
} | null = null;

// Cache validity period (5 minutes)
const CACHE_TTL = 5 * 60 * 1000;

export async function GET() {
  try {
    // Check if we have a valid cached response
    const now = Date.now();
    if (responseCache && now - responseCache.timestamp < CACHE_TTL) {
      return NextResponse.json(responseCache.data);
    }

    // Define base URL for the Flask API
    const apiUrl = process.env.FLASK_API_URL || 'http://localhost:5000';
    
    // Path to the data directory - updated to use root data folder
    const dataDir = path.join(process.cwd(), 'public', 'data');
    
    try {
      // Check if directory exists
      await fs.access(dataDir);
      
      // Find CSV files in the directory
      const files = (await fs.readdir(dataDir)).filter(file => file.toLowerCase().endsWith('.csv'));
      
      if (files.length === 0) {
        throw new Error('No CSV files found in data directory');
      }
      
      console.log(`Processing ${files.length} CSV files for locations`);
      
      // Collect all unique locations from all CSV files
      const allLocations = new Set<string>();
      
      for (const fileName of files) {
      const filePath = path.join(dataDir, fileName);
        
        try {
      // Read the CSV file
      const fileContent = await fs.readFile(filePath, 'utf8');
      
      // Split the content into lines
          const lines = fileContent.split('\n').filter(line => line.trim());
          
          if (lines.length === 0) continue;
      
          // Parse header line properly (handle quoted fields)
          const header = parseCSVLine(lines[0]);
      
      // Try to find the location column
      const possibleLocationColumns = ['Location', 'location', 'LOCATION', 'LocationID', 'location_id'];
      let locationColumnIndex = -1;
      
      for (const colName of possibleLocationColumns) {
        const index = header.findIndex(h => h.trim() === colName);
        if (index !== -1) {
          locationColumnIndex = index;
          break;
        }
      }
      
      if (locationColumnIndex === -1) {
            console.warn(`Location column not found in ${fileName}`);
            continue;
      }
      
          // Skip header line and parse data lines
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line) {
              const columns = parseCSVLine(line);
          if (columns.length > locationColumnIndex) {
            const location = columns[locationColumnIndex].trim();
                if (location && location !== '') {
                  allLocations.add(location);
            }
          }
            }
          }
        } catch (error) {
          console.error(`Error processing file ${fileName}:`, error);
        }
      }
      
      // Convert to array and sort alphabetically
      const sortedLocations = Array.from(allLocations).sort();
      
      console.log(`Found ${sortedLocations.length} unique locations: ${sortedLocations.join(', ')}`);
      
      // Format for the frontend, adding an "All Locations" option at the top
      const locations = [
        { id: 'All', name: 'All Locations' },
        ...sortedLocations.map((location: string) => ({
          id: location,
          name: location
        }))
      ];
      
      // Cache the response
      responseCache = {
        data: locations,
        timestamp: now
      };
      
      return NextResponse.json(locations);
      
    } catch (error) {
      console.error('Error reading CSV file:', error);
      
      // Fallback to model API
      try {
        const response = await fetch(`${apiUrl}/locations`);
        
        if (!response.ok) {
          throw new Error(`API returned status ${response.status}`);
        }
        
        // Process API response
        const apiData = await response.json();
        
        // Check if the response has a locations property
        if (Array.isArray(apiData.locations)) {
          const locations = [
            { id: 'All', name: 'All Locations' },
            ...apiData.locations.map((location: string) => ({
              id: location,
              name: location
            }))
          ];
          
          // Cache the response
          responseCache = {
            data: locations,
            timestamp: now
          };
          
          return NextResponse.json(locations);
        } else {
          throw new Error('Invalid API response format');
        }
      } catch (apiError: unknown) {
        console.warn(`Failed to fetch API locations: ${apiError instanceof Error ? apiError.message : 'Unknown error'}`);
        
        // Return a complete fallback list based on known data
        const fallbackLocations = [
          { id: 'All', name: 'All Locations' },
          { id: 'Central', name: 'Central' },
          { id: 'East', name: 'East' },
          { id: 'North', name: 'North' },
          { id: 'South', name: 'South' },
          { id: 'West', name: 'West' }
        ];
        
        // Cache the fallback response
        responseCache = {
          data: fallbackLocations,
          timestamp: now
        };
        
        return NextResponse.json(fallbackLocations);
      }
    }
    
  } catch (error) {
    console.error('Error in locations API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch locations' },
      { status: 500 }
    );
  }
}

// Helper function to properly parse CSV lines (handles quoted fields)
function parseCSVLine(line: string): string[] {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  
  // Add the last field
  result.push(current);
  
  return result;
} 