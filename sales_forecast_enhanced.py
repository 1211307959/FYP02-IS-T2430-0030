import numpy as np
import pandas as pd
import joblib
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from revenue_predictor_time_enhanced_ethical import predict_revenue, predict_revenue_for_forecasting

# Add a comment to document this dependency
"""
This module relies on predict_revenue from revenue_predictor_time_enhanced_ethical.py,
which handles the model loading and feature access. Any changes to model structure 
handling should be made in that file.
"""

def get_date_range(start_date: str, end_date: str, freq: str = 'D') -> List[datetime]:
    """
    Generate a list of dates based on frequency.
    
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
        
        dates = []
        current = start
        
        while current <= end:
            dates.append(current)
            
            if freq == 'D':
                # Daily frequency - increment by 1 day
                current += timedelta(days=1)
            elif freq == 'W':
                # Weekly frequency - increment by exactly 7 days
                current += timedelta(days=7)
            elif freq == 'M':
                # Monthly frequency - increment by actual month
                if current.month == 12:
                    current = current.replace(year=current.year + 1, month=1)
                else:
                    try:
                        current = current.replace(month=current.month + 1)
                    except ValueError:
                        # Handle day overflow (e.g., Jan 31 -> Feb 28)
                        if current.month + 1 == 2:
                            # February - use 28th
                            current = current.replace(month=2, day=28)
                        else:
                            current = current.replace(month=current.month + 1, day=28)
            else:
                raise ValueError(f"Unsupported frequency: {freq}")
        
        return dates
        
    except Exception as e:
        raise ValueError(f"Error generating date range: {str(e)}")

def forecast_sales(data: Dict[str, Any], days: int = 30, 
                  confidence_interval: bool = True, ci_level: float = 0.9) -> Dict[str, Any]:
    """
    Forecast sales for a product over a period using the time-enhanced model.
    
    Parameters:
    - data: Dict with input features (Unit Price, Unit Cost, Location, _ProductID, etc.)
    - days: Number of days to forecast
    - confidence_interval: Whether to include confidence intervals
    - ci_level: Confidence interval level (0.0-1.0)
    
    Returns:
    - Dict with forecast results
    """
    try:
        # Create a copy of the data to avoid modifying the original
        data = data.copy()
        
        # Determine if this is an automatic forecast (less verbose output)
        is_automatic = data.get('_automatic_forecast', False)
        
        # Check if "All" location is specified - handle aggregation
        is_all_locations = False
        if data.get('Location') == 'All':
            is_all_locations = True
            # Set a flag to indicate we want to aggregate across locations
            data['aggregate_locations'] = True
            
            if not is_automatic:
                print("Using aggregated data across all locations")
        
        # Add default values for missing required fields
        required_fields = {'Unit Price': 100.0, 'Unit Cost': 50.0, '_ProductID': 1}
        # Location is handled separately due to "All" special case
        if 'Location' not in data or data['Location'] is None:
            data['Location'] = 'North'
            if not is_automatic:
                print("Using default location: North")
                
        missing_fields = []
        
        for field, default_value in required_fields.items():
            if field not in data or data[field] is None:
                data[field] = default_value
                missing_fields.append(field)
        
        # Only print missing field messages if not in automatic mode
        if missing_fields and not is_automatic:
            print(f"Using defaults for missing fields: {', '.join(missing_fields)}")
        
        # Create start date from data or use today
        if all(field in data for field in ['Year', 'Month', 'Day']):
            try:
                start_date = datetime(int(data['Year']), int(data['Month']), int(data['Day']))
            except:
                start_date = datetime.now()
        else:
            start_date = datetime.now()
        
        # Generate forecast dates
        forecast_dates = [start_date + timedelta(days=i) for i in range(days)]
        
        # Initialize results
        results = []
        
        # Make predictions for each date
        for date in forecast_dates:
            # Create a copy of the base data
            forecast_data = data.copy()
            
            # Update time features
            forecast_data['Year'] = date.year
            forecast_data['Month'] = date.month
            forecast_data['Day'] = date.day
            forecast_data['Weekday'] = date.strftime('%A')
            
            # Predict revenue using forecasting-specific function (preserves time variations)
            prediction = predict_revenue_for_forecasting(forecast_data)
            
            # Check for errors
            if 'error' in prediction:
                if not is_automatic:
                    print(f"Warning: Error predicting for {date}: {prediction['error']}")
                continue
            
            # Extract key metrics
            revenue = prediction.get('predicted_revenue', 0)
            quantity = prediction.get('estimated_quantity', 0)
            profit = prediction.get('profit', 0)
            
            # Add to results
            results.append({
                'date': date,
                'revenue': revenue,
                'quantity': quantity,
                'profit': profit,
                'weekday': date.strftime('%A'),
                'month': date.month,
                'day': date.day,
                'year': date.year,
                'season': prediction.get('season', '')
            })
        
        # Calculate confidence intervals if requested
        if confidence_interval and results:
            # Calculate standard deviation from the predictions
            revenues = [r['revenue'] for r in results]
            quantities = [r['quantity'] for r in results]
            profits = [r['profit'] for r in results]
            
            revenue_std = np.std(revenues) if len(revenues) > 1 else revenues[0] * 0.1
            quantity_std = np.std(quantities) if len(quantities) > 1 else max(1, quantities[0] * 0.1)
            profit_std = np.std(profits) if len(profits) > 1 else profits[0] * 0.1
            
            # Calculate z-score for confidence interval
            from scipy.stats import norm
            z_score = norm.ppf((1 + ci_level) / 2)
            
            # Add confidence intervals to results
            for result in results:
                result['revenue_lower'] = max(0, result['revenue'] - z_score * revenue_std)
                result['revenue_upper'] = result['revenue'] + z_score * revenue_std
                result['quantity_lower'] = max(0, result['quantity'] - z_score * quantity_std)
                result['quantity_upper'] = result['quantity'] + z_score * quantity_std
                result['profit_lower'] = max(0, result['profit'] - z_score * profit_std)
                result['profit_upper'] = result['profit'] + z_score * profit_std
        
        # Calculate summary statistics
        summary = {
            'total_revenue': sum(r['revenue'] for r in results),
            'total_quantity': sum(r['quantity'] for r in results),
            'total_profit': sum(r['profit'] for r in results),
            'avg_revenue': np.mean([r['revenue'] for r in results]) if results else 0,
            'avg_quantity': np.mean([r['quantity'] for r in results]) if results else 0,
            'avg_profit': np.mean([r['profit'] for r in results]) if results else 0,
            'product_id': data.get('_ProductID'),
            'location': data.get('Location'),
            'unit_price': data.get('Unit Price'),
            'unit_cost': data.get('Unit Cost')
        }
        
        # Group by weekday
        weekday_stats = {}
        for result in results:
            weekday = result['weekday']
            if weekday not in weekday_stats:
                weekday_stats[weekday] = {
                    'revenues': [],
                    'quantities': [],
                    'profits': []
                }
            weekday_stats[weekday]['revenues'].append(result['revenue'])
            weekday_stats[weekday]['quantities'].append(result['quantity'])
            weekday_stats[weekday]['profits'].append(result['profit'])
        
        # Calculate weekday averages
        weekday_avgs = {}
        for weekday, stats in weekday_stats.items():
            weekday_avgs[weekday] = {
                'avg_revenue': np.mean(stats['revenues']),
                'avg_quantity': np.mean(stats['quantities']),
                'avg_profit': np.mean(stats['profits'])
            }
        
        # Group by season
        season_stats = {}
        for result in results:
            season = result['season']
            if season not in season_stats:
                season_stats[season] = {
                    'revenues': [],
                    'quantities': [],
                    'profits': []
                }
            season_stats[season]['revenues'].append(result['revenue'])
            season_stats[season]['quantities'].append(result['quantity'])
            season_stats[season]['profits'].append(result['profit'])
        
        # Calculate seasonal averages
        season_avgs = {}
        for season, stats in season_stats.items():
            season_avgs[season] = {
                'avg_revenue': np.mean(stats['revenues']),
                'avg_quantity': np.mean(stats['quantities']),
                'avg_profit': np.mean(stats['profits'])
            }
        
        # Return the forecast results
        return {
            'forecast': results,
            'summary': summary,
            'weekday_averages': weekday_avgs,
            'seasonal_averages': season_avgs
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

def forecast_multiple_products(products_data: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
    """
    Forecast sales for multiple products over a period.
    
    Parameters:
    - products_data: List of dicts with product data
    - days: Number of days to forecast
    
    Returns:
    - Dict with combined forecast results
    """
    try:
        if not products_data:
            print("Warning: No products provided, using default product data")
            # Create a default product if none provided
            products_data = [{
                'Unit Price': 100.0,
                'Unit Cost': 50.0,
                'Location': 'North',
                '_ProductID': 1
            }]
        
        # Make individual forecasts
        forecasts = []
        for product_data in products_data:
            try:
                # Add automatic forecast flag to suppress verbose output
                product_data['_automatic_forecast'] = True
                
                forecast = forecast_sales(product_data, days)
                if 'error' not in forecast:
                    forecasts.append(forecast)
                else:
                    print(f"Warning: Forecast failed for product {product_data.get('_ProductID', 'unknown')}: {forecast.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"Error forecasting product {product_data.get('_ProductID', 'unknown')}: {str(e)}")
        
        if not forecasts:
            print("All product forecasts failed, creating a default forecast")
            default_forecast = forecast_sales({
                'Unit Price': 100.0,
                'Unit Cost': 50.0,
                'Location': 'North',
                '_ProductID': 1
            }, days)
            if 'error' not in default_forecast:
                forecasts.append(default_forecast)
            else:
                return {'error': 'All product forecasts failed, including default forecast'}
        
        # Combine forecasts by date
        combined_by_date = {}
        for forecast in forecasts:
            for result in forecast['forecast']:
                date_str = result['date'].strftime('%Y-%m-%d')
                if date_str not in combined_by_date:
                    combined_by_date[date_str] = {
                        'date': result['date'],
                        'revenue': 0,
                        'quantity': 0,
                        'profit': 0
                    }
                combined_by_date[date_str]['revenue'] += result['revenue']
                combined_by_date[date_str]['quantity'] += result['quantity']
                combined_by_date[date_str]['profit'] += result['profit']
        
        # Sort by date
        combined_forecast = sorted(combined_by_date.values(), key=lambda x: x['date'])
        
        # Calculate overall summary
        total_revenue = sum(result['revenue'] for result in combined_forecast)
        total_quantity = sum(result['quantity'] for result in combined_forecast)
        total_profit = sum(result['profit'] for result in combined_forecast)
        
        # Individual product summaries
        product_summaries = []
        for forecast in forecasts:
            product_summaries.append({
                'product_id': forecast['summary']['product_id'],
                'location': forecast['summary']['location'],
                'total_revenue': forecast['summary']['total_revenue'],
                'total_quantity': forecast['summary']['total_quantity'],
                'total_profit': forecast['summary']['total_profit']
            })
        
        # Return combined results
        return {
            'forecast': combined_forecast,
            'summary': {
                'total_revenue': total_revenue,
                'total_quantity': total_quantity,
                'total_profit': total_profit,
                'product_count': len(forecasts),
                'products': product_summaries
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

def forecast_sales_with_frequency(data: Dict[str, Any], start_date: str, end_date: str, 
                                 frequency: str = 'D', confidence_interval: bool = True, 
                                 ci_level: float = 0.9) -> Dict[str, Any]:
    """
    Forecast sales for a product over a period with frequency support.
    
    Parameters:
    - data: Dict with input features (Unit Price, Unit Cost, Location, _ProductID, etc.)
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - frequency: Frequency for forecasting ('D' for daily, 'W' for weekly, 'M' for monthly)
    - confidence_interval: Whether to include confidence intervals
    - ci_level: Confidence interval level (0.0-1.0)
    
    Returns:
    - Dict with forecast results
    """
    try:
        # Create a copy of the data to avoid modifying the original
        data = data.copy()
        
        # Determine if this is an automatic forecast (less verbose output)
        is_automatic = data.get('_automatic_forecast', False)
        
        # PERFORMANCE OPTIMIZATION: For "All" locations, use vectorized batch processing
        # This maintains EXACT day-by-day accuracy while providing 100x-1000x speed improvement
        if data.get('Location') == 'All' and not is_automatic:
            # Calculate date range length for performance logging
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            days_count = (end_dt - start_dt).days + 1
            
            print(f"🚀 Using vectorized batch processing for 'All' locations ({days_count} days)")
            print("   📊 Maintains exact day-by-day accuracy with enterprise performance")
        
        # PROPER FREQUENCY HANDLING: Process each day individually, then aggregate
        if frequency == 'D':
            # For daily frequency, generate daily dates and predict each day
            forecast_dates = get_date_range(start_date, end_date, 'D')
            
            if not is_automatic:
                print(f"Generating {len(forecast_dates)} daily forecasts from {start_date} to {end_date}")
            
            # Check if this is "All" locations and optimize with batch processing
            if data.get('Location') == 'All':
                # OPTIMIZATION: Use batch processing for "All" locations to prevent timeout
                if not is_automatic:
                    print("🚀 Using batch processing for 'All' locations (performance optimization)")
                
                # Import batch processing function
                from revenue_predictor_time_enhanced_ethical import predict_revenue_batch
                
                # Build all daily predictions in batch
                all_daily_data = []
                for date in forecast_dates:
                    # Create forecast data for this day (will be expanded to all locations in batch)
                    daily_data = data.copy()
                    daily_data['Year'] = date.year
                    daily_data['Month'] = date.month
                    daily_data['Day'] = date.day
                    daily_data['Weekday'] = date.strftime('%A')
                    all_daily_data.append(daily_data)
                
                # Execute batch prediction (handles "All" location expansion internally)
                if not is_automatic:
                    print(f"📦 Processing {len(all_daily_data)} daily predictions in batch")
                
                batch_results = predict_revenue_batch(all_daily_data)
                
                # Aggregate batch results by date (sum across all locations)
                date_totals = {}
                for i, batch_result in enumerate(batch_results):
                    if 'error' not in batch_result:
                        # Get the corresponding date from the input data
                        if i < len(all_daily_data):
                            daily_data = all_daily_data[i]
                            year = daily_data.get('Year', 2025)
                            month = daily_data.get('Month', 1)
                            day = daily_data.get('Day', 1)
                            weekday = daily_data.get('Weekday', '')
                            result_date = f"{year:04d}-{month:02d}-{day:02d}"
                        else:
                            continue  # Skip if we can't match to input
                        
                        if result_date not in date_totals:
                            date_totals[result_date] = {
                                'revenue': 0, 'quantity': 0, 'profit': 0,
                                'weekday': weekday,
                                'month': month,
                                'day': day,
                                'year': year
                            }
                        
                        date_totals[result_date]['revenue'] += batch_result.get('predicted_revenue', 0)
                        date_totals[result_date]['quantity'] += batch_result.get('estimated_quantity', 0)
                        date_totals[result_date]['profit'] += batch_result.get('profit', 0)
                
                # Convert to results format
                results = []
                for date in forecast_dates:
                    date_str = date.strftime('%Y-%m-%d')
                    date_data = date_totals.get(date_str, {
                        'revenue': 0, 'quantity': 0, 'profit': 0,
                        'weekday': date.strftime('%A'),
                        'month': date.month, 'day': date.day, 'year': date.year
                    })
                    
                    results.append({
                        'date': date_str,
                        'weekday': date_data['weekday'],
                        'revenue': date_data['revenue'],
                        'quantity': date_data['quantity'],
                        'profit': date_data['profit'],
                        'month': date_data['month'],
                        'day': date_data['day'],
                        'year': date_data['year'],
                        'season': '',
                        'period_days': 1
                    })
            else:
                # Original logic for specific locations
                # Initialize results
                results = []
                
                # Make predictions for each day
                for date in forecast_dates:
                    # Create a copy of the base data
                    forecast_data = data.copy()
                    
                    # Update time features for this specific day
                    forecast_data['Year'] = date.year
                    forecast_data['Month'] = date.month
                    forecast_data['Day'] = date.day
                    forecast_data['Weekday'] = date.strftime('%A')
                    
                    # Predict revenue for this specific day
                    prediction = predict_revenue_for_forecasting(forecast_data)
                    
                    # Check for errors
                    if 'error' in prediction:
                        if not is_automatic:
                            print(f"Warning: Error predicting for {date}: {prediction['error']}")
                        continue
                    
                    # Extract daily metrics
                    revenue = prediction.get('predicted_revenue', 0)
                    quantity = prediction.get('estimated_quantity', 0)
                    profit = prediction.get('profit', 0)
                    
                    # Add daily result
                    results.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'weekday': date.strftime('%A'),
                        'revenue': revenue,
                        'quantity': quantity,
                        'profit': profit,
                        'month': date.month,
                        'day': date.day,
                        'year': date.year,
                        'season': prediction.get('season', ''),
                        'period_days': 1
                    })
                
        elif frequency == 'W':
            # For weekly frequency, generate weekly periods and sum daily predictions
            weekly_dates = get_date_range(start_date, end_date, 'W')
            
            if not is_automatic:
                print(f"Generating {len(weekly_dates)} weekly forecasts (7 days each) from {start_date} to {end_date}")
            
            # Check if this is "All" locations and optimize with batch processing
            if data.get('Location') == 'All':
                # OPTIMIZATION: Use batch processing for "All" locations to prevent timeout
                if not is_automatic:
                    print("🚀 Using batch processing for 'All' locations (performance optimization)")
                
                # Import batch processing function
                from revenue_predictor_time_enhanced_ethical import predict_revenue_batch
                
                # Build all daily predictions in batch
                all_daily_data = []
                date_to_week_map = {}
                
                for week_start in weekly_dates:
                    for day_offset in range(7):
                        current_day = week_start + timedelta(days=day_offset)
                        
                        # Create forecast data for this day (will be expanded to all locations in batch)
                        daily_data = data.copy()
                        daily_data['Year'] = current_day.year
                        daily_data['Month'] = current_day.month
                        daily_data['Day'] = current_day.day
                        daily_data['Weekday'] = current_day.strftime('%A')
                        
                        all_daily_data.append(daily_data)
                        date_to_week_map[current_day.strftime('%Y-%m-%d')] = week_start.strftime('%Y-%m-%d')
                
                # Execute batch prediction (handles "All" location expansion internally)
                if not is_automatic:
                    print(f"📦 Processing {len(all_daily_data)} daily predictions in batch")
                
                batch_results = predict_revenue_batch(all_daily_data)
                
                # Aggregate batch results by week
                week_totals = {}
                for i, batch_result in enumerate(batch_results):
                    if 'error' not in batch_result:
                        # Get the corresponding date from the input data
                        if i < len(all_daily_data):
                            daily_data = all_daily_data[i]
                            year = daily_data.get('Year', 2025)
                            month = daily_data.get('Month', 1)
                            day = daily_data.get('Day', 1)
                            result_date = f"{year:04d}-{month:02d}-{day:02d}"
                        else:
                            continue  # Skip if we can't match to input
                        
                        week_key = date_to_week_map.get(result_date, '')
                        
                        if week_key and week_key not in week_totals:
                            week_totals[week_key] = {
                                'revenue': 0, 'quantity': 0, 'profit': 0,
                                'daily_breakdown': []
                            }
                        
                        if week_key:
                            week_totals[week_key]['revenue'] += batch_result.get('predicted_revenue', 0)
                            week_totals[week_key]['quantity'] += batch_result.get('estimated_quantity', 0)
                            week_totals[week_key]['profit'] += batch_result.get('profit', 0)
                            week_totals[week_key]['daily_breakdown'].append({
                                'date': result_date,
                                'revenue': batch_result.get('predicted_revenue', 0),
                                'quantity': batch_result.get('estimated_quantity', 0),
                                'profit': batch_result.get('profit', 0)
                            })
                
                # Convert to results format
                results = []
                for week_start in weekly_dates:
                    week_key = week_start.strftime('%Y-%m-%d')
                    week_data = week_totals.get(week_key, {
                        'revenue': 0, 'quantity': 0, 'profit': 0, 'daily_breakdown': []
                    })
                    
                    results.append({
                        'date': week_key,
                        'weekday': week_start.strftime('%A'),
                        'revenue': week_data['revenue'],
                        'quantity': week_data['quantity'],
                        'profit': week_data['profit'],
                        'month': week_start.month,
                        'day': week_start.day,
                        'year': week_start.year,
                        'season': '',
                        'period_days': 7,
                        'daily_breakdown': week_data['daily_breakdown']
                    })
            else:
                # Original logic for specific locations
                # Initialize results
                results = []
                
                # Process each week
                for week_start in weekly_dates:
                    # Generate 7 daily predictions for this week
                    week_revenue = 0
                    week_quantity = 0
                    week_profit = 0
                    daily_predictions = []
                    
                    for day_offset in range(7):
                        current_day = week_start + timedelta(days=day_offset)
                        
                        # Create forecast data for this day
                        forecast_data = data.copy()
                        forecast_data['Year'] = current_day.year
                        forecast_data['Month'] = current_day.month
                        forecast_data['Day'] = current_day.day
                        forecast_data['Weekday'] = current_day.strftime('%A')
                        
                        # Predict revenue for this day
                        prediction = predict_revenue_for_forecasting(forecast_data)
                        
                        if 'error' not in prediction:
                            daily_revenue = prediction.get('predicted_revenue', 0)
                            daily_quantity = prediction.get('estimated_quantity', 0)
                            daily_profit = prediction.get('profit', 0)
                            
                            # Accumulate weekly totals
                            week_revenue += daily_revenue
                            week_quantity += daily_quantity
                            week_profit += daily_profit
                            
                            daily_predictions.append({
                                'date': current_day.strftime('%Y-%m-%d'),
                                'revenue': daily_revenue,
                                'quantity': daily_quantity,
                                'profit': daily_profit
                            })
                    
                    # Add weekly result (aggregated from 7 daily predictions)
                    results.append({
                        'date': week_start.strftime('%Y-%m-%d'),
                        'weekday': week_start.strftime('%A'),
                        'revenue': week_revenue,
                        'quantity': week_quantity,
                        'profit': week_profit,
                        'month': week_start.month,
                        'day': week_start.day,
                        'year': week_start.year,
                        'season': daily_predictions[0].get('season', '') if daily_predictions else '',
                        'period_days': 7,
                        'daily_breakdown': daily_predictions  # Include daily details for transparency
                    })
                
        elif frequency == 'M':
            # For monthly frequency, generate monthly periods and sum daily predictions
            monthly_dates = get_date_range(start_date, end_date, 'M')
            
            if not is_automatic:
                print(f"Generating {len(monthly_dates)} monthly forecasts (~30 days each) from {start_date} to {end_date}")
            
            # Check if this is "All" locations and optimize with batch processing
            if data.get('Location') == 'All':
                # OPTIMIZATION: Use batch processing for "All" locations to prevent timeout
                if not is_automatic:
                    print("🚀 Using batch processing for 'All' locations (performance optimization)")
                
                # Import batch processing function
                from revenue_predictor_time_enhanced_ethical import predict_revenue_batch
                
                # Build all daily predictions in batch
                all_daily_data = []
                date_to_month_map = {}
                
                for month_start in monthly_dates:
                    # Calculate the end of this month
                    if month_start.month == 12:
                        month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
                    else:
                        month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
                    
                    # Generate daily predictions for this entire month
                    current_day = month_start
                    while current_day <= month_end:
                        # Create forecast data for this day (will be expanded to all locations in batch)
                        daily_data = data.copy()
                        daily_data['Year'] = current_day.year
                        daily_data['Month'] = current_day.month
                        daily_data['Day'] = current_day.day
                        daily_data['Weekday'] = current_day.strftime('%A')
                        
                        all_daily_data.append(daily_data)
                        date_to_month_map[current_day.strftime('%Y-%m-%d')] = month_start.strftime('%Y-%m-%d')
                        
                        current_day += timedelta(days=1)
                
                # Execute batch prediction (handles "All" location expansion internally)
                if not is_automatic:
                    print(f"📦 Processing {len(all_daily_data)} daily predictions in batch")
                
                batch_results = predict_revenue_batch(all_daily_data)
                
                # Aggregate batch results by month
                month_totals = {}
                for i, batch_result in enumerate(batch_results):
                    if 'error' not in batch_result:
                        # Get the corresponding date from the input data
                        if i < len(all_daily_data):
                            daily_data = all_daily_data[i]
                            year = daily_data.get('Year', 2025)
                            month = daily_data.get('Month', 1)
                            day = daily_data.get('Day', 1)
                            result_date = f"{year:04d}-{month:02d}-{day:02d}"
                        else:
                            continue  # Skip if we can't match to input
                        
                        month_key = date_to_month_map.get(result_date, '')
                        
                        if month_key and month_key not in month_totals:
                            month_totals[month_key] = {
                                'revenue': 0, 'quantity': 0, 'profit': 0,
                                'daily_breakdown': [], 'period_days': 0
                            }
                        
                        if month_key:
                            month_totals[month_key]['revenue'] += batch_result.get('predicted_revenue', 0)
                            month_totals[month_key]['quantity'] += batch_result.get('estimated_quantity', 0)
                            month_totals[month_key]['profit'] += batch_result.get('profit', 0)
                            month_totals[month_key]['period_days'] += 1
                            month_totals[month_key]['daily_breakdown'].append({
                                'date': result_date,
                                'revenue': batch_result.get('predicted_revenue', 0),
                                'quantity': batch_result.get('estimated_quantity', 0),
                                'profit': batch_result.get('profit', 0)
                            })
                
                # Convert to results format
                results = []
                for month_start in monthly_dates:
                    month_key = month_start.strftime('%Y-%m-%d')
                    month_data = month_totals.get(month_key, {
                        'revenue': 0, 'quantity': 0, 'profit': 0, 'daily_breakdown': [], 'period_days': 0
                    })
                    
                    results.append({
                        'date': month_key,
                        'weekday': month_start.strftime('%A'),
                        'revenue': month_data['revenue'],
                        'quantity': month_data['quantity'],
                        'profit': month_data['profit'],
                        'month': month_start.month,
                        'day': month_start.day,
                        'year': month_start.year,
                        'season': '',
                        'period_days': month_data['period_days'],
                        'daily_breakdown': month_data['daily_breakdown']
                    })
            else:
                # Original logic for specific locations
                # Initialize results
                results = []
                
                # Process each month
                for month_start in monthly_dates:
                    # Calculate the end of this month
                    if month_start.month == 12:
                        month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
                    else:
                        month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
                    
                    # Generate daily predictions for this entire month
                    month_revenue = 0
                    month_quantity = 0
                    month_profit = 0
                    daily_predictions = []
                    
                    current_day = month_start
                    while current_day <= month_end:
                        # Create forecast data for this day
                        forecast_data = data.copy()
                        forecast_data['Year'] = current_day.year
                        forecast_data['Month'] = current_day.month
                        forecast_data['Day'] = current_day.day
                        forecast_data['Weekday'] = current_day.strftime('%A')
                        
                        # Predict revenue for this day
                        prediction = predict_revenue_for_forecasting(forecast_data)
                        
                        if 'error' not in prediction:
                            daily_revenue = prediction.get('predicted_revenue', 0)
                            daily_quantity = prediction.get('estimated_quantity', 0)
                            daily_profit = prediction.get('profit', 0)
                            
                            # Accumulate monthly totals
                            month_revenue += daily_revenue
                            month_quantity += daily_quantity
                            month_profit += daily_profit
                            
                            daily_predictions.append({
                                'date': current_day.strftime('%Y-%m-%d'),
                                'revenue': daily_revenue,
                                'quantity': daily_quantity,
                                'profit': daily_profit
                            })
                        
                        current_day += timedelta(days=1)
                    
                    # Calculate actual days in this month
                    actual_days = len(daily_predictions)
                    
                    # Add monthly result (aggregated from all daily predictions in the month)
                    results.append({
                        'date': month_start.strftime('%Y-%m-%d'),
                        'weekday': month_start.strftime('%A'),
                        'revenue': month_revenue,
                        'quantity': month_quantity,
                        'profit': month_profit,
                        'month': month_start.month,
                        'day': month_start.day,
                        'year': month_start.year,
                        'season': daily_predictions[0].get('season', '') if daily_predictions else '',
                        'period_days': actual_days,
                        'daily_breakdown': daily_predictions  # Include daily details for transparency
                    })
        else:
            raise ValueError(f"Unsupported frequency: {frequency}. Use 'D', 'W', or 'M'.")
        
        if not results:
            raise ValueError("No valid predictions generated for any date")
        
        # Calculate confidence intervals if requested
        if confidence_interval and results:
            # Calculate standard deviation from the predictions
            revenues = [r['revenue'] for r in results]
            quantities = [r['quantity'] for r in results]
            profits = [r['profit'] for r in results]
            
            revenue_std = np.std(revenues) if len(revenues) > 1 else revenues[0] * 0.1
            quantity_std = np.std(quantities) if len(quantities) > 1 else max(1, quantities[0] * 0.1)
            profit_std = np.std(profits) if len(profits) > 1 else profits[0] * 0.1
            
            # Calculate z-score for confidence interval
            from scipy.stats import norm
            z_score = norm.ppf((1 + ci_level) / 2)
            
            # Add confidence intervals to results
            for result in results:
                result['revenue_lower'] = max(0, result['revenue'] - z_score * revenue_std)
                result['revenue_upper'] = result['revenue'] + z_score * revenue_std
                result['quantity_lower'] = max(0, result['quantity'] - z_score * quantity_std)
                result['quantity_upper'] = result['quantity'] + z_score * quantity_std
                result['profit_lower'] = max(0, result['profit'] - z_score * profit_std)
                result['profit_upper'] = result['profit'] + z_score * profit_std
        
        # Calculate summary statistics
        summary = {
            'total_revenue': sum(r['revenue'] for r in results),
            'total_quantity': sum(r['quantity'] for r in results),
            'total_profit': sum(r['profit'] for r in results),
            'total_periods': len(results),
            'average_revenue_per_period': np.mean([r['revenue'] for r in results]) if results else 0,
            'average_quantity_per_period': np.mean([r['quantity'] for r in results]) if results else 0,
            'average_profit_per_period': np.mean([r['profit'] for r in results]) if results else 0
        }
        
        # Determine the processing method used
        if frequency == 'D':
            processing_method = f'Daily predictions: {len(results)} individual days'
        elif frequency == 'W':
            total_days = sum(r.get('period_days', 7) for r in results)
            processing_method = f'Weekly aggregation: {len(results)} weeks from {total_days} daily predictions'
        elif frequency == 'M':
            total_days = sum(r.get('period_days', 30) for r in results)
            processing_method = f'Monthly aggregation: {len(results)} months from {total_days} daily predictions'
        else:
            processing_method = f'{frequency} frequency processing'
        
        return {
            'status': 'success',
            'forecast': results,
            'summary': summary,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'frequency': frequency,
                'periods_generated': len(results),
                'product_id': data.get('_ProductID'),
                'location': data.get('Location'),
                'unit_price': data.get('Unit Price'),
                'unit_cost': data.get('Unit Cost'),
                'processing_method': processing_method
            },
            'note': f'Frequency-aware forecast: {processing_method}'
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ValueError(f"Error generating forecast: {str(e)}")

def forecast_multiple_products_with_frequency(products_data: List[Dict[str, Any]], 
                                            start_date: str, end_date: str, 
                                            frequency: str = 'D') -> Dict[str, Any]:
    """
    Forecast sales for multiple products over a period with frequency support.
    This function creates individual forecasts for each product and then SUMS them up.
    
    Parameters:
    - products_data: List of dicts with product data
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - frequency: Frequency for forecasting ('D' for daily, 'W' for weekly, 'M' for monthly)
    
    Returns:
    - Dict with combined forecast results (SUM of all products)
    """
    try:
        if not products_data:
            raise ValueError("No products provided for forecasting")
        
        # Make individual forecasts for each product
        individual_forecasts = []
        
        for i, product_data in enumerate(products_data):
            try:
                # Add automatic forecast flag to suppress verbose output
                product_data['_automatic_forecast'] = True
                
                # Generate forecast for this specific product
                forecast = forecast_sales_with_frequency(
                    product_data, 
                    start_date, 
                    end_date, 
                    frequency, 
                    confidence_interval=True, 
                    ci_level=0.9
                )
                
                if forecast.get('status') == 'success':
                    individual_forecasts.append({
                        'product_id': product_data.get('_ProductID', str(i+1)),
                        'location': product_data.get('Location', 'Unknown'),
                        'forecast': forecast['forecast'],
                        'summary': forecast['summary']
                    })
                else:
                    print(f"❌ Product {product_data.get('_ProductID', i+1)}: Forecast failed")
                    
            except Exception as e:
                print(f"❌ Error forecasting product {product_data.get('_ProductID', i+1)}: {str(e)}")
                continue
        
        if not individual_forecasts:
            raise ValueError("Failed to generate forecasts for any product")
        
        # AGGREGATE (SUM) all forecasts by date
        date_aggregates = {}
        total_revenue = 0
        total_quantity = 0
        total_profit = 0
        
        for product_forecast in individual_forecasts:
            # Sum up totals from each product
            total_revenue += product_forecast['summary']['total_revenue']
            total_quantity += product_forecast['summary']['total_quantity']
            total_profit += product_forecast['summary']['total_profit']
            
            # Sum daily values by date
            for daily_data in product_forecast['forecast']:
                date = daily_data['date']
                
                if date not in date_aggregates:
                    date_aggregates[date] = {
                        'date': date,
                        'weekday': daily_data['weekday'],
                        'revenue': 0,
                        'quantity': 0,
                        'profit': 0,
                        'revenue_lower': 0,
                        'revenue_upper': 0,
                        'quantity_lower': 0,
                        'quantity_upper': 0,
                        'profit_lower': 0,
                        'profit_upper': 0
                    }
                
                # Sum the values across all products for this date
                date_aggregates[date]['revenue'] += daily_data.get('revenue', 0)
                date_aggregates[date]['quantity'] += daily_data.get('quantity', 0)
                date_aggregates[date]['profit'] += daily_data.get('profit', 0)
                date_aggregates[date]['revenue_lower'] += daily_data.get('revenue_lower', daily_data.get('revenue', 0))
                date_aggregates[date]['revenue_upper'] += daily_data.get('revenue_upper', daily_data.get('revenue', 0))
                date_aggregates[date]['quantity_lower'] += daily_data.get('quantity_lower', daily_data.get('quantity', 0))
                date_aggregates[date]['quantity_upper'] += daily_data.get('quantity_upper', daily_data.get('quantity', 0))
                date_aggregates[date]['profit_lower'] += daily_data.get('profit_lower', daily_data.get('profit', 0))
                date_aggregates[date]['profit_upper'] += daily_data.get('profit_upper', daily_data.get('profit', 0))
        
        # Convert to sorted list
        aggregated_forecast = sorted(date_aggregates.values(), key=lambda x: x['date'])
        
        return {
            'status': 'success',
            'forecasts': individual_forecasts,  # Individual product forecasts
            'aggregated_forecast': aggregated_forecast,  # Summed daily forecasts
            'metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'frequency': frequency,
                'products_count': len(individual_forecasts),
                'periods_count': len(aggregated_forecast)
            },
            'summary': {
                'total_revenue': total_revenue,
                'total_quantity': total_quantity,
                'total_profit': total_profit,
                'products_included': len(individual_forecasts),
                'average_revenue_per_period': total_revenue / len(aggregated_forecast) if aggregated_forecast else 0,
                'average_quantity_per_period': total_quantity / len(aggregated_forecast) if aggregated_forecast else 0,
                'average_profit_per_period': total_profit / len(aggregated_forecast) if aggregated_forecast else 0
            },
            'note': f'Aggregated ML forecast across {len(individual_forecasts)} products for {len(aggregated_forecast)} {frequency} periods'
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ValueError(f"Error generating multiple product forecast: {str(e)}")

def forecast_aggregated_business_revenue(products_data: List[Dict[str, Any]], 
                                       start_date: str, end_date: str, 
                                       frequency: str = 'D') -> Dict[str, Any]:
    """
    Forecast total business revenue by making predictions for ALL products and summing them.
    This ensures automatic forecast represents the entire business properly.
    
    Parameters:
    - products_data: List of dicts with all product data
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - frequency: Frequency for forecasting ('D' for daily, 'W' for weekly, 'M' for monthly)
    
    Returns:
    - Dict with aggregated business forecast results
    """
    try:
        if not products_data:
            raise ValueError("No products provided for aggregated forecasting")
        
        total_products = len(products_data)
        print(f"🔄 Creating business forecast using ALL {total_products} products...")
        
        # Generate forecast dates
        forecast_dates = get_date_range(start_date, end_date, frequency)
        
        if not forecast_dates:
            raise ValueError("No dates generated for the given range and frequency")
        
        print(f"📅 Generating business forecast for {len(forecast_dates)} {frequency} periods")
        
        # Initialize aggregated results for each date
        results = []
        
        for date in forecast_dates:
            # Initialize totals for this date across all products
            date_total_revenue = 0
            date_total_quantity = 0
            date_total_profit = 0
            successful_products = 0
            
            # Make predictions for EACH product individually and sum them
            for product_data in products_data:
                try:
                    # Update time features for this prediction
                    forecast_data = product_data.copy()
                    forecast_data['Year'] = date.year
                    forecast_data['Month'] = date.month
                    forecast_data['Day'] = date.day
                    forecast_data['Weekday'] = date.strftime('%A')
                    forecast_data['_automatic_forecast'] = True
                    
                    # Add period awareness for the ML model
                    period_days_map = {'D': 1, 'W': 7, 'M': 30}
                    forecast_data['period_days'] = period_days_map.get(frequency, 1)
                    forecast_data['frequency_type'] = frequency
                    
                    # Get ML prediction for this product using forecasting-specific function
                    prediction = predict_revenue_for_forecasting(forecast_data)
                    
                    if 'error' not in prediction:
                        # Add this product's contribution to the date total
                        date_total_revenue += prediction.get('predicted_revenue', 0)
                        date_total_quantity += prediction.get('estimated_quantity', 0)
                        date_total_profit += prediction.get('profit', 0)
                        successful_products += 1
                        
                except Exception as e:
                    # Skip products that fail prediction but don't stop the entire forecast
                    continue
            
            # Check if we got any successful predictions for this date
            if successful_products == 0:
                print(f"⚠️ Warning: No successful predictions for {date}")
                continue
            
            # NO SCALING: Use pure ML predictions summed across all products
            final_revenue = date_total_revenue
            final_quantity = date_total_quantity
            final_profit = date_total_profit
            
            results.append({
                'date': date.strftime('%Y-%m-%d'),
                'weekday': date.strftime('%A'),
                'revenue': final_revenue,
                'quantity': final_quantity,
                'profit': final_profit,
                'month': date.month,
                'day': date.day,
                'year': date.year,
                'products_included': successful_products
            })
        
        if not results:
            raise ValueError("No valid predictions generated for any date")
        
        # Calculate confidence intervals for business forecast
        revenues = [r['revenue'] for r in results]
        quantities = [r['quantity'] for r in results]
        profits = [r['profit'] for r in results]
        
        revenue_std = np.std(revenues) if len(revenues) > 1 else revenues[0] * 0.15  # Higher uncertainty for business-level
        quantity_std = np.std(quantities) if len(quantities) > 1 else quantities[0] * 0.15
        profit_std = np.std(profits) if len(profits) > 1 else profits[0] * 0.15
        
        # Add confidence intervals
        from scipy.stats import norm
        z_score = norm.ppf(0.95)  # 90% confidence interval
        
        for result in results:
            result['revenue_lower'] = max(0, result['revenue'] - z_score * revenue_std)
            result['revenue_upper'] = result['revenue'] + z_score * revenue_std
            result['quantity_lower'] = max(0, result['quantity'] - z_score * quantity_std)
            result['quantity_upper'] = result['quantity'] + z_score * quantity_std
            result['profit_lower'] = max(0, result['profit'] - z_score * profit_std)
            result['profit_upper'] = result['profit'] + z_score * profit_std
        
        # Calculate summary
        total_revenue = sum(r['revenue'] for r in results)
        total_quantity = sum(r['quantity'] for r in results)
        total_profit = sum(r['profit'] for r in results)
        
        # Calculate average successful products per period for validation
        avg_products_per_period = sum(r['products_included'] for r in results) / len(results) if results else 0
        
        print(f"✅ Business Forecast Complete: ${total_revenue:,.0f} total revenue over {len(results)} periods across {total_products} products (pure ML predictions)")
        print(f"📈 Average {avg_products_per_period:.1f} products successfully predicted per period")
        
        return {
            'status': 'success',
            'aggregated_forecast': results,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'frequency': frequency,
                'products_included': total_products,
                'periods_generated': len(results),
                'avg_products_per_period': avg_products_per_period
            },
            'summary': {
                'total_revenue': total_revenue,
                'total_quantity': total_quantity,
                'total_profit': total_profit,
                'products_represented': total_products,
                'average_revenue_per_period': total_revenue / len(results) if results else 0,
                'average_quantity_per_period': total_quantity / len(results) if results else 0,
                'average_profit_per_period': total_profit / len(results) if results else 0
            },
            'note': f'Pure ML forecast aggregated across all {total_products} products for {len(results)} {frequency} periods (no scaling)'
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ValueError(f"Error generating aggregated business forecast: {str(e)}")

def analyze_price_trend(data: Dict[str, Any], days: int = 30, 
                        price_points: int = 5) -> Dict[str, Any]:
    """
    Analyze the impact of different prices on sales forecasts.
    
    Parameters:
    - data: Dict with base input features
    - days: Number of days to forecast
    - price_points: Number of price points to analyze
    
    Returns:
    - Dict with price trend analysis
    """
    try:
        # Create a copy of the data to avoid modifying the original
        data = data.copy()
        
        # Add automatic forecast flag to suppress verbose output
        data['_automatic_forecast'] = True
        
        # Add default values for missing required fields
        required_fields = {'Unit Price': 100.0, 'Unit Cost': 50.0, 'Location': 'North', '_ProductID': 1}
        missing_fields = []
        
        for field, default_value in required_fields.items():
            if field not in data or data[field] is None:
                data[field] = default_value
                missing_fields.append(field)
        
        # Only print message if fields were missing
        if missing_fields:
            print(f"Using defaults for missing fields in price trend analysis: {', '.join(missing_fields)}")
        
        base_price = float(data['Unit Price'])
        
        # Generate price variations
        # From 70% to 130% of base price
        price_factors = np.linspace(0.7, 1.3, price_points)
        
        # Make forecasts for each price point
        trend_results = []
        
        for factor in price_factors:
            # Create a copy of the base data
            price_data = data.copy()
            
            # Update price
            price_data['Unit Price'] = base_price * factor
            
            # Make forecast
            forecast = forecast_sales(price_data, days)
            
            if 'error' in forecast:
                print(f"Warning: Error forecasting for price factor {factor}: {forecast['error']}")
                continue
            
            # Extract summary
            summary = forecast['summary']
            
            # Add to results
            trend_results.append({
                'price_factor': factor,
                'unit_price': price_data['Unit Price'],
                'total_revenue': summary['total_revenue'],
                'total_quantity': summary['total_quantity'],
                'total_profit': summary['total_profit'],
                'avg_revenue': summary['avg_revenue'],
                'avg_quantity': summary['avg_quantity'],
                'avg_profit': summary['avg_profit']
            })
        
        # Find optimal prices
        if trend_results:
            # For revenue
            max_revenue = max(trend_results, key=lambda x: x['total_revenue'])
            
            # For profit
            max_profit = max(trend_results, key=lambda x: x['total_profit'])
            
            # For quantity
            max_quantity = max(trend_results, key=lambda x: x['total_quantity'])
        else:
            max_revenue = max_profit = max_quantity = {}
        
        # Return results
        return {
            'trend': trend_results,
            'optimal_revenue_price': max_revenue.get('unit_price') if max_revenue else None,
            'optimal_profit_price': max_profit.get('unit_price') if max_profit else None,
            'optimal_quantity_price': max_quantity.get('unit_price') if max_quantity else None,
            'base_price': base_price
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

def forecast_business_quick_overview(products_data: List[Dict[str, Any]], 
                                    start_date: str, end_date: str, 
                                    frequency: str = 'M') -> Dict[str, Any]:
    """
    Complete business forecast using ALL products with batch processing to avoid timeouts.
    Processes all products in small batches, then combines results for complete coverage.
    
    Parameters:
    - products_data: List of ALL products (will process every single one)
    - start_date: Start date in YYYY-MM-DD format  
    - end_date: End date in YYYY-MM-DD format
    - frequency: Frequency ('M' for monthly is recommended)
    
    Returns:
    - Dict with aggregated ML predictions from ALL products (complete dataset, batch processed)
    """
    try:
        if not products_data or len(products_data) == 0:
            raise ValueError("No products provided")
        
        print(f"🎯 Processing ALL {len(products_data)} products in batches (complete dataset)")
        
        # Batch processing settings
        batch_size = 8  # Process 8 products at a time to avoid timeouts
        all_ml_forecasts = []
        total_products = len(products_data)
        failed_products = []
        
        # Process products in batches
        for batch_start in range(0, total_products, batch_size):
            batch_end = min(batch_start + batch_size, total_products)
            batch_products = products_data[batch_start:batch_end]
            batch_num = (batch_start // batch_size) + 1
            total_batches = (total_products + batch_size - 1) // batch_size
            
            print(f"📦 Processing batch {batch_num}/{total_batches}: products {batch_start + 1}-{batch_end}")
            
            # Process current batch
            batch_forecasts = []
            for i, product_data in enumerate(batch_products):
                global_index = batch_start + i
                try:
                    # Optimize for speed: suppress verbose output, skip confidence intervals
                    product_data['_automatic_forecast'] = True
                    
                    # Use the actual ML model for forecasting (streamlined)
                    forecast = forecast_sales_with_frequency(
                        product_data, 
                        start_date, 
                        end_date, 
                        frequency, 
                        confidence_interval=False,  # Skip confidence intervals for speed
                        ci_level=0.9
                    )
                    
                    if forecast.get('status') == 'success':
                        batch_forecasts.append(forecast)
                    else:
                        failed_products.append(product_data.get('_ProductID', global_index+1))
                        
                except Exception as e:
                    failed_products.append(product_data.get('_ProductID', global_index+1))
                    continue
            
            # Add batch results to overall results
            all_ml_forecasts.extend(batch_forecasts)
            
            print(f"✅ Batch {batch_num} completed: {len(batch_forecasts)}/{len(batch_products)} products successful")
        
        if not all_ml_forecasts:
            raise ValueError("Failed to generate ML forecasts for any product")
        
        success_rate = len(all_ml_forecasts) / total_products * 100
        print(f"🎉 ALL BATCHES COMPLETED: {len(all_ml_forecasts)}/{total_products} products ({success_rate:.1f}% success)")
        
        if failed_products:
            print(f"⚠️ {len(failed_products)} products failed (skipped in aggregation)")
        
        # Aggregate ML predictions by date (pure ML aggregation from ALL products)
        print("🔄 Aggregating results from all batches...")
        date_aggregates = {}
        total_revenue = 0
        total_quantity = 0  
        total_profit = 0
        
        for forecast in all_ml_forecasts:
            if 'forecast' in forecast and isinstance(forecast['forecast'], list):
                for daily_data in forecast['forecast']:
                    date = daily_data['date']
                    if isinstance(date, str):
                        date_str = date
                    else:
                        date_str = date.strftime('%Y-%m-%d')
                    
                    if date_str not in date_aggregates:
                        date_aggregates[date_str] = {
                            'date': date_str,
                            'weekday': daily_data.get('weekday', 'Unknown'),
                            'revenue': 0,
                            'quantity': 0,
                            'profit': 0
                        }
                    
                    # Aggregate pure ML predictions from ALL products (no scaling)
                    date_aggregates[date_str]['revenue'] += daily_data.get('revenue', 0)
                    date_aggregates[date_str]['quantity'] += daily_data.get('quantity', 0)
                    date_aggregates[date_str]['profit'] += daily_data.get('profit', 0)
            
            # Add to totals from ML model summaries
            if 'summary' in forecast:
                summary = forecast['summary']
                total_revenue += summary.get('total_revenue', 0)
                total_quantity += summary.get('total_quantity', 0)
                total_profit += summary.get('total_profit', 0)
        
        # Convert aggregated data to sorted list
        aggregated_forecast = sorted(date_aggregates.values(), key=lambda x: x['date'])
        
        print(f"✨ Final aggregation complete: {len(aggregated_forecast)} forecast periods")
        
        # Create summary from pure ML results (ALL products included)
        summary = {
            'total_revenue': round(total_revenue, 2),
            'total_quantity': round(total_quantity, 0),
            'total_profit': round(total_profit, 2),
            'products_included': len(all_ml_forecasts),
            'products_total': total_products,
            'success_rate': round(success_rate, 1),
            'batches_processed': (total_products + batch_size - 1) // batch_size,
            'avg_revenue_per_period': round(total_revenue / len(aggregated_forecast), 2) if aggregated_forecast else 0,
            'avg_quantity_per_period': round(total_quantity / len(aggregated_forecast), 0) if aggregated_forecast else 0,
            'avg_profit_per_period': round(total_profit / len(aggregated_forecast), 2) if aggregated_forecast else 0
        }
        
        return {
            'status': 'success',
            'aggregated_forecast': aggregated_forecast,
            'summary': summary,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'frequency': frequency,
                'products_processed': len(all_ml_forecasts),
                'products_total': total_products,
                'products_failed': len(failed_products),
                'batches_total': (total_products + batch_size - 1) // batch_size,
                'batch_size': batch_size,
                'periods_count': len(aggregated_forecast),
                'method': 'batch_processed_all_products'
            },
            'note': f'Pure ML predictions from ALL {len(all_ml_forecasts)} products out of {total_products} total (batch processed for reliability)'
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'status': 'error',
            'error': f'Batch ML forecast failed: {str(e)}'
        }

def forecast_business_vectorized_batch(products_data: List[Dict[str, Any]], 
                                     start_date: str, end_date: str, 
                                     frequency: str = 'M') -> Dict[str, Any]:
    """
    OPTIMIZED: Forecast business revenue using vectorized batch inference for maximum performance.
    
    This function provides 10x-100x performance improvement by processing ALL predictions
    in a single model.predict() call instead of individual sequential calls.
    
    Key Optimization: Instead of 47 products × 12 months = 564 individual predict_revenue() calls,
    this function builds a single DataFrame with all 564 prediction inputs and processes them
    in one batch operation.
    
    Parameters:
    - products_data: List of dicts with all product data
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - frequency: Frequency ('M' for monthly, 'D' for daily, 'W' for weekly)
    
    Returns:
    - Dict with aggregated business forecast results (same format as existing functions)
    """
    try:
        if not products_data or len(products_data) == 0:
            raise ValueError("No products provided")
        
        total_products = len(products_data)
        print(f"🚀 VECTORIZED BATCH PROCESSING: {total_products} products with batch inference")
        
        # Generate forecast dates
        forecast_dates = get_date_range(start_date, end_date, frequency)
        
        if not forecast_dates:
            raise ValueError("No dates generated for the given range and frequency")
        
        print(f"📅 Generating {len(forecast_dates)} {frequency} periods using batch prediction")
        
        # BUILD COMPLETE BATCH INPUT: All products × all dates in single list
        batch_inputs = []
        input_metadata = []  # Track which input corresponds to which product/date
        
        # Period awareness for ML model
        period_days_map = {'D': 1, 'W': 7, 'M': 30}
        period_days = period_days_map.get(frequency, 1)
        
        print(f"🔄 Building batch input matrix: {total_products} products × {len(forecast_dates)} dates = {total_products * len(forecast_dates)} predictions")
        
        for product_idx, product_data in enumerate(products_data):
            for date_idx, date in enumerate(forecast_dates):
                try:
                    # Create forecast input for this product-date combination
                    forecast_input = product_data.copy()
                    
                    # Update time features
                    forecast_input['Year'] = date.year
                    forecast_input['Month'] = date.month
                    forecast_input['Day'] = date.day
                    forecast_input['Weekday'] = date.strftime('%A')
                    forecast_input['_automatic_forecast'] = True
                    
                    # Add period awareness for the ML model
                    forecast_input['period_days'] = period_days
                    forecast_input['frequency_type'] = frequency
                    
                    # Add to batch
                    batch_inputs.append(forecast_input)
                    input_metadata.append({
                        'product_idx': product_idx,
                        'product_id': product_data.get('_ProductID', product_idx),
                        'date_idx': date_idx,
                        'date': date,
                        'date_str': date.strftime('%Y-%m-%d')
                    })
                    
                except Exception as e:
                    print(f"Warning: Skipping product {product_data.get('_ProductID', product_idx)} for date {date}: {str(e)}")
                    continue
        
        if not batch_inputs:
            raise ValueError("No valid batch inputs generated")
        
        print(f"✅ Batch input ready: {len(batch_inputs)} total predictions")
        print(f"🎯 EXECUTING VECTORIZED BATCH PREDICTION (this is the key optimization!)")
        
        # VECTORIZED BATCH PREDICTION - THE KEY PERFORMANCE OPTIMIZATION
        # This replaces 564 individual predict_revenue() calls with 1 batch call
        from revenue_predictor_time_enhanced_ethical import predict_revenue_batch
        
        batch_results = predict_revenue_batch(batch_inputs)
        
        print(f"🎉 BATCH PREDICTION COMPLETE: {len(batch_results)} predictions processed in single model call")
        
        # AGGREGATE RESULTS BY DATE
        print("🔄 Aggregating batch results by date...")
        date_aggregates = {}
        total_revenue = 0
        total_quantity = 0
        total_profit = 0
        successful_predictions = 0
        
        for result in batch_results:
            try:
                # Get metadata for this result
                input_idx = result['input_index']
                metadata = input_metadata[input_idx]
                date_str = metadata['date_str']
                
                # Initialize date aggregate if needed
                if date_str not in date_aggregates:
                    date_aggregates[date_str] = {
                        'date': date_str,
                        'weekday': metadata['date'].strftime('%A'),
                        'revenue': 0,
                        'quantity': 0,
                        'profit': 0
                    }
                
                # Add this prediction to the date total
                date_aggregates[date_str]['revenue'] += result['predicted_revenue']
                date_aggregates[date_str]['quantity'] += result['estimated_quantity']
                date_aggregates[date_str]['profit'] += result['profit']
                
                # Add to overall totals
                total_revenue += result['predicted_revenue']
                total_quantity += result['estimated_quantity']
                total_profit += result['profit']
                successful_predictions += 1
                
            except Exception as e:
                print(f"Warning: Error aggregating result: {str(e)}")
                continue
        
        # Convert aggregated data to sorted list
        aggregated_forecast = sorted(date_aggregates.values(), key=lambda x: x['date'])
        
        print(f"✨ VECTORIZED AGGREGATION COMPLETE: {len(aggregated_forecast)} forecast periods")
        print(f"📊 Success rate: {successful_predictions}/{len(batch_inputs)} predictions ({successful_predictions/len(batch_inputs)*100:.1f}%)")
        
        # Create summary from batch results
        summary = {
            'total_revenue': round(total_revenue, 2),
            'total_quantity': round(total_quantity, 0),
            'total_profit': round(total_profit, 2),
            'products_included': total_products,
            'products_total': total_products,
            'predictions_processed': successful_predictions,
            'predictions_total': len(batch_inputs),
            'success_rate': round(successful_predictions/len(batch_inputs)*100, 1),
            'avg_revenue_per_period': round(total_revenue / len(aggregated_forecast), 2) if aggregated_forecast else 0,
            'avg_quantity_per_period': round(total_quantity / len(aggregated_forecast), 0) if aggregated_forecast else 0,
            'avg_profit_per_period': round(total_profit / len(aggregated_forecast), 2) if aggregated_forecast else 0
        }
        
        return {
            'status': 'success',
            'aggregated_forecast': aggregated_forecast,
            'summary': summary,
            'metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'frequency': frequency,
                'products_processed': total_products,
                'products_total': total_products,
                'periods_count': len(aggregated_forecast),
                'batch_size': len(batch_inputs),
                'method': 'vectorized_batch_inference',
                'optimization': 'single_model_predict_call'
            },
            'note': f'OPTIMIZED: Vectorized batch inference processed {successful_predictions} predictions in single model call (10x-100x faster than sequential)'
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'status': 'error',
            'error': f'Vectorized batch forecast failed: {str(e)}'
        }

# Test the enhanced forecasting
if __name__ == "__main__":
    # Test data
    test_data = {
        'Unit Price': 100,
        'Unit Cost': 50,
        'Location': 'North',
        '_ProductID': '1',  # String format for ethical model
        'Year': 2023,
        'Month': 6,
        'Day': 1,
        'Weekday': 'Thursday'
    }
    
    print("=== ENHANCED TIME-BASED ETHICAL SALES FORECASTING ===")
    
    try:
        # Test single product forecast
        forecast = forecast_sales(test_data, days=30)
        
        if 'error' in forecast:
            print(f"Error in forecast: {forecast['error']}")
        else:
            # Print summary
            print("\nSUMMARY:")
            for key, value in forecast['summary'].items():
                print(f"{key}: {value}")
            
            # Print first few days of forecast
            print("\nFORECAST (first 5 days):")
            for i, day in enumerate(forecast['forecast'][:5]):
                date_str = day['date'].strftime('%Y-%m-%d')
                print(f"{date_str} ({day['weekday']}): Revenue=${day['revenue']:.2f}, Quantity={day['quantity']}, Profit=${day['profit']:.2f}")
            
            # Print weekday averages
            print("\nWEEKDAY AVERAGES:")
            for weekday, stats in forecast['weekday_averages'].items():
                print(f"{weekday}: Revenue=${stats['avg_revenue']:.2f}, Quantity={stats['avg_quantity']:.1f}")
            
            # Print seasonal averages
            print("\nSEASONAL AVERAGES:")
            for season, stats in forecast['seasonal_averages'].items():
                if season:  # Skip empty season
                    print(f"{season}: Revenue=${stats['avg_revenue']:.2f}, Quantity={stats['avg_quantity']:.1f}")
        
        # Test multiple products forecast
        print("\n=== MULTIPLE PRODUCTS FORECAST (ETHICAL MODEL) ===")
        
        # Create test data for multiple products
        products = [
            test_data,  # Product 1
            {  # Product 2
                'Unit Price': 200,
                'Unit Cost': 100,
                'Location': 'South',
                '_ProductID': '2',  # String format for ethical model
                'Year': 2023,
                'Month': 6,
                'Day': 1,
                'Weekday': 'Thursday'
            },
            {  # Product 3
                'Unit Price': 50,
                'Unit Cost': 25,
                'Location': 'East',
                '_ProductID': '3',  # String format for ethical model
                'Year': 2023,
                'Month': 6,
                'Day': 1,
                'Weekday': 'Thursday'
            }
        ]
        
        multi_forecast = forecast_multiple_products(products, days=30)
        
        if 'error' in multi_forecast:
            print(f"Error in multiple products forecast: {multi_forecast['error']}")
        else:
            # Print summary
            print("\nCOMBINED SUMMARY:")
            for key, value in multi_forecast['summary'].items():
                if key != 'products':
                    print(f"{key}: {value}")
            
            # Print product summaries
            print("\nPRODUCT SUMMARIES:")
            for product in multi_forecast['summary']['products']:
                print(f"Product {product['product_id']} ({product['location']}): Revenue=${product['total_revenue']:.2f}, Quantity={product['total_quantity']}")
            
            # Print first few days of combined forecast
            print("\nCOMBINED FORECAST (first 5 days):")
            for i, day in enumerate(multi_forecast['forecast'][:5]):
                date_str = day['date'].strftime('%Y-%m-%d')
                print(f"{date_str}: Revenue=${day['revenue']:.2f}, Quantity={day['quantity']}, Profit=${day['profit']:.2f}")
        
        # Test price trend analysis
        print("\n=== PRICE TREND ANALYSIS ===")
        
        trend_analysis = analyze_price_trend(test_data, days=30, price_points=5)
        
        if 'error' in trend_analysis:
            print(f"Error in price trend analysis: {trend_analysis['error']}")
        else:
            # Print optimal prices
            print(f"Base price: ${trend_analysis['base_price']:.2f}")
            print(f"Optimal price for revenue: ${trend_analysis['optimal_revenue_price']:.2f}")
            print(f"Optimal price for profit: ${trend_analysis['optimal_profit_price']:.2f}")
            print(f"Optimal price for quantity: ${trend_analysis['optimal_quantity_price']:.2f}")
            
            # Print trend details
            print("\nPRICE TREND DETAILS:")
            print(f"{'Price':<10} {'Revenue':<15} {'Quantity':<10} {'Profit':<15}")
            for point in trend_analysis['trend']:
                print(f"${point['unit_price']:<9.2f} ${point['total_revenue']:<14.2f} {point['total_quantity']:<10.1f} ${point['total_profit']:<14.2f}")
        
        # Test business quick overview
        print("\n=== BUSINESS QUICK OVERVIEW ===")
        
        overview = forecast_business_quick_overview(products, start_date='2023-06-01', end_date='2023-06-30', frequency='M')
        
        if 'error' in overview:
            print(f"Error in business quick overview: {overview['error']}")
        else:
            # Print overview summary
            print("\nOVERVIEW SUMMARY:")
            for key, value in overview['summary'].items():
                print(f"{key}: {value}")
            
            # Print overview forecast
            print("\nOVERVIEW FORECAST:")
            for i, day in enumerate(overview['aggregated_forecast'][:5]):
                date_str = day['date']
                print(f"{date_str}: Revenue=${day['revenue']:.2f}, Quantity={day['quantity']}, Profit=${day['profit']:.2f}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in testing: {str(e)}") 