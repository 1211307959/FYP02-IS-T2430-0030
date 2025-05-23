import requests
import json

# Call the dashboard-data API
response = requests.get("http://localhost:5000/dashboard-data")
data = response.json()

# Extract and count products
products = data.get("top_products_data", [])
total_products = len(products)
product_ids = [p.get("id") for p in products]
product_ranks = {}

for p in products:
    rank = p.get("rank")
    if rank not in product_ranks:
        product_ranks[rank] = 0
    product_ranks[rank] += 1

# Print results
print(f"Total products returned: {total_products}")
print(f"Product IDs: {product_ids}")
print(f"Products by rank: {product_ranks}") 