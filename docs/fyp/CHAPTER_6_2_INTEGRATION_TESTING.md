# CHAPTER 6.2: INTEGRATION TESTING

## 6.2 Integration Testing

Integration testing evaluates the interfaces and interaction between integrated system components. This testing focuses on data flow between modules and API endpoint functionality.

### 6.2.1 Test Plan for Integration Testing

**Table 6.20: Integration Testing Plan**

| **Interface** | **Test ID** | **Component A** | **Component B** | **Test Focus** | **Test Date** |
|---------------|-------------|----------------|-----------------|----------------|---------------|
| **API-ML Integration** | IT-2.1 | Flask API | ML Prediction Engine | Data exchange and prediction accuracy | 16.12.2025 |
| **Frontend-Backend** | IT-2.2 | Next.js Frontend | Flask API | HTTP requests and response handling | 16.12.2025 |
| **Data-Model Integration** | IT-2.3 | CSV Data Loader | ML Model | Data preprocessing and model input | 16.12.2025 |

### 6.2.2 Test Data for Integration Testing

**Table 6.21: Integration Test Data**

| **Test ID** | **Input Data** | **Interface Points** | **Expected Data Flow** |
|-------------|----------------|---------------------|------------------------|
| **IT-2.1** | Unit Price: $3000, Unit Cost: $1200, Location: "Central", Product ID: 1 | Flask API → ML Engine → Response | JSON request → Prediction → JSON response |
| **IT-2.2** | Frontend form data: Price $5000, Cost $2000 | Next.js → Flask API → Response | Form submit → HTTP POST → UI update |
| **IT-2.3** | trainingdataset.csv (100,000+ rows) | CSV → Preprocessor → ML Model | Raw data → Encoded features → Predictions |

### 6.2.3 Integration Test Results

#### **Test Case: IT-2.1 – API-ML Integration**

**Table 6.22: Test Case IT-2.1**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | IT-2.1 |
| **Test Objective** | Ensure Flask API successfully communicates with ML prediction engine |
| **Precondition** | Flask API server running, ML model loaded |
| **Post Conditions** | API returns valid prediction response with proper formatting |
| **Test Script** | **Test Steps:**<br/>1. Send POST request to /api/predict endpoint<br/>2. Include valid business data in request body<br/>3. Verify ML engine receives and processes data<br/>4. Check prediction accuracy and response format<br/>5. **Expected Result:** HTTP 200 with prediction: {"predicted_revenue": <number>}<br/>6. **Actual Result:** HTTP 200 with {"predicted_revenue": 9384.62} |
| **Expected Result** | HTTP 200 with prediction: {"predicted_revenue": <number>} |
| **Actual Results** | ✅ **PASS** - HTTP 200 with {"predicted_revenue": 9384.62} |

#### **Test Case: IT-2.2 – Frontend-Backend Integration**

**Table 6.23: Test Case IT-2.2**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | IT-2.2 |
| **Test Objective** | Ensure Next.js frontend successfully communicates with Flask backend |
| **Precondition** | Next.js development server and Flask API both running |
| **Post Conditions** | Frontend receives and displays prediction data correctly |
| **Test Script** | **Test Steps:**<br/>1. Access frontend prediction form<br/>2. Submit prediction request via frontend<br/>3. Verify CORS headers and request routing<br/>4. Check data display and error handling<br/>5. **Expected Result:** Prediction displayed with proper formatting and error handling<br/>6. **Actual Result:** Prediction $9,384.62 displayed correctly with full error handling |
| **Expected Result** | Prediction displayed with proper formatting and error handling |
| **Actual Results** | ✅ **PASS** - Prediction $9,384.62 displayed correctly with full error handling |

#### **Test Case: IT-2.3 – Data-Model Integration**

**Table 6.24: Test Case IT-2.3**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | IT-2.3 |
| **Test Objective** | Ensure CSV data loader properly feeds processed data to ML model |
| **Precondition** | trainingdataset.csv loaded, ML model and encoders operational |
| **Post Conditions** | Seamless data flow from CSV to ML model with proper preprocessing |
| **Test Script** | **Test Steps:**<br/>1. Load business data from trainingdataset.csv<br/>2. Process data through preprocessing pipeline<br/>3. Feed processed data to ML model<br/>4. Verify prediction accuracy and data integrity<br/>5. **Expected Result:** Seamless data flow with accurate predictions<br/>6. **Actual Result:** Complete data pipeline functioning with 0.9937 R² accuracy |
| **Expected Result** | Seamless data flow with accurate predictions |
| **Actual Results** | ✅ **PASS** - Complete data pipeline functioning with 0.9937 R² accuracy |

### 6.2.4 Integration Testing Summary

**Table 6.25: Complete Integration Test Results**

| **Test ID** | **Interface** | **Test Input** | **Expected Output** | **Actual Output** | **Response Time** | **Result** |
|-------------|---------------|----------------|-------------------|-------------------|-------------------|------------|
| **IT-2.1** | API-ML Integration | POST /api/predict with business data | HTTP 200 + prediction JSON | {"predicted_revenue": 9384.62} | 0.187s | ✅ PASS |
| **IT-2.2** | Frontend-Backend | Form submission via React | Prediction display | $9,384.62 formatted correctly | 0.245s | ✅ PASS |
| **IT-2.3** | Data-Model Pipeline | 100,000+ CSV rows | Accurate predictions | R² = 0.9937 accuracy | 1.234s | ✅ PASS |

- **Total Integration Tests Executed**: 3
- ✅ **Passed**: 3 (100%)
- ❌ **Failed**: 0 (0%)
- **Overall Integration Test Success Rate**: **100%** 