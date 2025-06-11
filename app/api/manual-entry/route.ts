import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Function to ensure the data directory exists
function ensureDataDirExists() {
  const dataDir = path.join(process.cwd(), 'public', 'data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
  return dataDir;
}

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    
    // Validate required fields
    const requiredFields = ['location', '_ProductID', 'unit_cost', 'unit_price', 'total_revenue', 'year', 'month', 'day', 'weekday'];
    for (const field of requiredFields) {
      if (data[field] === undefined || data[field] === null) {
        return NextResponse.json(
          { error: `Missing required field: ${field}` },
          { status: 400 }
        );
      }
    }
    
    // Create the data directory if it doesn't exist
    const dataDir = ensureDataDirExists();
    
    // Create filename with timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `manual_entry_${timestamp}.csv`;
    const filePath = path.join(dataDir, filename);
    
    // CSV header
    const header = 'Location,_ProductID,Unit Cost,Unit Price,Total Revenue,Year,Month,Day,Weekday\n';
    
    // Format the data row
    const row = `${data.location},${data._ProductID},${data.unit_cost},${data.unit_price},${data.total_revenue},${data.year},${data.month},${data.day},${data.weekday}\n`;
    
    // Write the CSV file
    fs.writeFileSync(filePath, header + row);
    
    return NextResponse.json({
      success: true,
      filename,
      message: `Manual entry saved successfully: ${filename}`,
      data: data
    });
  } catch (error) {
    console.error('Error saving manual entry:', error);
    return NextResponse.json(
      { error: 'Error saving manual entry: ' + (error instanceof Error ? error.message : 'Unknown error') },
      { status: 500 }
    );
  }
} 