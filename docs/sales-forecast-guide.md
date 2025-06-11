# Sales Forecast Guide - Revenue Prediction System

## Overview
This guide covers the advanced sales forecasting functionality of the Revenue Prediction System, which provides time-series forecasting capabilities for business planning and inventory management.

## Introduction

The sales forecasting module leverages the ethical time-enhanced LightGBM model to generate forward-looking predictions about sales performance. Unlike the scenario planner which focuses on immediate "what-if" analysis, sales forecasting projects future performance over time periods.

### Key Differences: Sales Forecasting vs. Scenario Planner

| Feature | Sales Forecasting | Scenario Planner |
|---------|-------------------|------------------|
| **Purpose** | Future planning & trends | Immediate price optimization |
| **Time Horizon** | Days/weeks/months ahead | Current moment analysis |
| **Output** | Time-series data with confidence intervals | Price variation comparisons |
| **Use Case** | Inventory planning, capacity planning | Pricing strategy, profit optimization |
| **Data Format** | Sequential daily/weekly/monthly predictions | Side-by-side price scenarios |

## Core Features

### 1. Time-Series Forecasting
- **Daily Forecasts:** Day-by-day predictions for detailed planning
- **Weekly Aggregations:** Weekly summaries for medium-term planning  
- **Monthly Aggregations:** Monthly projections for long-term strategy
- **Confidence Intervals:** Upper and lower bounds for uncertainty quantification

### 2. Temporal Pattern Recognition
- **Seasonal Patterns:** Recognition of seasonal sales cycles
- **Weekday Effects:** Different performance on weekdays vs. weekends
- **Holiday Impact:** Special event and holiday effects on sales
- **Trend Analysis:** Long-term growth or decline patterns

### 3. Multi-Product Forecasting
- **Single Product:** Detailed forecasts for specific products
- **Multi-Product:** Aggregated forecasts across product portfolios
- **Location-Based:** Regional or location-specific forecasting
- **Business-Wide:** Overall business performance forecasting

## API Endpoints

### 1. Single Product Forecast

**Endpoint:** `POST /forecast-sales`

**Request:**
```json
{
  "_ProductID": 12,
  "Location": "North",
  "Unit Price": 150.00,
  "Unit Cost": 75.00,
  "start_date": "2024-01-01",
  "end_date": "2024-01-30",
  "frequency": "daily"
}
```

**Response:**
```json
{
  "forecast": [
    {
      "date": "2024-01-01",
      "predicted_revenue": 1247.85,
      "predicted_quantity": 8,
      "confidence_lower": 1050.00,
      "confidence_upper": 1445.70,
      "weekday": "Monday",
      "is_weekend": false,
      "is_holiday": true
    }
  ],
  "summary": {
    "total_revenue": 37435.50,
    "total_quantity": 240,
    "average_daily_revenue": 1247.85,
    "confidence_interval": 0.95,
    "forecast_days": 30
  },
  "patterns": {
    "weekday_effect": "Higher sales on weekdays",
    "seasonal_trend": "Stable performance",
    "holiday_impact": "Positive holiday boost"
  }
}
```

### 2. Multi-Product Forecast

**Endpoint:** `POST /forecast-multiple`

**Request:**
```json
{
  "products": [
    {
      "_ProductID": 12,
      "Location": "North",
      "Unit Price": 150.00,
      "Unit Cost": 75.00
    },
    {
      "_ProductID": 15,
      "Location": "South",
      "Unit Price": 200.00,
      "Unit Cost": 100.00
    }
  ],
  "start_date": "2024-01-01",
  "end_date": "2024-01-30",
  "frequency": "daily"
}
```

**Response:**
```json
{
  "forecasts": [
    {
      "product_id": 12,
      "location": "North",
      "forecast": [...],
      "summary": {
        "total_revenue": 37435.50,
        "total_quantity": 240
      }
    }
  ],
  "combined_summary": {
    "total_revenue": 89234.56,
    "total_quantity": 567,
    "products_count": 2,
    "average_daily_revenue": 2974.49
  }
}
```

### 3. Price Trend Analysis

