// Test script for Next.js API routes
import fetch from 'node-fetch';

// Configuration
const NEXTJS_BASE_URL = 'http://localhost:3000/api';
const TEST_TIMEOUT = 10000; // 10 seconds

// Helper function for colorful console output
const print = {
  success: (message) => console.log(`\x1b[32m✓ ${message}\x1b[0m`),
  warning: (message) => console.log(`\x1b[33m⚠ ${message}\x1b[0m`),
  error: (message) => console.log(`\x1b[31m✗ ${message}\x1b[0m`),
  info: (message) => console.log(`\x1b[36mi ${message}\x1b[0m`),
  section: (title) => {
    console.log('\n' + '='.repeat(80));
    console.log(' ' + title.toUpperCase() + ' '.repeat(78 - title.length) + ' ');
    console.log('='.repeat(80) + '\n');
  }
};

// Test health endpoint
async function testHealth() {
  print.info('Testing health endpoint...');
  try {
    const response = await fetch(`${NEXTJS_BASE_URL}/health`);
    const data = await response.json();
    
    if (response.ok && data.status === 'healthy') {
      print.success('Health endpoint working properly');
      return true;
    } else {
      print.error(`Health endpoint returned unexpected status: ${data.status}`);
      return false;
    }
  } catch (error) {
    print.error(`Error testing health endpoint: ${error.message}`);
    return false;
  }
}

// Test locations endpoint
async function testLocations() {
  print.info('Testing locations endpoint...');
  try {
    const response = await fetch(`${NEXTJS_BASE_URL}/locations`);
    const data = await response.json();
    
    if (response.ok && Array.isArray(data.locations) && data.locations.length > 0) {
      print.success(`Locations endpoint returned ${data.locations.length} locations`);
      print.info(`Sample locations: ${data.locations.slice(0, 3).join(', ')}${data.locations.length > 3 ? '...' : ''}`);
      return true;
    } else {
      print.error('Locations endpoint failed or returned no locations');
      return false;
    }
  } catch (error) {
    print.error(`Error testing locations endpoint: ${error.message}`);
    return false;
  }
}

// Test products endpoint
async function testProducts() {
  print.info('Testing products endpoint...');
  try {
    const response = await fetch(`${NEXTJS_BASE_URL}/products`);
    const data = await response.json();
    
    if (response.ok && Array.isArray(data.products) && data.products.length > 0) {
      print.success(`Products endpoint returned ${data.products.length} products`);
      print.info(`Sample products: ${data.products.slice(0, 3).join(', ')}${data.products.length > 3 ? '...' : ''}`);
      return true;
    } else {
      print.error('Products endpoint failed or returned no products');
      return false;
    }
  } catch (error) {
    print.error(`Error testing products endpoint: ${error.message}`);
    return false;
  }
}

