# APPENDIX: FILE & FUNCTION INDEX

## A.1 Backend Module Index (Python)

### A.1.1 Core ML Engine

#### File: `revenue_predictor_time_enhanced_ethical.py`
**Module**: Machine Learning Core
**Purpose**: Ethical time-enhanced revenue prediction using LightGBM

| Function | Purpose | Inputs | Outputs |
|----------|---------|--------|---------|
| `predict_revenue()` | Main prediction function | Product parameters, pricing, date | Revenue prediction with metrics |
| `validate_and_convert_input()` | Input validation and type conversion | Raw input dictionary | Validated parameters |
| `load_model()` | Load trained ML model and encoders | Model file paths | Model components |
| `add_enhanced_time_features()` | Time-based feature engineering | Date parameters | Enhanced feature set |
| `preprocess()` | Feature preprocessing pipeline | Raw data, encoders | ML-ready DataFrame |
| `predict_revenue_for_forecasting()` | Optimized prediction for batch processing | Product parameters | Revenue prediction |
| `simulate_price_variations()` | Price scenario simulation | Base parameters, price ranges | Scenario analysis |
| `optimize_price()` | Price optimization algorithm | Product parameters, optimization metric | Optimal price recommendations |
| `predict_revenue_batch()` | Batch prediction processing | List of prediction parameters | Batch prediction results |
| `get_available_locations_and_products()` | Dynamic data discovery | CSV file paths | Available locations and products |

#### File: `sales_forecast_enhanced.py`
**Module**: Sales Forecasting
**Purpose**: Time-series forecasting with confidence intervals

| Function | Purpose | Inputs | Outputs |
|----------|---------|--------|---------|
| `forecast_sales()` | Generate sales forecast | Product, location, date range | Forecast with confidence intervals |
| `forecast_multiple_products()` | Multi-product forecasting | Product list, parameters | Multiple product forecasts |
| `analyze_price_trend()` | Price sensitivity analysis | Price variations, date range | Trend analysis |
| `forecast_sales_with_frequency()` | Custom frequency forecasting | Parameters, frequency setting | Time-specific forecasts |
| `forecast_multiple_products_with_frequency()` | Multi-product custom forecasting | Product list, frequency | Multiple frequency forecasts |
| `forecast_aggregated_business_revenue()` | Business-wide revenue forecasting | All products, locations | Aggregated business forecast |
| `forecast_business_quick_overview()` | Rapid business overview | Basic parameters | Quick forecast summary |

#### File: `actionable_insights.py`
**Module**: Business Intelligence
**Purpose**: AI-powered business insight generation

| Function | Purpose | Inputs | Outputs |
|----------|---------|--------|---------|
| `actionable_insights()` | Generate business insights | Complete business dataset | Prioritized insights list |
| `calculate_insight_priority()` | Priority scoring algorithm | Insight data, business metrics | Priority score (0-100) |

---

### A.1.2 API Layer

#### File: `combined_time_enhanced_ethical_api.py`
**Module**: REST API
**Purpose**: Flask API providing all system endpoints

| Endpoint Function | HTTP Method | Purpose | Input Format | Output Format |
|-------------------|-------------|---------|--------------|---------------|
| `health_check()` | GET /health | System health monitoring | None | Status JSON |
| `get_locations()` | GET /locations | Available locations | None | Locations array |
| `get_products()` | GET /products | Available products | None | Products array |
| `predict_revenue_endpoint()` | POST /predict-revenue | Revenue prediction | Product parameters JSON | Prediction results JSON |
| `simulate_revenue_endpoint()` | POST /simulate-revenue | Price scenario simulation | Simulation parameters JSON | Scenario results JSON |
| `optimize_price_endpoint()` | POST /optimize-price | Price optimization | Optimization parameters JSON | Optimal price JSON |
| `forecast_sales_endpoint()` | POST /forecast-sales | Sales forecasting | Forecast parameters JSON | Forecast data JSON |
| `forecast_multiple_endpoint()` | POST /forecast-multiple | Multi-product forecasting | Multiple product parameters JSON | Multiple forecasts JSON |
| `forecast_trend_endpoint()` | POST /forecast-trend | Price trend analysis | Trend parameters JSON | Trend analysis JSON |
| `dashboard_data_endpoint()` | GET /dashboard-data | Business dashboard metrics | None | Dashboard data JSON |
| `get_comprehensive_insights()` | GET /insights | Comprehensive insights | Optional category filter | Insights with priorities JSON |
| `reload_data_endpoint()` | POST /reload-data | Data source reload | Confirmation JSON | Reload status JSON |
| `manual_entry_endpoint()` | POST /manual-entry | Manual data save | Manual entry CSV JSON | Confirmation JSON |

---

## A.2 Frontend Module Index (TypeScript/React)

### A.2.1 Page Components

#### File: `app/dashboard/page.tsx`
**Module**: Dashboard Interface
**Purpose**: Business metrics and performance display

#### File: `app/sales-forecasting/page.tsx`
**Module**: Forecasting Interface
**Purpose**: Sales forecasting and prediction

#### File: `app/insights/page.tsx`
**Module**: Business Intelligence Interface
**Purpose**: Insight display and interaction

#### File: `app/scenario-planner/page.tsx`
**Module**: Scenario Planning Interface
**Purpose**: Price optimization and what-if analysis

#### File: `app/data-input/page.tsx`
**Module**: Data Management Interface
**Purpose**: Data upload, manual entry (calendar date picker, custom product/location), and management

