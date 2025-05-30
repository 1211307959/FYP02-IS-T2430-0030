# Scenario Planner Test Documentation

This document outlines the comprehensive testing strategy for the Scenario Planner feature, which allows users to simulate revenue outcomes based on different pricing scenarios across various locations and products.

## Testing Goals

1. Verify correct loading and display of dynamic location and product data
2. Validate accurate price simulation with proper price elasticity effects
3. Confirm proper handling of the "All Locations" option
4. Ensure consistent field mappings between frontend and backend
5. Test responsiveness to extreme price values
6. Verify data refresh functionality

## Test Components

The testing suite consists of three primary test scripts:

1. **Backend API Test** (`test_scenario_planner.py`) - Tests the Flask API endpoints
2. **Frontend API Test** (`test_scenario_planner_frontend.js`) - Tests the Next.js API routes
3. **Component Test** (`test_component_scenario_planner.js`) - Tests the React components

## Key Requirements Tested

### 1. Dynamic Data Loading

- Locations are loaded from the data files, not hardcoded
- Products are dynamically loaded with correct metadata
- Product prices and costs are accurately loaded
- UI elements update when new data is loaded

### 2. "All Locations" Option

- "All Locations" appears as the first option in location dropdowns
- Backend handles the "All Locations" case by using a default location
- Response includes appropriate notification about default location usage
- UI displays appropriate messages when using "All Locations"

### 3. Price Elasticity

- Lower prices result in higher quantities
- Higher prices result in lower quantities
- Extreme prices (>100,000) are properly handled with error messages
- Revenue and profit calculations are accurate based on price and quantity

### 4. Field Name Consistency

- Different field naming conventions are normalized
- Both camelCase and snake_case fields are supported
- Frontend receives consistent field names regardless of backend changes
- Legacy field names continue to work for backward compatibility

### 5. Error Handling

- Invalid inputs are properly validated
- API errors are caught and displayed
- Timeout handling prevents infinite loading states
- Fallback values are provided when data is unavailable

### 6. Data Refresh

- "Reload Product Data" button refreshes the product data
- UI updates with the latest data after refresh
- Data file changes are detected and reflected in the UI

## Test Scenarios

### Backend API Test Scenarios

1. **Location and Product Fetching**
   - Fetch and validate locations list
   - Fetch and validate products list
   - Verify "All" location is included

2. **Revenue Prediction**
   - Test prediction with different locations
   - Test prediction with "All" location
   - Verify note about default location for "All"
   - Compare predictions across locations

3. **Revenue Simulation**
   - Test simulation with different price points
   - Verify price elasticity effect (higher price = lower quantity)
   - Test simulation with "All" location
   - Compare simulation results across locations

### Frontend API Test Scenarios

1. **Next.js API Routes**
   - Test locations API route
   - Test products API route
   - Test product-data API route
   - Test simulate-revenue API route
   - Test with "All Locations"

2. **Field Mapping**
   - Verify correct mapping of locationId to Location
   - Verify correct mapping of productId to _ProductID
   - Verify correct mapping of unitPrice to Unit Price
   - Verify correct mapping of unitCost to Unit Cost

3. **Response Normalization**
   - Verify consistent field names in response
   - Check for presence of both camelCase and snake_case fields
   - Verify note field is preserved

### Component Test Scenarios

1. **UI Rendering**
   - Verify location dropdown renders correctly
   - Verify product dropdown renders correctly
   - Verify price and cost inputs render correctly
   - Verify chart renders after simulation

2. **User Interactions**
   - Test location selection
   - Test product selection
   - Test price input
   - Test cost input
   - Test simulate button
   - Test reset button
   - Test reload button

3. **Simulation Results**
   - Verify chart updates with simulation results
   - Verify Apply This Scenario button appears
   - Verify price elasticity effect is visible

## Test Execution

### Running Backend Tests

```bash
# Run Flask API tests
python tests/test_scenario_planner.py
```

### Running Frontend API Tests

```bash
# Run Next.js API route tests
node tests/test_scenario_planner_frontend.js
```

### Running Component Tests

```bash
# Run React component tests with Jest
jest tests/test_component_scenario_planner.js
```

## Test Results

After running all tests, detailed reports are generated:

1. `scenario_planner_test_report.json` - Backend test results
2. `scenario_planner_frontend_test_report.json` - Frontend API test results
3. Jest output for component tests

## Fixed Issues

Through comprehensive testing, the following issues were identified and fixed:

1. **Field Naming Inconsistency**
   - Problem: Backend used different field names than expected by frontend
   - Fix: Added field normalization in the simulate-revenue API route

2. **"All Locations" Handling**
   - Problem: "All" location not properly handled by backend
   - Fix: Modified API to use default location and include note in response

3. **Extreme Price Values**
   - Problem: Very high prices caused backend errors
   - Fix: Added validation and proper error handling for extreme values

