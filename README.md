# Revenue Prediction System - IDSS for Small Businesses

## Project Overview
A production-ready web-based decision support system that leverages ethical machine learning to provide small businesses with accurate revenue predictions and data-driven insights. The system uses an advanced ethical time-enhanced LightGBM model to analyze historical sales data and generate actionable business recommendations.

**Current Production Model**: Ethical Time-Enhanced LightGBM Model (R² = 0.9937)

**Key Features**:
- **Accurate Revenue Prediction**: 99.37% accuracy using ethical AI without target leakage
- **Interactive Scenario Planning**: Sophisticated price optimization and what-if analysis
- **Sales Forecasting**: Advanced time-series forecasting with confidence intervals
- **Business Insights**: Dynamic recommendations with implementation plans
- **Responsive Dashboard**: Real-time visualizations and KPI monitoring
- **Price Elasticity Modeling**: Economic-based quantity and revenue predictions
- **Temporal Analytics**: Seasonal, holiday, and weekday pattern analysis
- **Location Intelligence**: Multi-location aggregation and comparison

**Target Users**: Small business owners, retail managers, e-commerce operators, data analysts

## System Architecture
```mermaid
graph TD
    A[Web Frontend - Next.js] --> B[Next.js API Routes]
    B --> C[Flask Backend API]
    C --> D[ML Models - LightGBM/XGBoost]
    D --> E[Feature Engineering Pipeline]
    C --> F[CSV Data Processor]
    F --> G[Combined Historical Data]
    H[Multiple CSV Files] --> F
```

### Use Case Diagram
```mermaid
graph TD
    subgraph "IDSS System"
        UC1[View Dashboard]
        UC2[Simulate Price Scenarios]
        UC3[Get Business Insights]
        UC4[Forecast Sales]
        UC5[Upload Data]
        UC6[Optimize Pricing]
    end
    
    subgraph "Users"
        BOwner[Business Owner]
        Manager[Store Manager]
        Analyst[Data Analyst]
    end
    
    BOwner --> UC1
    BOwner --> UC2
    BOwner --> UC3
    BOwner --> UC4
    BOwner --> UC6
    
    Manager --> UC1
    Manager --> UC2
    Manager --> UC4
    Manager --> UC5
    
    Analyst --> UC1
    Analyst --> UC2
    Analyst --> UC3
    Analyst --> UC4
    Analyst --> UC5
    Analyst --> UC6
```

### Activity Diagram
```mermaid
graph TD
    Start([Start]) --> UploadData[Upload Sales Data]
    UploadData --> ProcessData[Process & Combine Data]
    ProcessData --> ViewDashboard[View Dashboard Metrics]
    
    ViewDashboard --> Decision{Make Decision?}
    Decision -->|Yes| PlanScenario[Plan Price Scenario]
    Decision -->|No| CheckInsights[Check Business Insights]
    
    PlanScenario --> SimulatePrice[Simulate Price Changes]
    SimulatePrice --> OptimizePrice[Find Optimal Price Point]
    OptimizePrice --> ForecastSales[Forecast Future Sales]
    
    CheckInsights --> ReviewRecommendations[Review Action Recommendations]
    ReviewRecommendations --> ImplementChanges[Implement Business Changes]
    
    ForecastSales --> ImplementChanges
    ImplementChanges --> Evaluate[Evaluate Results]
    Evaluate --> End([End])
```

### Class Diagram
```mermaid
classDiagram
    class DataProcessor {
        +loadData(files)
        +processData()
        +combineDatasets()
        +getProcessedData()
    }
    
    class RevenueModel {
        -modelFile
        -encoders
        +loadModel()
        +predict(inputs)
        +simulatePrices(priceRange)
        +optimizePrice(goal)
    }
    
    class BusinessInsights {
        +generateInsights(data)
        +prioritizeRecommendations()
        +getActionItems()
    }
    
    class SalesForecast {
        +forecast(timeframe)
        +calculateSeasonality()
        +getPredictions()
    }
    
    class DashboardMetrics {
        +calculateKPIs()
        +getRevenueData()
        +getProductPerformance()
        +getLocationPerformance()
    }
    
    DataProcessor --> RevenueModel
    DataProcessor --> DashboardMetrics
    RevenueModel --> BusinessInsights
    RevenueModel --> SalesForecast
    BusinessInsights --> DashboardMetrics
    SalesForecast --> DashboardMetrics
```

### Sequence Diagram
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Model
    participant DataProcessor
    
    User->>Frontend: Access Dashboard
    Frontend->>API: Request Dashboard Data
    API->>DataProcessor: Process Latest Data
    DataProcessor->>API: Return Processed Data
    API->>Frontend: Send Dashboard Metrics
    Frontend->>User: Display Dashboard
    
    User->>Frontend: Create Price Scenario
    Frontend->>API: Send Scenario Parameters
    API->>Model: Run Price Simulation
    Model->>API: Return Simulation Results
    API->>Frontend: Send Prediction Results
    Frontend->>User: Display Revenue Forecast
    
    User->>Frontend: Request Business Insights
    Frontend->>API: Request Insights Generation
    API->>Model: Analyze Data Patterns
    Model->>API: Return Insights & Recommendations
    API->>Frontend: Send Actionable Insights
    Frontend->>User: Display Recommendations
