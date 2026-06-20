import os
import sqlite3
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_data(num_orders=12500):
    print(f"Generating {num_orders} synthetic retail sales records...")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # 1. Categories and Products definition with specific prices and profit margins
    products_db = {
        "Electronics": [
            {"id": "PROD-EL-001", "name": "Smartphone X1", "price": 850.0, "margin": 0.12},
            {"id": "PROD-EL-002", "name": "Ultrabook Air", "price": 1200.0, "margin": 0.10},
            {"id": "PROD-EL-003", "name": "Noise-Canceling Headphones", "price": 199.99, "margin": 0.25},
            {"id": "PROD-EL-004", "name": "Smart Fitness Watch", "price": 249.99, "margin": 0.20},
            {"id": "PROD-EL-005", "name": "Wireless Charging Dock", "price": 49.99, "margin": 0.35}
        ],
        "Apparel": [
            {"id": "PROD-AP-001", "name": "Premium Denim Jacket", "price": 89.99, "margin": 0.45},
            {"id": "PROD-AP-002", "name": "Organic Cotton Hoodie", "price": 59.99, "margin": 0.50},
            {"id": "PROD-AP-003", "name": "Lightweight Running Shoes", "price": 119.99, "margin": 0.35},
            {"id": "PROD-AP-004", "name": "Classic Fit Chinos", "price": 49.99, "margin": 0.40},
            {"id": "PROD-AP-005", "name": "Pack of Athletic Socks", "price": 14.99, "margin": 0.60}
        ],
        "Home & Kitchen": [
            {"id": "PROD-HK-001", "name": "Digital Air Fryer", "price": 129.99, "margin": 0.30},
            {"id": "PROD-HK-002", "name": "Programmable Drip Coffee Maker", "price": 79.99, "margin": 0.35},
            {"id": "PROD-HK-003", "name": "10-Piece Stainless Steel Cookware Set", "price": 249.99, "margin": 0.25},
            {"id": "PROD-HK-004", "name": "Ergonomic Memory Foam Pillow", "price": 39.99, "margin": 0.45},
            {"id": "PROD-HK-005", "name": "Smart Robot Vacuum", "price": 349.99, "margin": 0.22}
        ],
        "Books": [
            {"id": "PROD-BK-001", "name": "The Galactic Horizon (Sci-Fi Novel)", "price": 17.99, "margin": 0.65},
            {"id": "PROD-BK-002", "name": "Exponential Growth (Business Guide)", "price": 24.99, "margin": 0.60},
            {"id": "PROD-BK-003", "name": "Healthy Eats: 100 Recipes (Cookbook)", "price": 29.99, "margin": 0.55},
            {"id": "PROD-BK-004", "name": "Whispers in the Dark (Mystery Thriller)", "price": 14.99, "margin": 0.70},
            {"id": "PROD-BK-005", "name": "Focus: The Art of Concentration (Self-Help)", "price": 19.99, "margin": 0.65}
        ],
        "Sports & Outdoors": [
            {"id": "PROD-SO-001", "name": "Eco-Friendly Yoga Mat", "price": 39.99, "margin": 0.50},
            {"id": "PROD-SO-002", "name": "Insulated Stainless Water Bottle", "price": 34.99, "margin": 0.55},
            {"id": "PROD-SO-003", "name": "4-Person Instant Camping Tent", "price": 179.99, "margin": 0.30},
            {"id": "PROD-SO-004", "name": "Adjustable Dumbbells Set", "price": 299.99, "margin": 0.20},
            {"id": "PROD-SO-005", "name": "Heavy Duty Resistance Bands", "price": 19.99, "margin": 0.60}
        ]
    }
    
    categories = list(products_db.keys())
    regions = ["East", "West", "North", "South"]
    
    # 2. Generate customers list to ensure repeat purchases
    first_names = ["John", "Jane", "Robert", "Mary", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", 
                   "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy",
                   "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                  "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]
    
    num_customers = 1800
    customers = []
    for i in range(1, num_customers + 1):
        cust_id = f"CUST-{i:04d}"
        cust_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        cust_region = random.choice(regions)
        customers.append((cust_id, cust_name, cust_region))
        
    # We want a power-law distribution for customer purchases (few buy a lot, many buy once)
    # Generate weights for each customer
    customer_weights = np.random.exponential(scale=1.0, size=num_customers)
    customer_weights /= customer_weights.sum()
    
    # 3. Time Frame: Jan 1, 2024 to May 31, 2026
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 5, 31)
    days_range = (end_date - start_date).days
    
    # Generate list of dates with seasonal weights
    # November-December (Christmas): 1.4x
    # July-August (Summer): 1.15x
    # February (Winter dip): 0.85x
    # Weekend (Fri-Sat): 1.2x, Sun: 1.1x, Weekdays: 0.9x
    date_pool = []
    current_date = start_date
    while current_date <= end_date:
        weight = 1.0
        
        # Monthly seasonality
        month = current_date.month
        if month in [11, 12]:
            weight *= 1.4
        elif month in [7, 8]:
            weight *= 1.15
        elif month == 2:
            weight *= 0.85
            
        # Day of week seasonality
        day_of_week = current_date.weekday()
        if day_of_week in [4, 5]: # Friday, Saturday
            weight *= 1.2
        elif day_of_week == 6: # Sunday
            weight *= 1.1
        else:
            weight *= 0.9
            
        # Add positive trend over years (growing business)
        year_multiplier = 1.0 + (current_date.year - 2024) * 0.15
        weight *= year_multiplier
        
        date_pool.append((current_date, weight))
        current_date += timedelta(days=1)
        
    # Standardize weights
    dates_only, date_weights = zip(*date_pool)
    date_weights = np.array(date_weights)
    date_weights /= date_weights.sum()
    
    # 4. Generate individual orders
    data = []
    
    # Random choices based on weights
    chosen_dates = np.random.choice(dates_only, size=num_orders, p=date_weights)
    chosen_customer_indices = np.random.choice(range(num_customers), size=num_orders, p=customer_weights)
    
    for idx in range(num_orders):
        order_id = f"ORD-{chosen_dates[idx].year}-{idx+10001:05d}"
        order_date = chosen_dates[idx].strftime("%Y-%m-%d")
        
        # Customer details (consistently mapped)
        cust_id, cust_name, region = customers[chosen_customer_indices[idx]]
        
        # Select Category and Product
        category = random.choice(categories)
        product = random.choice(products_db[category])
        
        product_id = product["id"]
        product_name = product["name"]
        unit_price = product["price"]
        margin = product["margin"]
        
        # Quantity purchased: mostly 1-3, occasionally up to 10
        qty_choices = [1, 2, 3, 4, 5, 8, 10]
        qty_weights = [0.55, 0.25, 0.10, 0.05, 0.03, 0.01, 0.01]
        quantity = int(np.random.choice(qty_choices, p=qty_weights))
        
        revenue = round(quantity * unit_price, 2)
        
        # Introduce profit variation (returns, discounts, promotions)
        # 4% of orders will be heavily discounted / returned (negative profit)
        # 10% of orders will have a minor discount (reduced margin)
        # Rest will have baseline margin with small random variation
        rand_val = random.random()
        if rand_val < 0.04:  # Return/Loss
            act_margin = random.uniform(-0.30, -0.05)
        elif rand_val < 0.14:  # Promotional discount
            act_margin = margin * random.uniform(0.3, 0.7)
        else:  # Standard
            act_margin = margin * random.uniform(0.9, 1.1)
            
        profit = round(revenue * act_margin, 2)
        
        data.append({
            "Order ID": order_id,
            "Order Date": order_date,
            "Customer ID": cust_id,
            "Customer Name": cust_name,
            "Product ID": product_id,
            "Product Name": product_name,
            "Category": category,
            "Region": region,
            "Quantity": quantity,
            "Unit Price": unit_price,
            "Revenue": revenue,
            "Profit": profit
        })
        
    df = pd.DataFrame(data)
    
    # Let's inject a very small amount of missing values and duplicates to show how our processing module handles it!
    # 5. Injecting minor missing values (e.g., 5 rows with missing Region, 5 with missing Customer Name)
    missing_indices_region = np.random.choice(df.index, size=5, replace=False)
    df.loc[missing_indices_region, 'Region'] = None
    
    missing_indices_name = np.random.choice(df.index, size=5, replace=False)
    df.loc[missing_indices_name, 'Customer Name'] = None
    
    # Injecting minor duplicates (e.g., duplicate 10 random rows)
    dup_indices = np.random.choice(df.index, size=10, replace=False)
    df_dups = df.loc[dup_indices].copy()
    # Change order id slightly or keep exact duplicate? Let's keep exact duplicate to clean it.
    df = pd.concat([df, df_dups], ignore_index=True)
    
    return df

