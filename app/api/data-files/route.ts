import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Path to the data directory
    const dataDir = path.join(process.cwd(), 'public', 'data');
    
    try {
      // Check if directory exists
      await fs.access(dataDir);
      
      // Find CSV files in the directory
      const files = (await fs.readdir(dataDir)).filter(file => file.toLowerCase().endsWith('.csv'));
      
      if (files.length === 0) {
        return NextResponse.json({
          status: 'success',
          message: 'No CSV files found in data directory',
          files: []
        });
      }
      
      // Return the list of CSV files
      return NextResponse.json({
        status: 'success',
        message: `Found ${files.length} CSV files`,
        files
      });
      
    } catch (error) {
      console.error('Error reading data directory:', error);
      
      return NextResponse.json({
        status: 'error',
        message: 'Error reading data directory',
        files: []
      }, { status: 500 });
    }
    
  } catch (error) {
    console.error('Error in data-files API route:', error);
    
    return NextResponse.json({
      status: 'error',
      message: 'Failed to fetch data files',
      files: []
    }, { status: 500 });
  }
} 