import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

export async function GET() {
  try {
    // Path to the data directory
    const dataDir = path.join(process.cwd(), 'public', 'data');
    
    // Find CSV files in the directory
    let files;
    try {
      files = (await fs.readdir(dataDir)).filter(file => file.toLowerCase().endsWith('.csv'));
    } catch (err) {
      console.error('Error reading data directory:', err);
      throw new Error('Failed to read data directory');
    }
    
    if (files.length === 0) {
      throw new Error('No CSV files found in data directory');
    }
    
    // Use the first CSV file found
    const filePath = path.join(dataDir, files[0]);
    console.log(`Using data file for product data: ${filePath}`);
    
    // Read the CSV file
    const fileContent = await fs.readFile(filePath, 'utf8');
    
    // Parse CSV
    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    });
    
    // If no records found
    if (!records || records.length === 0) {
      throw new Error('No data records found in CSV file');
    }
    
    // Get product ID column name
    const header = Object.keys(records[0]);
    const productIdColumn = header.find(h => 
      ['_ProductID', 'ProductID', 'Product_ID', 'product_id'].includes(h)
    );
    
    if (!productIdColumn) {
      throw new Error('Product ID column not found in CSV');
    }
    
    // Get price and cost column names
    const priceColumn = header.find(h => 
      ['Unit Price', 'UnitPrice', 'Price', 'unit_price'].includes(h)
    );
    const costColumn = header.find(h => 
      ['Unit Cost', 'UnitCost', 'Cost', 'unit_cost'].includes(h)
    );
    
    if (!priceColumn) {
      throw new Error('Price column not found in CSV');
    }
    if (!costColumn) {
      throw new Error('Cost column not found in CSV');
    }
    
    // Calculate average price and cost for each product
    const productMap = new Map();
    
    for (const record of records) {
      const productId = Number(record[productIdColumn]);
      const price = Number(record[priceColumn]);
      const cost = Number(record[costColumn]);
      
      if (isNaN(productId) || isNaN(price) || isNaN(cost)) {
        continue; // Skip invalid records
      }
      
      if (!productMap.has(productId)) {
        productMap.set(productId, { 
          count: 0, 
          totalPrice: 0, 
          totalCost: 0 
        });
      }
      
      const data = productMap.get(productId);
      data.count++;
      data.totalPrice += price;
      data.totalCost += cost;
    }
    
    // Calculate averages and format results
    const products = Array.from(productMap.entries()).map(([productId, data]) => ({
      productId,
      price: data.totalPrice / data.count,
      cost: data.totalCost / data.count
    }));
    
    // Sort by product ID
    products.sort((a, b) => a.productId - b.productId);
    
    // Return product data
    return NextResponse.json({
      status: 'success',
      source: files[0],
      products
    });
    
  } catch (error: any) {
    console.error('Error in product-data API route:', error);
    
    return NextResponse.json(
      { 
        status: 'error',
        error: error.message || 'Failed to get product data' 
      },
      { status: 500 }
    );
  }
} 