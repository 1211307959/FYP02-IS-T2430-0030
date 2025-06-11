import numpy as np
import pandas as pd
import joblib
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from revenue_predictor_50_50 import load_model, preprocess, predict_revenue

def get_date_range(start_date: str, end_date: str, freq: str = 'D') -> List[datetime]:
    """
    Generate a date range for forecasting.
    
    Parameters:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - freq: Frequency for date range ('D' for daily, 'W' for weekly, 'M' for monthly)
    
    Returns:
    - List of datetime objects
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Ensure end date is after start date
        if end < start:
            raise ValueError("End date must be after start date")
        
        # Generate date range based on frequency
        if freq == 'D':
            # Daily forecasting
            days = (end - start).days + 1
            return [start + timedelta(days=i) for i in range(days)]
        elif freq == 'W':
            # Weekly forecasting (starting from Monday)
            # Adjust start to the nearest Monday if not already Monday
            start_weekday = start.weekday()
            if start_weekday > 0:  # If not Monday
                start = start - timedelta(days=start_weekday)
            
            # Generate weeks
            dates = []
            current = start
            while current <= end:
                dates.append(current)
                current += timedelta(days=7)
            return dates
        elif freq == 'M':
            # Monthly forecasting (1st of each month)
            dates = []
            current = datetime(start.year, start.month, 1)
            while current <= end:
                dates.append(current)
                # Move to next month
                if current.month == 12:
                    current = datetime(current.year + 1, 1, 1)
                else:
                    current = datetime(current.year, current.month + 1, 1)
            return dates
        else:
            raise ValueError(f"Unsupported frequency: {freq}")
    except ValueError as e:
        raise ValueError(f"Error creating date range: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error creating date range: {str(e)}")

def create_forecast_data(base_data: Dict[str, Any], date_range: List[datetime]) -> List[Dict[str, Any]]:
    """
    Create forecast data for each date in the range.
    
    Parameters:
    - base_data: Base data for prediction
    - date_range: List of dates to forecast for
    
    Returns:
    - List of data points for prediction
    """
    forecast_data = []
    
    for date in date_range:
        # Create a copy of base data
        data_point = base_data.copy()
        
        # Update date-related fields
        data_point['Year'] = date.year
        data_point['Month'] = date.month
        data_point['Day'] = date.day
        data_point['Weekday'] = date.strftime('%A')
        
        forecast_data.append(data_point)
    
    return forecast_data

def add_confidence_interval(prediction: float, uncertainty: float = 0.15) -> Dict[str, float]:
    """
    Add confidence interval to prediction.
    
    Parameters:
    - prediction: Predicted value
    - uncertainty: Uncertainty factor (default 15%)
    
    Returns:
    - Dict with prediction and confidence interval
    """
    lower_bound = max(0, prediction * (1 - uncertainty))
    upper_bound = prediction * (1 + uncertainty)
    
    return {
        'prediction': round(prediction, 2),
        'lower_bound': round(lower_bound, 2),
        'upper_bound': round(upper_bound, 2)
    }

def forecast_sales(base_data: Dict[str, Any], start_date: str, end_date: str, 
                   freq: str = 'D', include_confidence: bool = True) -> Dict[str, Any]:
    """
    Forecast sales for a date range using the ML model.
    
    Parameters:
    - base_data: Base data for prediction (product, location, price, cost)
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - freq: Frequency for forecasting ('D' for daily, 'W' for weekly, 'M' for monthly)
    - include_confidence: Whether to include confidence intervals
    
    Returns:
    - Dict with forecast results
    """
    try:
        # Generate date range
        date_range = get_date_range(start_date, end_date, freq)
        
        # Create forecast data for each date
        forecast_data = create_forecast_data(base_data, date_range)
        
        # Make predictions for each data point
        results = []
        total_revenue = 0
        total_quantity = 0
        total_profit = 0
        
        for i, data_point in enumerate(forecast_data):
            # Predict revenue for this data point using the ML model
            prediction = predict_revenue(data_point)
            
            # Handle prediction errors
            if 'error' in prediction:
                continue
            
            # Get prediction values directly from the model without adjustments
            predicted_revenue = prediction.get('predicted_revenue', 0)
            estimated_quantity = prediction.get('estimated_quantity', 0)
            profit = prediction.get('profit', 0)
            
            # Add to totals
            total_revenue += predicted_revenue
            total_quantity += estimated_quantity
            total_profit += profit
            
            # Format date for output
            date_str = date_range[i].strftime('%Y-%m-%d')
            
            # Create result with confidence interval if requested
            result = {
                'date': date_str,
                'weekday': date_range[i].strftime('%A'),
                'period_type': freq,
            }
            
            # Add prediction with confidence interval if requested
            if include_confidence:
                result['revenue'] = add_confidence_interval(predicted_revenue)
                result['quantity'] = add_confidence_interval(estimated_quantity)
                result['profit'] = add_confidence_interval(profit)
            else:
                result['revenue'] = round(predicted_revenue, 2)
                result['quantity'] = estimated_quantity
                result['profit'] = round(profit, 2)
            
            results.append(result)
        
        # Create summary
        summary = {
            'total_periods': len(results),
            'total_revenue': round(total_revenue, 2),
            'total_quantity': total_quantity,
            'total_profit': round(total_profit, 2),
            'average_revenue_per_period': round(total_revenue / max(1, len(results)), 2),
            'average_quantity_per_period': round(total_quantity / max(1, len(results)), 2),
            'average_profit_per_period': round(total_profit / max(1, len(results)), 2)
        }
        
        # Return results
        return {
            'status': 'success',
            'forecast': results,
            'summary': summary,
            'metadata': {
                'product_id': base_data.get('_ProductID'),
                'location': base_data.get('Location'),
                'unit_price': base_data.get('Unit Price'),
                'unit_cost': base_data.get('Unit Cost'),
                'start_date': start_date,
                'end_date': end_date,
                'frequency': freq
            }
        }
    except ValueError as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'status': 'error',
            'error': f"Unexpected error: {str(e)}"
        }

def forecast_multiple_products(product_list: List[Dict[str, Any]], 
                              start_date: str, end_date: str,
                              freq: str = 'D') -> Dict[str, Any]:
    """
    Forecast sales for multiple products in a date range.
    
    Parameters:
    - product_list: List of product data (each with product_id, location, price, cost)
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - freq: Frequency for forecasting ('D', 'W', 'M')
    
    Returns:
    - Dict with forecast results for each product
    """
    try:
        results = []
        
        for product_data in product_list:
            # Forecast for this product using ML model
            forecast = forecast_sales(product_data, start_date, end_date, freq, include_confidence=False)
            
            # Handle forecast errors
            if forecast.get('status') == 'error':
                continue
            
            # Add product forecast to results
            results.append({
                'product_id': product_data.get('_ProductID'),
                'location': product_data.get('Location'),
                'forecast': forecast.get('forecast', []),
                'summary': forecast.get('summary', {})
            })
        
        # Return combined results
        return {
            'status': 'success',
            'forecasts': results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'frequency': freq,
                'products_count': len(results)
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'status': 'error',
            'error': f"Error forecasting multiple products: {str(e)}"
        } 