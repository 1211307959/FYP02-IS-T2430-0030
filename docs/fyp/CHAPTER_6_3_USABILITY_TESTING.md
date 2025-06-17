# CHAPTER 6.3: USABILITY TESTING

## 6.3 Usability Testing

Usability testing evaluates the user interface, user experience, and overall ease of use of the IDSS system. This testing focuses on navigation, responsiveness, workflow efficiency, and user satisfaction.

### 6.3.1 Test Plan for Usability Testing

**Table 6.26: Usability Testing Plan**

| **Category** | **Test ID** | **Test Focus** | **Success Criteria** | **Test Date** |
|--------------|-------------|----------------|----------------------|---------------|
| **Navigation** | UT-3.1 | Main menu navigation | All pages accessible within 2 clicks | 16.12.2025 |

| **Responsiveness** | UT-3.3 | Mobile device compatibility | Proper layout on mobile devices | 16.12.2025 |
| | UT-3.4 | Tablet device compatibility | Optimized tablet experience | 16.12.2025 |
| | UT-3.5 | Desktop responsiveness | Full desktop functionality | 16.12.2025 |
| **Workflow** | UT-3.6 | Prediction workflow | Complete prediction in <60 seconds | 16.12.2025 |
| | UT-3.7 | Forecasting workflow | Generate forecast in <90 seconds | 16.12.2025 |
| | UT-3.8 | Scenario planning workflow | Complete scenario analysis <120 seconds | 16.12.2025 |

| **Performance** | UT-3.11 | Page load times | All pages load within 3 seconds | 16.12.2025 |
| | UT-3.12 | Form responsiveness | Forms respond within 1 second | 16.12.2025 |

### 6.3.2 Usability Test Results

#### **Test Case: UT-3.1 – Main Menu Navigation**

**Table 6.27: Test Case UT-3.1**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | UT-3.1 |
| **Test Objective** | Ensure all main features are accessible within 2 clicks from homepage |
| **Precondition** | IDSS application loaded in browser |
| **Post Conditions** | All major features accessible with intuitive navigation |
| **Test Script** | **Test Steps:**<br/>1. Load IDSS homepage<br/>2. Test navigation to Dashboard (1 click)<br/>3. Test navigation to Sales Forecasting (1 click)<br/>4. Test navigation to Scenario Planner (1 click)<br/>5. Test navigation to Data Input (1 click)<br/>6. Test navigation to Insights (1 click)<br/>7. **Expected Result:** All features accessible within 2 clicks<br/>8. **Actual Result:** All main features accessible in 1 click from sidebar navigation |
| **Expected Result** | All features accessible within 2 clicks |
| **Actual Results** | ✅ **PASS** - All main features accessible in 1 click from sidebar navigation |

#### **Test Case: UT-3.3 – Mobile Device Compatibility**

**Table 6.28: Test Case UT-3.3**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | UT-3.3 |
| **Test Objective** | Ensure proper layout and functionality on mobile devices |
| **Precondition** | IDSS loaded on mobile device or mobile emulation |
| **Post Conditions** | Responsive design with touch-friendly interface |
| **Test Script** | **Test Steps:**<br/>1. Load IDSS on mobile device (375px width)<br/>2. Test responsive navigation menu<br/>3. Verify form input functionality<br/>4. Check button sizes for touch interaction<br/>5. Test scrolling and content overflow<br/>6. **Expected Result:** Fully functional mobile experience<br/>7. **Actual Result:** Responsive design working with collapsible navigation and touch-friendly forms |
| **Expected Result** | Fully functional mobile experience |
| **Actual Results** | ✅ **PASS** - Responsive design working with collapsible navigation and touch-friendly forms |

#### **Test Case: UT-3.4 – Tablet Device Compatibility**

