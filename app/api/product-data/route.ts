import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { promisify } from 'util';
import { parse } from 'csv-parse/sync';

const readFile = promisify(fs.readFile);

export async function GET() {
  try {
    // Get the data directory path
    const dataDir = path.join(process.cwd(), 'public', 'data');
    
    // Check if directory exists
    if (!fs.existsSync(dataDir)) {
      return NextResponse.json(
        { error: 'Data directory not found' },
        { status: 404 }
      );
    }
    
    // Find CSV files in the directory
    const files = fs.readdirSync(dataDir).filter(file => file.toLowerCase().endsWith('.csv'));
    
    if (files.length === 0) {
      return NextResponse.json(
        { error: 'No CSV files found in data directory' },
        { status: 404 }
      );
    }
    
    // Use the first CSV file found
    const dataFilePath = path.join(dataDir, files[0]);
    console.log(`Using data file: ${dataFilePath}`);
    
    // Read the file content
    const fileContent = await readFile(dataFilePath, 'utf8');
    
    // Parse CSV content
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    // Create a map to store product data
    const productMap = new Map();
    
    // Process records to extract product data
    records.forEach(record => {
      // Try to get ProductID from different possible column names
      const productId = parseInt(record['_ProductID'] || record['ProductID'] || record['Product_ID'] || record['product_id'] || '0');
      const unitPrice = parseFloat(record['Unit Price'] || record['UnitPrice'] || record['Price'] || record['unit_price'] || '0');
      const unitCost = parseFloat(record['Unit Cost'] || record['UnitCost'] || record['Cost'] || record['unit_cost'] || '0');
      
      if (!isNaN(productId) && !isNaN(unitPrice) && !isNaN(unitCost)) {
        // Store data by product ID (not in PROD format)
        if (!productMap.has(productId)) {
          productMap.set(productId, {
            count: 1,
            totalPrice: unitPrice,
            totalCost: unitCost
          });
        } else {
          const current = productMap.get(productId);
          productMap.set(productId, {
            count: current.count + 1,
            totalPrice: current.totalPrice + unitPrice,
            totalCost: current.totalCost + unitCost
          });
        }
      }
    });
    
    // Calculate averages and format the response
    const productData = Array.from(productMap.entries()).map(([id, data]) => ({
      productId: id, // Keep as number
      price: data.totalPrice / data.count,
      cost: data.totalCost / data.count
    }));
    
    // Return product data as JSON
    return NextResponse.json({
      message: 'Product data loaded from file',
      source: files[0],
      lastUpdated: new Date().toISOString(),
      products: productData
    });
    
  } catch (error) {
    console.error('Error fetching product data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch product data' },
      { status: 500 }
    );
  }
} 