**Endpoint:** `POST /forecast-trend`

**Request:**
```json
{
  "_ProductID": 12,
  "Location": "North",
  "Unit Cost": 75.00,
  "base_price": 150.00,
  "price_change_percent": 10,
  "days": 30
}
```

**Response:**
```json
{
  "trend_analysis": [
    {
      "day": 1,
      "price": 150.00,
      "revenue": 1247.85,
      "quantity": 8
    },
    {
      "day": 30,
      "price": 165.00,
      "revenue": 1156.34,
      "quantity": 7
    }
  ],
  "summary": {
    "revenue_change": -91.51,
    "quantity_change": -1,
    "price_elasticity": -0.73,
    "elasticity_interpretation": "Moderately elastic demand"
  }
}
```

## Frontend Implementation

### Automatic Forecast Tab

The automatic forecast provides business-wide projections without requiring detailed input:

```javascript
// Automatic forecast for all business
const generateAllProductsForecast = async () => {
  try {
    const response = await fetch('/api/forecast-multiple', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        products: allProducts,
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        frequency: 'daily'
      })
    });
    
    const data = await response.json();
    setChartData(processChartData(data));
  } catch (error) {
    console.error('Forecast generation failed:', error);
  }
};
```

### Custom Forecast Tab

The custom forecast allows specific product and location selection:

```javascript
// Custom forecast for specific parameters
const generateCustomForecast = async (productId, location) => {
  const productData = await getProductAverages(productId);
  
  const response = await fetch('/api/forecast-sales', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      _ProductID: parseInt(productId),
      Location: location,
      Unit_Price: productData.price,
      Unit_Cost: productData.cost,
      start_date: new Date().toISOString().split('T')[0],
      end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      frequency: 'daily'
    })
  });
  
  return await response.json();
};
```

## Backend Implementation

### Core Forecasting Module

The sales forecasting is implemented in `sales_forecast_enhanced.py`:

```python
def forecast_sales(product_id, location, unit_price, unit_cost, 
                  start_date, end_date, frequency='daily', automatic=False):
    """
    Generate sales forecast for a specific product over a date range.
    
    Args:
        product_id (int): Product identifier
        location (str): Sales location
        unit_price (float): Price per unit
        unit_cost (float): Cost per unit
        start_date (str): Start date (YYYY-MM-DD)
        end_date (str): End date (YYYY-MM-DD)
        frequency (str): 'daily', 'weekly', or 'monthly'
        automatic (bool): Suppress verbose output for automatic mode
        
    Returns:
        dict: Forecast results with predictions and summary
    """
    
    # Generate date range
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create forecast data
    forecast_data = []
    for date in dates:
        # Prepare input data for model
        input_data = {
            '_ProductID': product_id,
            'Location': location,
            'Unit Price': unit_price,
            'Unit Cost': unit_cost,
            'Weekday': date.strftime('%A'),
            'Month': date.month,
            'Day': date.day,
            'Year': date.year
        }
        
        # Get prediction
        prediction = predict_revenue(input_data)
        
        # Calculate confidence intervals
        confidence_lower, confidence_upper = calculate_confidence_intervals(
            prediction['predicted_revenue'], date
        )
        
        forecast_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'predicted_revenue': prediction['predicted_revenue'],
            'predicted_quantity': prediction['estimated_quantity'],
            'confidence_lower': confidence_lower,
            'confidence_upper': confidence_upper,
            'weekday': date.strftime('%A'),
            'is_weekend': date.weekday() >= 5,
            'is_holiday': is_holiday(date)
        })
    
    # Aggregate by frequency if needed
    if frequency != 'daily':
        forecast_data = aggregate_forecast(forecast_data, frequency)
    
    # Generate summary statistics
    summary = generate_forecast_summary(forecast_data)
    
    # Analyze patterns
    patterns = analyze_temporal_patterns(forecast_data)
    
    return {
        'forecast': forecast_data,
        'summary': summary,
        'patterns': patterns
    }
```

### Confidence Interval Calculation

