import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export async function GET() {
  try {
    // Define the standard locations that our model expects
    const standardLocations = [
      { id: 'North', name: 'North Region' },
      { id: 'South', name: 'South Region' },
      { id: 'East', name: 'East Region' },
      { id: 'West', name: 'West Region' },
      { id: 'Central', name: 'Central Region' }
    ];
    
    return NextResponse.json(standardLocations);
    
  } catch (error) {
    console.error('Error in locations API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch locations' },
      { status: 500 }
    );
  }
} 