def initialize_database():
    db_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(db_dir, "retail_sales.db")
    project_dir = os.path.dirname(db_dir)
    data_dir = os.path.join(project_dir, "data")
    
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "retail_sales_sample.csv")
    
    print(f"Database will be saved to: {db_path}")
    print(f"CSV backup will be saved to: {csv_path}")
    
    # Generate the dataset
    df = generate_synthetic_data()
    
    # Write to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop table if exists to start fresh
    cursor.execute("DROP TABLE IF EXISTS sales")
    
    # Create Table
    cursor.execute("""
        CREATE TABLE sales (
            order_id TEXT,
            order_date TEXT,
            customer_id TEXT,
            customer_name TEXT,
            product_id TEXT,
            product_name TEXT,
            category TEXT,
            region TEXT,
            quantity INTEGER,
            unit_price REAL,
            revenue REAL,
            profit REAL
        )
    """)
    
    # Insert Data
    df.to_sql("sales", conn, if_exists="replace", index=False)
    
    # Also save CSV backup
    df.to_csv(csv_path, index=False)
    
    # Verify count
    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]
    print(f"Successfully loaded {count} rows into the SQLite 'sales' database.")
    
    conn.commit()
    conn.close()
    print("Database initialization completed successfully.")

if __name__ == "__main__":
    initialize_database()
