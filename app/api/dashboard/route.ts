import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic'; // Disable static caching of this route

/**
 * Handles GET requests to fetch dashboard data
 * This endpoint redirects to /api/dashboard-data for compatibility
 */
export async function GET(request: Request) {
  try {
    // Extract any query parameters from the request URL
    const url = new URL(request.url);
    const queryString = url.search || '';
    
    // Create the redirect URL
    const redirectUrl = `/api/dashboard-data${queryString}`;
    
    // Log the redirection
    console.log(`Redirecting from /api/dashboard to ${redirectUrl}`);
    
    // Return a redirect response
    return NextResponse.redirect(new URL(redirectUrl, request.url));
  } catch (error: any) {
    console.error('Error redirecting dashboard request:', error);
    
    return NextResponse.json(
      { 
        status: 'error',
        error: error.message || 'Failed to redirect dashboard request' 
      },
      { status: 500 }
    );
  }
} 