// Test simulate-revenue endpoint with regular case
async function testSimulateRevenue() {
  print.info('Testing simulate-revenue endpoint with normal parameters...');
  try {
    const testData = {
      productId: 1,
      unitPrice: 100,
      unitCost: 50,
      Location: 'Central',
      Month: 6,
      Day: 15,
      Weekday: 'Friday',
      Year: 2023
    };
    
    const response = await fetch(`${NEXTJS_BASE_URL}/simulate-revenue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testData)
    });
    
    const data = await response.json();
    
    if (response.ok && data.status === 'success' && Array.isArray(data.simulations) && data.simulations.length > 0) {
      print.success(`Simulate revenue endpoint returned ${data.simulations.length} price simulations`);
      
      // Check proper price elasticity
      const lowestPrice = Math.min(...data.simulations.map(s => s['Unit Price'] || 0));
      const highestPrice = Math.max(...data.simulations.map(s => s['Unit Price'] || 0));
      
      const lowestPriceSim = data.simulations.find(s => s['Unit Price'] === lowestPrice);
      const highestPriceSim = data.simulations.find(s => s['Unit Price'] === highestPrice);
      
      const lowestPriceQuantity = lowestPriceSim ? (lowestPriceSim['Predicted Quantity'] || lowestPriceSim.quantity || 0) : 0;
      const highestPriceQuantity = highestPriceSim ? (highestPriceSim['Predicted Quantity'] || highestPriceSim.quantity || 0) : 0;
      
      if (lowestPriceQuantity > highestPriceQuantity) {
        print.success('Price elasticity check passed: Lower price has higher quantity');
      } else {
        print.warning('Price elasticity check failed: Lower price does not have higher quantity');
      }
      
      return true;
    } else {
      print.error('Simulate revenue endpoint failed or returned invalid data');
      console.log(data);
      return false;
    }
  } catch (error) {
    print.error(`Error testing simulate revenue endpoint: ${error.message}`);
    return false;
  }
}

// Test simulate-revenue endpoint with "All Locations"
async function testSimulateRevenueAllLocations() {
  print.info('Testing simulate-revenue endpoint with "All Locations"...');
  try {
    const testData = {
      productId: 1,
      unitPrice: 100,
      unitCost: 50,
      Location: 'All',
      Month: 6,
      Day: 15,
      Weekday: 'Friday',
      Year: 2023
    };
    
    const response = await fetch(`${NEXTJS_BASE_URL}/simulate-revenue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testData)
    });
    
    const data = await response.json();
    
    if (response.ok && data.status === 'success' && Array.isArray(data.simulations) && data.simulations.length > 0) {
      print.success(`All Locations simulation returned ${data.simulations.length} price simulations`);
      
      // Check if note about default location is present
      if (data.note && data.note.toLowerCase().includes('default location')) {
        print.success('All Locations note is present: ' + data.note);
        return true;
      } else {
        print.warning('All Locations note is missing or does not mention default location');
        console.log('Note: ', data.note);
        return false;
      }
    } else {
      print.error('All Locations simulation failed or returned invalid data');
      console.log(data);
      return false;
    }
  } catch (error) {
    print.error(`Error testing All Locations simulation: ${error.message}`);
    return false;
  }
}

// Test extreme price values
async function testExtremePrice() {
  print.info('Testing simulate-revenue endpoint with extreme price...');
  try {
    const testData = {
      productId: 1,
      unitPrice: 99999,
      unitCost: 50,
      Location: 'Central',
      Month: 6,
      Day: 15,
      Weekday: 'Friday',
      Year: 2023
    };
    
    const response = await fetch(`${NEXTJS_BASE_URL}/simulate-revenue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testData)
    });
    
    const data = await response.json();
    
    if (response.ok && data.status === 'success' && Array.isArray(data.simulations)) {
      print.success(`Extreme price simulation returned ${data.simulations.length} price simulations`);
      
      // Check if extremely high prices result in zero quantity
      const highPriceSims = data.simulations.filter(s => s['Unit Price'] > 10000);
      
      if (highPriceSims.length === 0) {
        print.info('No extremely high price simulations were returned');
        return true;
      }
      
      const allZeroQuantity = highPriceSims.every(s => {
        const quantity = s['Predicted Quantity'] || s.quantity || 0;
        return quantity === 0;
      });
      
      if (allZeroQuantity) {
        print.success('Extreme price check passed: All high prices result in zero quantity');
        return true;
      } else {
        print.warning('Extreme price check failed: Some high prices show non-zero quantity');
        return false;
      }
    } else {
      print.error('Extreme price simulation failed or returned invalid data');
      console.log(data);
      return false;
    }
  } catch (error) {
    print.error(`Error testing extreme price simulation: ${error.message}`);
    return false;
  }
}

// Run all tests
async function runTests() {
  print.section('Frontend API Tests');
  
  let passed = 0;
  let failed = 0;
  
  // Basic API tests
  if (await testHealth()) passed++; else failed++;
  if (await testLocations()) passed++; else failed++;
  if (await testProducts()) passed++; else failed++;
  
  // Scenario planner tests
  print.section('Scenario Planner Tests');
  if (await testSimulateRevenue()) passed++; else failed++;
  if (await testSimulateRevenueAllLocations()) passed++; else failed++;
  if (await testExtremePrice()) passed++; else failed++;
  
  // Print summary
  print.section('Test Results');
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log(`Total: ${passed + failed}`);
  
  if (failed === 0) {
    print.success('All tests passed successfully!');
    process.exit(0);
  } else {
    print.error(`${failed} test(s) failed.`);
    process.exit(1);
  }
}

// Set timeout to exit if tests hang
setTimeout(() => {
  print.error(`Tests timed out after ${TEST_TIMEOUT / 1000} seconds`);
  process.exit(1);
}, TEST_TIMEOUT);

// Run the tests
runTests(); 