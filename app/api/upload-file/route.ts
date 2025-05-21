import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Create a route handler for upload-file
export async function POST(request: NextRequest) {
  try {
    // Get the file from the request
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json(
        { error: 'No file found in the request' },
        { status: 400 }
      );
    }
    
    // Check if file is a CSV
    if (!file.name.toLowerCase().endsWith('.csv')) {
      return NextResponse.json(
        { error: 'Only CSV files are allowed' },
        { status: 400 }
      );
    }
    
    // Save the file to a temporary location
    const dataDir = path.join(process.cwd(), 'data');
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }
    
    const filePath = path.join(dataDir, file.name);
    const fileBuffer = Buffer.from(await file.arrayBuffer());
    fs.writeFileSync(filePath, fileBuffer);
    
    // Forward to both endpoints - our existing upload-csv endpoint and also trigger a reload in the backend
    // First, upload to our Next.js endpoint
    const uploadFormData = new FormData();
    uploadFormData.append('file', new File([fileBuffer], file.name, { type: file.type }));
    
    try {
      await fetch('/api/upload-csv', {
        method: 'POST',
        body: uploadFormData
      });
    } catch (error) {
      console.error('Error uploading to internal endpoint:', error);
      // Continue even if this fails, as we'll try the Flask endpoint
    }
    
    // Now manually reload the data files in the backend
    try {
      await fetch('/api/reload');
    } catch (error) {
      console.error('Error reloading data files:', error);
      // Continue even if this fails
    }
    
    return NextResponse.json({
      success: true,
      filename: file.name,
      message: `File uploaded successfully: ${file.name}`
    });
  } catch (error) {
    console.error('Error in upload-file route:', error);
    return NextResponse.json(
      { error: 'Error uploading file: ' + (error instanceof Error ? error.message : 'Unknown error') },
      { status: 500 }
    );
  }
} 