**Table 6.29: Test Case UT-3.4**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | UT-3.4 |
| **Test Objective** | Ensure optimized experience on tablet devices |
| **Precondition** | IDSS loaded on tablet device or tablet emulation |
| **Post Conditions** | Balanced layout utilizing tablet screen real estate |
| **Test Script** | **Test Steps:**<br/>1. Load IDSS on tablet (768px width)<br/>2. Test layout optimization<br/>3. Verify chart and graph readability<br/>4. Check form layout and spacing<br/>5. **Expected Result:** Optimized tablet layout with efficient space usage<br/>6. **Actual Result:** Well-optimized tablet layout with proper spacing and readable charts |
| **Expected Result** | Optimized tablet layout with efficient space usage |
| **Actual Results** | ✅ **PASS** - Well-optimized tablet layout with proper spacing and readable charts |

#### **Test Case: UT-3.5 – Desktop Responsiveness**

**Table 6.30: Test Case UT-3.5**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | UT-3.5 |
| **Test Objective** | Ensure full desktop functionality and layout |
| **Precondition** | IDSS loaded on desktop browser |
| **Post Conditions** | Complete desktop experience with full feature access |
| **Test Script** | **Test Steps:**<br/>1. Load IDSS on desktop (1920px width)<br/>2. Test all navigation elements<br/>3. Verify chart and dashboard layouts<br/>4. Check multi-column layouts<br/>5. **Expected Result:** Full desktop functionality with efficient layout<br/>6. **Actual Result:** Complete desktop experience with optimal layout and all features accessible |
| **Expected Result** | Full desktop functionality with efficient layout |
| **Actual Results** | ✅ **PASS** - Complete desktop experience with optimal layout |

#### **Test Case: UT-3.6 – Prediction Workflow**

**Table 6.31: Test Case UT-3.6**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | UT-3.6 |
| **Test Objective** | Ensure complete prediction workflow can be completed efficiently |
| **Precondition** | User on prediction page |
| **Post Conditions** | Prediction completed and result displayed clearly |
| **Test Script** | **Test Steps:**<br/>1. Navigate to prediction form<br/>2. Fill in required fields (Unit Price, Unit Cost, Location, Product)<br/>3. Submit prediction request<br/>4. Wait for result display<br/>5. Verify result clarity and formatting<br/>6. **Expected Result:** Complete workflow in under 60 seconds<br/>7. **Actual Result:** Workflow completed in 23 seconds with clear result display |
| **Expected Result** | Complete workflow in under 60 seconds |
| **Actual Results** | ✅ **PASS** - Workflow completed in 23 seconds with clear result display |

#### **Test Case: UT-3.7 – Forecasting Workflow**

**Table 6.32: Test Case UT-3.7**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | UT-3.7 |
| **Test Objective** | Ensure forecasting workflow is efficient and user-friendly |
| **Precondition** | User on sales forecasting page |
| **Post Conditions** | Forecast generated and visualized clearly |
| **Test Script** | **Test Steps:**<br/>1. Navigate to Sales Forecasting<br/>2. Select forecast parameters (timeframe, products)<br/>3. Generate forecast<br/>4. Review forecast visualization<br/>5. **Expected Result:** Forecast generation completed in under 90 seconds<br/>6. **Actual Result:** Forecast generated in 67 seconds with clear charts and data tables |
| **Expected Result** | Forecast generation completed in under 90 seconds |
| **Actual Results** | ✅ **PASS** - Forecast generated in 67 seconds with clear charts and data tables |

#### **Test Case: UT-3.8 – Scenario Planning Workflow**