4. **Price Elasticity Inconsistency**
   - Problem: Not all locations showed proper price elasticity
   - Fix: Ensured consistent price elasticity behavior across all locations

5. **Data Refresh Issues**
   - Problem: UI did not update when product data was reloaded
   - Fix: Added proper state updates and event handling for data reload

## Issues Identified

Through our testing of the scenario planner feature, we identified several issues that were causing errors:

1. **Null Value Handling**: The Flask backend was failing with `TypeError: float() argument must be a string or a real number, not 'NoneType'` when null values were passed for `_ProductID`, `Unit Price`, and `Unit Cost`.

2. **Type Conversion**: Even when default values were provided, there were issues with type conversion when parsing the request data.

3. **Field Name Inconsistency**: Different naming conventions between frontend and backend caused compatibility issues.

4. **Error Handling**: Insufficient error handling for edge cases like extremely high prices.

## Fixes Implemented

### 1. Backend Flask API (`combined_revenue_api_50_50.py`)

- Added explicit handling for null values in required fields:
  ```python
  if data.get('_ProductID') is None:
      data['_ProductID'] = DEFAULT_PRODUCT_ID
        
  if data.get('Unit Price') is None:
      data['Unit Price'] = 100.0  # Default price if none provided
        
  if data.get('Unit Cost') is None:
      data['Unit Cost'] = 50.0  # Default cost if none provided
  ```

### 2. Revenue Predictor (`revenue_predictor_50_50.py`)

- Enhanced `simulate_price_variations` function to handle null and missing values:
  ```python
  # Check for missing or null values in base_data and set defaults
  if base_data is None:
      base_data = {}
        
  # Set default values for missing or null fields
  if base_data.get('Unit Price') is None:
      base_data['Unit Price'] = 100.0
        
  if base_data.get('Unit Cost') is None:
      base_data['Unit Cost'] = 50.0
  ```

- Improved type conversion for numeric fields:
  ```python
  profit = revenue - (quantity * float(sim_data.get('Unit Cost', 0)))
  ```

### 3. Next.js API Route (`app/api/simulate-revenue/route.ts`)

- Created a comprehensive data validation and transformation process:
  ```typescript
  // Handle missing or null values
  const processedData = { ...data };
  
  // Handle null/undefined values for required fields
  if (processedData._ProductID === null || processedData._ProductID === undefined) {
    processedData._ProductID = 1; // Default product ID
  }
  
  // Ensure numeric fields are properly typed
  processedData._ProductID = parseInt(String(processedData._ProductID), 10);
  processedData['Unit Price'] = parseFloat(String(processedData['Unit Price']));
  processedData['Unit Cost'] = parseFloat(String(processedData['Unit Cost']));
  ```

- Added consistent field name normalization in the response:
  ```typescript
  const normalizedResults = resultData.map((item: any) => ({
    Scenario: item.Scenario || item.scenario || 'Unknown',
    'Unit Price': item['Unit Price'] || item.unitPrice || 0,
    'Predicted Revenue': item['Predicted Revenue'] || item.revenue || item.predicted_revenue || 0,
    // ...including both field naming conventions for compatibility
    revenue: item['Predicted Revenue'] || item.revenue || item.predicted_revenue || 0,
  }));
  ```

### 4. Frontend API Client (`lib/api.ts`)

- Enhanced the `simulateScenarios` function to validate data before sending:
  ```typescript
  // Make sure required fields have values (not null or undefined)
  if (apiData._ProductID === null || apiData._ProductID === undefined) {
    apiData._ProductID = 1; // Default product ID
  }
  
  // Ensure values are proper types
  apiData._ProductID = parseInt(String(apiData._ProductID), 10);
  apiData['Unit Price'] = parseFloat(String(apiData['Unit Price']));
  apiData['Unit Cost'] = parseFloat(String(apiData['Unit Cost']));
  ```

## Testing Strategy

1. **Unit Testing**:
   - Verified proper handling of null and undefined values
   - Confirmed correct type conversion for numeric fields
   - Tested field name normalization

2. **Integration Testing**:
   - Tested the API route with various input scenarios
   - Verified communication between the NextJS API and Flask backend
   - Confirmed proper handling of the "All Locations" option

3. **End-to-End Testing**:
   - Tested the scenario planner from the UI
   - Verified price simulation displays correctly
   - Confirmed price elasticity is shown accurately (lower prices = higher quantities)

## Verification

The scenario planner now properly handles:

1. **Null Values**: Default values are provided for any missing or null fields
2. **Type Conversion**: All numeric values are properly converted to the correct type
3. **Field Naming**: Both camelCase and snake_case field names are supported for compatibility
4. **Error Handling**: Extreme price values and other edge cases are properly handled
5. **"All Locations" Option**: Default location is used with proper notification

## Conclusion

These improvements ensure that the scenario planner functions reliably across different input scenarios and edge cases. The robust error handling and default value system prevents crashes and provides a better user experience, while the consistent field naming ensures compatibility between different parts of the application. 