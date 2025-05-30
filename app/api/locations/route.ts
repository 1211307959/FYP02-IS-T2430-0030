import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Define base URL for the Flask API
    const apiUrl = process.env.FLASK_API_URL || 'http://localhost:5000';
    
    // Path to the data directory
    const dataDir = path.join(process.cwd(), 'public', 'data');
    
    try {
      // Check if directory exists
      await fs.access(dataDir);
      
      // Find CSV files in the directory
      const files = (await fs.readdir(dataDir)).filter(file => file.toLowerCase().endsWith('.csv'));
      
      if (files.length === 0) {
        throw new Error('No CSV files found in data directory');
      }
      
      // Use the first CSV file found
      const filePath = path.join(dataDir, files[0]);
      console.log(`Using data file for locations: ${filePath}`);
      
      // Read the CSV file
      const fileContent = await fs.readFile(filePath, 'utf8');
      
      // Split the content into lines
      const lines = fileContent.split('\n');
      
      // Extract unique locations from the Location column
      const locationSet = new Set<string>();
      
      // Try to find the location column
      const header = lines[0].split(',');
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
        throw new Error('Location column not found in CSV header');
      }
      
      // Skip header line
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line) {
          const columns = line.split(',');
          if (columns.length > locationColumnIndex) {
            const location = columns[locationColumnIndex].trim();
            if (location) {
              locationSet.add(location);
            }
          }
        }
      }
      
      // Convert to array and sort alphabetically
      const sortedLocations = Array.from(locationSet).sort();
      
      // Format for the frontend, adding an "All Locations" option at the top
      const locations = [
        { id: 'All', name: 'All Locations' },
        ...sortedLocations.map((location: string) => ({
          id: location,
          name: location
        }))
      ];
      
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
          return NextResponse.json(locations);
        } else {
          throw new Error('Invalid API response format');
        }
      } catch (apiError: unknown) {
        console.warn(`Failed to fetch API locations: ${apiError instanceof Error ? apiError.message : 'Unknown error'}`);
        
        // Return a minimal fallback list of locations if all else fails
        const fallbackLocations = [
          { id: 'All', name: 'All Locations' },
          { id: 'North', name: 'North' },
          { id: 'South', name: 'South' },
          { id: 'East', name: 'East' },
          { id: 'West', name: 'West' },
          { id: 'Central', name: 'Central' }
        ];
        
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