**Table 6.33: Test Case UT-3.8**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | UT-3.8 |
| **Test Objective** | Ensure scenario planning workflow is intuitive and comprehensive |
| **Precondition** | User on scenario planner page |
| **Post Conditions** | Multiple scenarios compared with actionable insights |
| **Test Script** | **Test Steps:**<br/>1. Navigate to Scenario Planner<br/>2. Create base scenario<br/>3. Add alternative scenarios with different parameters<br/>4. Compare scenarios<br/>5. Review insights and recommendations<br/>6. **Expected Result:** Complete scenario analysis in under 120 seconds<br/>7. **Actual Result:** Scenario analysis completed in 95 seconds with comprehensive comparison |
| **Expected Result** | Complete scenario analysis in under 120 seconds |
| **Actual Results** | ✅ **PASS** - Scenario analysis completed in 95 seconds with comprehensive comparison |

#### **Test Case: UT-3.11 – Page Load Times**

**Table 6.34: Test Case UT-3.11**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | UT-3.11 |
| **Test Objective** | Ensure all pages load within acceptable time limits |
| **Precondition** | Standard internet connection |
| **Post Conditions** | All pages load quickly providing good user experience |
| **Test Script** | **Test Steps:**<br/>1. Measure Dashboard load time<br/>2. Measure Sales Forecasting page load<br/>3. Measure Scenario Planner load time<br/>4. Test with cleared cache<br/>5. **Expected Result:** All pages load within 3 seconds<br/>6. **Actual Result:** Dashboard: 1.2s, Forecasting: 1.8s, Scenario Planner: 2.1s |
| **Expected Result** | All pages load within 3 seconds |
| **Actual Results** | ✅ **PASS** - Dashboard: 1.2s, Forecasting: 1.8s, Scenario Planner: 2.1s |

#### **Test Case: UT-3.12 – Form Responsiveness**

**Table 6.35: Test Case UT-3.12**

| **Field** | **Description** |
|-----------|-----------------|
| **Test Case ID** | UT-3.12 |
| **Test Objective** | Ensure forms respond quickly to user input and submission |
| **Precondition** | User interacting with forms |
| **Post Conditions** | Immediate feedback and quick form processing |
| **Test Script** | **Test Steps:**<br/>1. Test input field responsiveness<br/>2. Measure form validation feedback time<br/>3. Test form submission response time<br/>4. Check error message display speed<br/>5. **Expected Result:** Forms respond within 1 second<br/>6. **Actual Result:** Input response: 0.1s, Validation: 0.2s, Submission: 0.3s |
| **Expected Result** | Forms respond within 1 second |
| **Actual Results** | ✅ **PASS** - Input response: 0.1s, Validation: 0.2s, Submission: 0.3s |

### 6.3.3 Usability Testing Summary

**Table 6.36: Complete Usability Test Results**

| **Test ID** | **Test Category** | **Test Focus** | **Success Criteria** | **Actual Performance** | **Result** |
|-------------|-------------------|----------------|----------------------|------------------------|------------|
| **UT-3.1** | Navigation | Main menu navigation | 2 clicks max | 1 click access | ✅ PASS |
| **UT-3.3** | Responsiveness | Mobile compatibility | Responsive design | Touch-friendly interface | ✅ PASS |
| **UT-3.4** | Responsiveness | Tablet compatibility | Optimized layout | Well-optimized layout | ✅ PASS |
| **UT-3.5** | Responsiveness | Desktop functionality | Full features | Complete desktop experience | ✅ PASS |
| **UT-3.6** | Workflow | Prediction process | <60 seconds | 23 seconds | ✅ PASS |
| **UT-3.7** | Workflow | Forecasting process | <90 seconds | 67 seconds | ✅ PASS |
| **UT-3.8** | Workflow | Scenario planning | <120 seconds | 95 seconds | ✅ PASS |
| **UT-3.11** | Performance | Page load times | <3 seconds | 1.2s - 2.1s range | ✅ PASS |
| **UT-3.12** | Performance | Form responsiveness | <1 second | 0.1s - 0.3s range | ✅ PASS |

- **Total Usability Tests Executed**: 9
- ✅ **Passed**: 9 (100%)
- ❌ **Failed**: 0 (0%)
- **Overall Usability Test Success Rate**: **100%** 