```

## Tech Stack
**Frontend**:
- Next.js 14 (React 18)
- TypeScript
- Recharts for data visualization
- Tailwind CSS with responsive design
- Shadcn UI component library

**Backend**:
- Python 3.11+
- Flask REST API with CORS support
- Pandas for data processing
- Scikit-learn for preprocessing
- LightGBM/XGBoost for ML models

**ML Pipeline**:
- Ethical Time-Enhanced LightGBM model (R² = 0.9937)
- Advanced temporal feature engineering with cyclical encodings
- No target leakage - uses only available features at prediction time
- Sophisticated price elasticity modeling
- Holiday and seasonal pattern detection
- Location and product interaction features
- Hyperparameter optimization via RandomizedSearchCV

## Quick Start

### Prerequisites
- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Git** for version control

### Installation
1. **Clone repository:**
```bash
git clone https://github.com/yourusername/idssnew.git
cd idssnew
```

2. **Install dependencies:**
```bash
# Backend (Python)
pip install -r requirements.txt

# Frontend (Node.js)
npm install
```

3. **Start the application:**
```bash
# Start backend API (Terminal 1)
python combined_time_enhanced_ethical_api.py

# Start frontend (Terminal 2)
npm run dev
```

4. **Access the application:**
- **Frontend**: http://localhost:3000
- **API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## Production Files

### Core System
- `revenue_predictor_time_enhanced_ethical.py` - Main prediction engine
- `combined_time_enhanced_ethical_api.py` - Flask API server  
- `train_time_enhanced_ethical_model.py` - Model training script
- `sales_forecast_enhanced.py` - Sales forecasting module

### Model Files (Required for Production)
- `revenue_model_time_enhanced_ethical.pkl` - Trained LightGBM model
- `revenue_encoders_time_enhanced_ethical.pkl` - Feature encoders
- `reference_data_time_enhanced_ethical.pkl` - Reference statistics
- `trainingdataset.csv` - Training dataset

### Testing
- `app_model_test.py` - Main model validation and testing
- `test_ethical_time_enhanced_model.py` - Comprehensive model tests

## Documentation
📚 **All documentation is located in the `/docs` folder** for easy navigation:

- `docs/model-guide.md` - Model architecture and performance details
- `docs/api-guide.md` - API endpoints and usage examples  
- `docs/testing-guide.md` - Testing procedures and validation
- `docs/deployment-guide.md` - Production deployment instructions
- `docs/sales-forecast-guide.md` - Sales forecasting documentation

## Technical Stack

### Machine Learning
- **Algorithm:** LightGBM Regressor with ethical feature engineering
- **Features:** 50+ advanced temporal and price-based features
- **Performance:** R² = 0.9937, MAE = 48.06, RMSE = 238.37
- **Latency:** <1ms per prediction

### Backend
- **Framework:** Flask with CORS support
- **Model Storage:** Pickle serialization
- **API Design:** RESTful with JSON responses
- **Error Handling:** Comprehensive validation and logging

### Frontend
- **Framework:** Next.js 14 with React 18
- **Styling:** Tailwind CSS with responsive design
- **Charts:** Recharts for data visualization
- **State Management:** React hooks and context

### Data Processing
- **Pandas:** Data manipulation and analysis
- **NumPy:** Numerical computations
- **Scikit-learn:** Data preprocessing and metrics

## Usage
1. **Data Management**:
   - Upload CSV files with sales data
   - System automatically combines all data files
   - Required columns: Date, ProductID, Location, UnitPrice, UnitCost, Quantity

2. **Dashboard**:
   - Interactive visualizations for revenue trends
   - Product and location performance analysis
   - Filters for date range, product, and location
   - Profit/revenue toggle for deeper analysis

3. **Scenario Planning**:
   - Simulate price changes and their impact on revenue
   - Identify optimal price points for maximum revenue or profit
   - Visualize price sensitivity curves
   - Test seasonal and location-based variations

4. **Business Insights**:
   - Data-driven recommendations with implementation plans
   - Product performance insights with severity ratings
   - Price optimization suggestions
   - Seasonal trend identification

## ML Model Details
**Core Model**: XGBoost 50/50 Split Revenue Predictor
- R² = 0.9947, MAE = 42.69, RMSE = 218.03
- Key Features:
  - Price_vs_Product_Avg (18.21%)
  - Unit Price (9.32%)
  - ProductID_Encoded (9.07%)
  - Price_Seasonal_Deviation (6.57%)
  - Price_Popularity (6.31%)
- Performance:
  - Average prediction time: <0.01s
  - Realistic price elasticity modeling
  - Accurate seasonal pattern recognition

## System Features
| Feature | Description |
|---------|-------------|
| Revenue Prediction | Accurate forecasting with 99.47% accuracy |
| Price Optimization | Optimal pricing recommendations by product |
| Scenario Simulation | Interactive "what-if" analysis for business decisions |
| Responsive Design | Mobile, tablet, and desktop support |
| Dynamic Insights | Data-driven business recommendations |
| Multi-file Processing | Automatic combination of all CSV data files |
| Business Intelligence | Product, location, and seasonal performance analysis |

## Screenshots
1. [Dashboard View](/actual_vs_predicted_50_50_split.png)
2. [Price Sensitivity](/price_sensitivity.png)
3. [Feature Importance](/feature_importance_50_50_split.png)

## Future Roadmap
- [ ] Cloud Deployment (AWS/Azure/GCP)
- [ ] Advanced Anomaly Detection
- [ ] Inventory Optimization
- [ ] Customer Segmentation Analysis
- [ ] AI-powered Strategy Recommendations
- [ ] Real-time Data Integration

## License
MIT License - See [LICENSE.md](LICENSE.md)

---

**Documentation**: [API Reference](API_DOCUMENTATION.md) | [Model Documentation](MODEL_DOCUMENTATION.md) | [Insights Documentation](MODEL_DOCUMENTATION_INSIGHTS.md)  
**Support**: Contact support@idss-system.com 