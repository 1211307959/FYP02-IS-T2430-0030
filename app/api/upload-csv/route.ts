import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { Readable } from 'stream';

// Function to ensure the data directory exists
function ensureDataDirExists() {
  const dataDir = path.join(process.cwd(), 'data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
  return dataDir;
}

// Helper function to read the request stream
async function streamToBuffer(stream: ReadableStream<Uint8Array>): Promise<Buffer> {
  const reader = stream.getReader();
  const chunks: Uint8Array[] = [];
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  
  return Buffer.concat(chunks);
}

export async function POST(request: NextRequest) {
  try {
    // Ensure formData is supported
    if (!request.body) {
      return NextResponse.json(
        { error: 'Request body is empty' },
        { status: 400 }
      );
    }
    
    // Use the new FormData API
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json(
        { error: 'No file found in the request' },
        { status: 400 }
      );
    }
    
    // Check if the file is a CSV
    if (!file.name.toLowerCase().endsWith('.csv')) {
      return NextResponse.json(
        { error: 'Only CSV files are allowed' },
        { status: 400 }
      );
    }
    
    // Create the data directory if it doesn't exist
    const dataDir = ensureDataDirExists();
    
    // Get the file data as a Buffer
    const fileBuffer = Buffer.from(await file.arrayBuffer());
    
    // Create a safe filename (avoid overwriting the default file)
    let filename = file.name;
    if (filename === 'Adjusted_Sales_Data_With_Time_Features.csv') {
      // Add a timestamp to avoid overwriting the default file
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      filename = `Adjusted_Sales_Data_With_Time_Features_${timestamp}.csv`;
    }
    
    // Save the file to the data directory
    const filePath = path.join(dataDir, filename);
    fs.writeFileSync(filePath, fileBuffer);
    
    // Copy to public/data as well for frontend access
    const publicDataDir = path.join(process.cwd(), 'public', 'data');
    if (!fs.existsSync(publicDataDir)) {
      fs.mkdirSync(publicDataDir, { recursive: true });
    }
    fs.writeFileSync(path.join(publicDataDir, filename), fileBuffer);
    
    return NextResponse.json({
      success: true,
      filename,
      message: `File uploaded successfully to data directory: ${filename}`
    });
  } catch (error) {
    console.error('Error uploading file:', error);
    return NextResponse.json(
      { error: 'Error uploading file: ' + (error instanceof Error ? error.message : 'Unknown error') },
      { status: 500 }
    );
  }
} 