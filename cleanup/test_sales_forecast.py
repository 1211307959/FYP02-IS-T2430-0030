import os
import sys
import json
from datetime import datetime, timedelta
from pprint import pprint

# Add the project root to Python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sales_forecast import get_date_range, create_forecast_data, forecast_sales, forecast_multiple_products

def test_date_range():
    """Test date range generation for different frequencies"""
    print("\n=== Testing date range generation ===")
    
    # Test daily frequency
    start_date = "2023-10-01"
    end_date = "2023-10-07"
    dates = get_date_range(start_date, end_date, "D")
    print(f"Daily dates ({len(dates)} days):")
    for date in dates:
        print(f"  {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})")
    
    # Test weekly frequency
    start_date = "2023-10-01"
    end_date = "2023-11-15"
    dates = get_date_range(start_date, end_date, "W")
    print(f"\nWeekly dates ({len(dates)} weeks):")
    for date in dates:
        print(f"  {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})")
    
    # Test monthly frequency
    start_date = "2023-01-15"
    end_date = "2023-12-31"
    dates = get_date_range(start_date, end_date, "M")
    print(f"\nMonthly dates ({len(dates)} months):")
    for date in dates:
        print(f"  {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})")

def test_single_product_forecast():
    """Test forecasting for a single product"""
    print("\n=== Testing single product forecast ===")
    
    # Create test data
    base_data = {
        "_ProductID": "12",
        "Location": "North",
        "Unit Price": 100.0,
        "Unit Cost": 60.0,
        "Year": 2023,
        "Month": 10,
        "Day": 1,
        "Weekday": "Monday"
    }
    
    # Test forecasting for different frequencies
    for freq in ["D", "W", "M"]:
        # Get current date
        now = datetime.now()
        
        # Create date range for forecast
        start_date = now.strftime("%Y-%m-%d")
        end_date_obj = now + timedelta(days=30)
        end_date = end_date_obj.strftime("%Y-%m-%d")
        
        # Generate forecast
        result = forecast_sales(
            base_data=base_data,
            start_date=start_date,
            end_date=end_date,
            freq=freq,
            include_confidence=True
        )
        
        # Print results
        print(f"\nForecast results for frequency '{freq}':")
        print(f"Status: {result['status']}")
        print(f"Periods: {result['summary']['total_periods']}")
        print(f"Total Revenue: ${result['summary']['total_revenue']:.2f}")
        print(f"Total Quantity: {result['summary']['total_quantity']}")
        print(f"Total Profit: ${result['summary']['total_profit']:.2f}")
        
        # Print sample forecast
        if result['forecast'] and len(result['forecast']) > 0:
            print("\nSample forecast period:")
            sample = result['forecast'][0]
            print(f"  Date: {sample['date']} ({sample['weekday']})")
            
            if isinstance(sample['revenue'], dict):
                print(f"  Revenue: ${sample['revenue']['prediction']:.2f} (Range: ${sample['revenue']['lower_bound']:.2f} - ${sample['revenue']['upper_bound']:.2f})")
            else:
                print(f"  Revenue: ${sample['revenue']:.2f}")
                
            if isinstance(sample['quantity'], dict):
                print(f"  Quantity: {sample['quantity']['prediction']} (Range: {sample['quantity']['lower_bound']} - {sample['quantity']['upper_bound']})")
            else:
                print(f"  Quantity: {sample['quantity']}")
                
            if isinstance(sample['profit'], dict):
                print(f"  Profit: ${sample['profit']['prediction']:.2f} (Range: ${sample['profit']['lower_bound']:.2f} - ${sample['profit']['upper_bound']:.2f})")
            else:
                print(f"  Profit: ${sample['profit']:.2f}")

def test_multiple_products_forecast():
    """Test forecasting for multiple products"""
    print("\n=== Testing multiple products forecast ===")
    
    # Create test data for multiple products
    products = [
        {
            "_ProductID": "12",
            "Location": "North",
            "Unit Price": 100.0,
            "Unit Cost": 60.0,
            "Year": 2023,
            "Month": 10,
            "Day": 1,
            "Weekday": "Monday"
        },
        {
            "_ProductID": "24",
            "Location": "South",
            "Unit Price": 150.0,
            "Unit Cost": 90.0,
            "Year": 2023,
            "Month": 10,
            "Day": 1,
            "Weekday": "Monday"
        },
        {
            "_ProductID": "36",
            "Location": "East",
            "Unit Price": 200.0,
            "Unit Cost": 120.0,
            "Year": 2023,
            "Month": 10,
            "Day": 1,
            "Weekday": "Monday"
        }
    ]
    
    # Get current date
    now = datetime.now()
    
    # Create date range for forecast
    start_date = now.strftime("%Y-%m-%d")
    end_date_obj = now + timedelta(days=30)
    end_date = end_date_obj.strftime("%Y-%m-%d")
    
    # Generate forecast for multiple products
    result = forecast_multiple_products(
        product_list=products,
        start_date=start_date,
        end_date=end_date,
        freq="D"
    )
    
    # Print results
    print(f"\nMultiple products forecast results:")
    print(f"Status: {result['status']}")
    print(f"Products count: {result['metadata']['products_count']}")
    
    # Print summary for each product
    for i, product_forecast in enumerate(result['forecasts']):
        print(f"\nProduct {i+1} - ID: {product_forecast['product_id']}, Location: {product_forecast['location']}")
        print(f"  Total Revenue: ${product_forecast['summary']['total_revenue']:.2f}")
        print(f"  Total Quantity: {product_forecast['summary']['total_quantity']}")
        print(f"  Total Profit: ${product_forecast['summary']['total_profit']:.2f}")

def main():
    """Run all tests"""
    print("=== Sales Forecast Module Tests ===")
    
    # Test date range generation
    test_date_range()
    
    # Test single product forecast
    test_single_product_forecast()
    
    # Test multiple products forecast
    test_multiple_products_forecast()

if __name__ == "__main__":
    main()