```python
def calculate_confidence_intervals(base_revenue, date, confidence_level=0.95):
    """
    Calculate confidence intervals based on temporal patterns and model uncertainty.
    
    Args:
        base_revenue (float): Base revenue prediction
        date (datetime): Date for the prediction
        confidence_level (float): Confidence level (default 0.95)
        
    Returns:
        tuple: (lower_bound, upper_bound)
    """
    
    # Base uncertainty factor (model RMSE)
    base_uncertainty = 238.37  # RMSE from model evaluation
    
    # Adjust uncertainty based on temporal factors
    weekday_factor = 1.2 if date.weekday() >= 5 else 1.0  # Weekend uncertainty
    holiday_factor = 1.3 if is_holiday(date) else 1.0     # Holiday uncertainty
    
    # Calculate z-score for confidence level
    z_score = stats.norm.ppf((1 + confidence_level) / 2)
    
    # Calculate bounds
    uncertainty = base_uncertainty * weekday_factor * holiday_factor
    margin = z_score * uncertainty
    
    lower_bound = max(0, base_revenue - margin)
    upper_bound = base_revenue + margin
    
    return lower_bound, upper_bound
```

### Pattern Analysis

```python
def analyze_temporal_patterns(forecast_data):
    """
    Analyze temporal patterns in the forecast data.
    
    Args:
        forecast_data (list): List of forecast points
        
    Returns:
        dict: Pattern analysis results
    """
    
    df = pd.DataFrame(forecast_data)
    df['date'] = pd.to_datetime(df['date'])
    df['weekday_num'] = df['date'].dt.dayofweek
    
    # Weekday effect analysis
    weekday_avg = df[df['is_weekend'] == False]['predicted_revenue'].mean()
    weekend_avg = df[df['is_weekend'] == True]['predicted_revenue'].mean()
    
    if weekday_avg > weekend_avg * 1.1:
        weekday_effect = "Higher sales on weekdays"
    elif weekend_avg > weekday_avg * 1.1:
        weekday_effect = "Higher sales on weekends"
    else:
        weekday_effect = "No significant weekday pattern"
    
    # Trend analysis
    df['day_num'] = range(len(df))
    correlation = df['day_num'].corr(df['predicted_revenue'])
    
    if correlation > 0.3:
        seasonal_trend = "Growing trend"
    elif correlation < -0.3:
        seasonal_trend = "Declining trend"
    else:
        seasonal_trend = "Stable performance"
    
    # Holiday impact
    if 'is_holiday' in df.columns and df['is_holiday'].any():
        holiday_avg = df[df['is_holiday'] == True]['predicted_revenue'].mean()
        normal_avg = df[df['is_holiday'] == False]['predicted_revenue'].mean()
        
        if holiday_avg > normal_avg * 1.1:
            holiday_impact = "Positive holiday boost"
        elif holiday_avg < normal_avg * 0.9:
            holiday_impact = "Negative holiday impact"
        else:
            holiday_impact = "Neutral holiday effect"
    else:
        holiday_impact = "No holidays in forecast period"
    
    return {
        'weekday_effect': weekday_effect,
        'seasonal_trend': seasonal_trend,
        'holiday_impact': holiday_impact
    }
```

## Business Applications

### 1. Inventory Planning

Use sales forecasting to optimize inventory levels and reduce stockouts while minimizing carrying costs.

### 2. Capacity Planning

Plan production capacity, staffing levels, and resource allocation based on predicted demand patterns.

### 3. Financial Planning

Generate revenue projections for budgeting, cash flow planning, and investor reporting.

### 4. Marketing Strategy

Time marketing campaigns and promotions to align with predicted demand patterns.

## Best Practices

### 1. Regular Validation
- Compare forecasts against actual results
- Monitor forecast accuracy over time
- Adjust parameters based on performance

### 2. Confidence Intervals
- Always communicate uncertainty ranges
- Use confidence intervals for risk assessment
- Plan for both optimistic and pessimistic scenarios

### 3. Seasonal Adjustments
- Account for known seasonal patterns
- Adjust for holidays and special events
- Consider external market factors

For detailed API documentation and implementation examples, refer to the API guide and model documentation. 