### A.2.2 API Integration

#### File: `lib/api.ts`
**Module**: API Client
**Purpose**: Frontend-backend communication

| Function | Purpose | Inputs | Outputs |
|----------|---------|--------|---------|
| `predictRevenue()` | Revenue prediction API call | Prediction parameters | Prediction results Promise |
| `fetchForecastSales()` | Sales forecast API call | Forecast parameters | Forecast data Promise |
| `getDashboardData()` | Dashboard data API call | None | Dashboard metrics Promise |
| `getProducts()` | Products list API call | None | Products array Promise |
| `getLocations()` | Locations list API call | None | Locations array Promise |

---

## A.3 Configuration Files

### A.3.1 Python Configuration

#### File: `requirements.txt`
**Purpose**: Python dependency management
**Contents**: 
- pandas>=1.3.5 (Data manipulation)
- numpy>=1.21.6 (Numerical computing)
- scikit-learn>=1.0.2 (ML utilities)
- lightgbm>=3.3.2 (Gradient boosting)
- flask>=2.0.1 (Web framework)
- joblib>=1.1.0 (Model serialization)

### A.3.2 Node.js Configuration

#### File: `package.json`
**Purpose**: Node.js dependency and script management
**Key Dependencies**:
- next@14.1.0 (React framework)
- react@18.2.0 (UI library)
- typescript@5.0 (Type safety)
- tailwindcss@3.3.0 (CSS framework)
- recharts (Data visualization)

---

## A.4 Data Files

### A.4.1 Training Data

#### File: `trainingdataset.csv`
**Purpose**: Primary ML training dataset
**Schema**: ProductID, Location, Unit Price, Unit Cost, Revenue, Quantity, Date fields
**Size**: 100,000+ transaction records
**Coverage**: 47 products × 5 locations × ~425 days

#### File: `manual_entry_template.csv`
**Purpose**: Manual data entry template
**Schema**: Identical to training dataset
**Usage**: User data input validation and integration

#### Generated Files: `manual_entry_<timestamp>.csv`
**Purpose**: Saved manual entry records (one per file)
**Location**: `public/data/`
**Schema**: Same as manual entry template

### A.4.2 Model Files

#### File: `revenue_model_time_enhanced_ethical.pkl`
**Purpose**: Trained LightGBM model
**Contents**: Model weights, parameters, performance metrics
**Performance**: R² = 0.9937

#### File: `revenue_encoders_time_enhanced_ethical.pkl`
**Purpose**: Feature encoders
**Contents**: Label encoders for categorical variables

#### File: `reference_data_time_enhanced_ethical.pkl`
**Purpose**: Reference statistics
**Contents**: Feature scaling parameters, validation ranges

---

## A.5 Testing Files

### A.5.1 Test Scripts

#### File: `tests/comprehensive_test_summary.py`
**Purpose**: Comprehensive system testing
**Coverage**: All major features, API endpoints, integration scenarios

#### File: `tests/run_comprehensive_test.py`
**Purpose**: Test execution controller
**Function**: Automated test suite execution and reporting

---

## A.6 Documentation Files

### A.6.1 Project Documentation

#### File: `README.md`
**Purpose**: Project overview and setup instructions
**Contents**: Installation, usage, deployment guide

#### File: `PROJECT_STRUCTURE.md`
**Purpose**: Codebase organization documentation
**Contents**: Directory structure, file organization, development guidelines

### A.6.2 FYP Documentation

#### File: `docs/fyp/CHAPTER_3_REQUIREMENTS.md`
**Purpose**: Requirements analysis and specification
**Contents**: Functional and non-functional requirements, user requirements

#### File: `docs/fyp/CHAPTER_4_SYSTEM_DESIGN.md`
**Purpose**: System design and architecture
**Contents**: UML diagrams, interface design, system architecture

#### File: `docs/fyp/CHAPTER_5_IMPLEMENTATION.md`
**Purpose**: Implementation details and technical specifications
**Contents**: Technology stack, modules, challenges, solutions

#### File: `docs/fyp/CHAPTER_6_TESTING.md`
**Purpose**: Testing methodology and results
**Contents**: Test cases, performance metrics, acceptance criteria

---

## A.7 Summary Statistics

### A.7.1 Codebase Metrics

**Backend (Python)**:
- Core files: 4 main modules
- API endpoints: 14 major endpoints
- Functions: 50+ core functions
- Lines of code: ~3,000+ lines

**Frontend (TypeScript/React)**:
- Page components: 5 main pages
- UI components: 20+ reusable components
- API routes: 13 Next.js API routes
- Lines of code: ~2,500+ lines

**Total Project Size**:
- Files: 100+ files across all categories
- Dependencies: 15+ Python packages, 50+ Node.js packages
- Test coverage: 60+ test cases
- Documentation: 6 comprehensive chapters

### A.7.2 Module Dependencies

**Dependency Flow**:
1. **Data Layer**: CSV files → Data management functions
2. **ML Layer**: Data → Feature engineering → Model prediction
3. **API Layer**: ML functions → HTTP endpoints → JSON responses
4. **Frontend Layer**: API calls → React components → User interface
5. **Integration**: All layers → Complete business intelligence system

**Key Integration Points**:
- ML model predictions power all frontend features
- API layer coordinates all backend modules
- Frontend components provide unified user experience
- Testing framework validates entire system integration

This comprehensive index enables developers and stakeholders to quickly locate specific functionality, understand system architecture, and navigate the codebase effectively.