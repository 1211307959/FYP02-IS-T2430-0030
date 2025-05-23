import { NextResponse } from 'next/server';
import { getDashboardData } from '@/lib/api';

export const dynamic = 'force-dynamic'; // Disable static caching of this route

// Define interfaces for our product data
interface ProductData {
  id: number;
  name: string;
  rank?: 'top' | 'bottom';
  profit: number;
  revenue: number;
  [key: string]: any; // For other properties
}

/**
 * Handles GET requests to fetch dashboard data
 */
export async function GET(request: Request) {
  try {
    // Create a simple query string for cache busting
    const timestamp = new Date().getTime();
    const cacheBustQuery = `?_=${timestamp}`;
    
    console.log(`Dashboard API route handling request with cacheBustQuery: ${cacheBustQuery}`);
    
    // Get dashboard data directly from the Flask backend
    const response = await fetch(`http://localhost:5000/dashboard-data${cacheBustQuery}`, {
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Backend API returned error status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Add data validation and consistency checks
    if (data.top_products_data && Array.isArray(data.top_products_data)) {
      // Find any products that appear in both top and bottom rank
      const productsWithMultipleRanks = data.top_products_data.filter(
        (product: ProductData) => product.rank === 'top'
      ).map((p: ProductData) => p.id).filter(
        (id: number) => data.top_products_data.some((p: ProductData) => p.rank === 'bottom' && p.id === id)
      );
      
      // Log any inconsistencies for debugging
      if (productsWithMultipleRanks.length > 0) {
        console.warn(
          `Data inconsistency warning: Products with multiple ranks detected: ${productsWithMultipleRanks.join(', ')}`
        );
        
        // Fix any remaining inconsistencies by prioritizing 'top' rank
        const seenIds = new Set<number>();
        const fixedProductsData: ProductData[] = [];
        
        // First add all top-ranked products
        for (const product of data.top_products_data) {
          if (product.rank === 'top' && !seenIds.has(product.id)) {
            seenIds.add(product.id);
            fixedProductsData.push(product);
          }
        }
        
        // Then add bottom-ranked products that aren't already included
        for (const product of data.top_products_data) {
          if (product.rank === 'bottom' && !seenIds.has(product.id)) {
            seenIds.add(product.id);
            fixedProductsData.push(product);
          }
        }
        
        // Replace the original data with fixed data
        data.top_products_data = fixedProductsData;
        
        console.log(
          `Fixed data inconsistencies. New product count: ${fixedProductsData.length}`
        );
      }
    }
    
    // Create a response with no-cache headers
    const nextResponse = NextResponse.json(data);
    
    // Set cache control headers to prevent browser caching
    nextResponse.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
    nextResponse.headers.set('Pragma', 'no-cache');
    nextResponse.headers.set('Expires', '0');
    
    return nextResponse;
  } catch (error: any) {
    console.error('Error fetching dashboard data:', error);
    
    return NextResponse.json(
      { 
        status: 'error',
        error: error.message || 'Failed to fetch dashboard data' 
      },
      { status: 500 }
    );
  }
} 