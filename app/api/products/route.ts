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
      console.log(`Using data file for products: ${filePath}`);
      
      // Read the CSV file
      const fileContent = await fs.readFile(filePath, 'utf8');
      
      // Split the content into lines
      const lines = fileContent.split('\n');
      
      // Extract unique product IDs from the _ProductID column
      const productIds = new Set();
      
      // Try to find the product ID column
      const header = lines[0].split(',');
      const possibleProductColumns = ['_ProductID', 'ProductID', 'Product_ID', 'product_id'];
      let productIdColumnIndex = -1;
      
      for (const colName of possibleProductColumns) {
        const index = header.findIndex(h => h.trim() === colName);
        if (index !== -1) {
          productIdColumnIndex = index;
          break;
        }
      }
      
      if (productIdColumnIndex === -1) {
        throw new Error('Product ID column not found in CSV header');
      }
      
      // Skip header line
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line) {
          const columns = line.split(',');
          if (columns.length > productIdColumnIndex) {
            const productId = columns[productIdColumnIndex];
            if (productId) {
              productIds.add(productId);
            }
          }
        }
      }
      
      // Convert to array and sort numerically
      const sortedProductIds = Array.from(productIds)
        .map(id => parseInt(id, 10))
        .filter(id => !isNaN(id))
        .sort((a, b) => a - b);
      
      // Format for the frontend - use numeric IDs directly
      const products = sortedProductIds.map(id => ({
        id: id.toString(), // Use numeric ID as string
        name: `Product ${id}` // Use a friendly name format
      }));
      
      return NextResponse.json(products);
      
    } catch (error) {
      console.error('Error reading CSV file:', error);
      
      // Fallback to model API
      const response = await fetch(`${apiUrl}/products`);
      
      if (!response.ok) {
        // If API fails too, return fallback list
        console.warn(`Failed to fetch API products: ${response.statusText}`);
        
        // Return a fallback list of products with numeric IDs
        const fallbackProducts = Array.from({ length: 20 }, (_, i) => ({
          id: (i + 1).toString(), // Use numeric ID as string
          name: `Product ${i + 1}` // Use a friendly name format
        }));
        
        return NextResponse.json(fallbackProducts);
      }
      
      // Return products from API
      const apiProducts = await response.json();
      const products = Array.isArray(apiProducts.products) ? apiProducts.products : apiProducts;
      
      return NextResponse.json(products);
    }
    
  } catch (error) {
    console.error('Error in products API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch products' },
      { status: 500 }
    );
  }
} 