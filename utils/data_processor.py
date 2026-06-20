import pandas as pd
import numpy as np

def clean_data(df):
    """
    Cleans the input DataFrame by handling missing values, removing duplicates,
    and converting date columns to the appropriate datetime format.
    """
    cleaned_df = df.copy()
    
    # 1. Remove duplicates
    initial_rows = len(cleaned_df)
    cleaned_df.drop_duplicates(inplace=True)
    duplicates_removed = initial_rows - len(cleaned_df)
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} duplicate rows.")
        
    # 2. Handle missing values
    # Fill missing Region with 'Unknown'
    if 'Region' in cleaned_df.columns:
        cleaned_df['Region'] = cleaned_df['Region'].fillna('Unknown')
        
    # Fill missing Customer Name with 'Guest Customer'
    if 'Customer Name' in cleaned_df.columns:
        cleaned_df['Customer Name'] = cleaned_df['Customer Name'].fillna('Guest Customer')
        
    # 3. Ensure proper data types
    if 'Order Date' in cleaned_df.columns:
        cleaned_df['Order Date'] = pd.to_datetime(cleaned_df['Order Date'])
        
    # Convert numerical columns and ensure correct types
    num_cols = ['Quantity', 'Unit Price', 'Revenue', 'Profit']
    for col in num_cols:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
            
    # Drop rows with critical null fields (like null Order ID or Category after cleaning)
    cleaned_df.dropna(subset=['Order ID', 'Category'], inplace=True)
    
    return cleaned_df

def calculate_kpis(df):
    """
    Calculates high-level Executive Summary KPIs.
    """
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_profit": 0.0,
            "total_orders": 0,
            "total_customers": 0,
            "profit_margin": 0.0
        }
        
    total_revenue = df['Revenue'].sum()
    total_profit = df['Profit'].sum()
    total_orders = df['Order ID'].nunique()
    total_customers = df['Customer ID'].nunique()
    
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    
    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "profit_margin": profit_margin
    }

def get_monthly_trends(df):
    """
    Aggregates sales data to monthly intervals for trend analysis.
    """
    if df.empty:
        return pd.DataFrame()
        
    trends_df = df.copy()
    trends_df['YearMonth'] = trends_df['Order Date'].dt.to_period('M')
    
    monthly_summary = trends_df.groupby('YearMonth').agg(
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Orders=('Order ID', 'nunique')
    ).reset_index()
    
    # Convert YearMonth back to string for easier Plotly rendering
    monthly_summary['Month_Str'] = monthly_summary['YearMonth'].dt.strftime('%b %Y')
    # Keep date object for sorting
    monthly_summary['Date_Sort'] = monthly_summary['YearMonth'].dt.to_timestamp()
    monthly_summary = monthly_summary.sort_values('Date_Sort')
    
    return monthly_summary

def get_category_sales(df):
    """
    Summarizes sales and profitability by product category.
    """
    if df.empty:
        return pd.DataFrame()
        
    category_summary = df.groupby('Category').agg(
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Quantity_Sold=('Quantity', 'sum')
    ).reset_index()
    
    category_summary['Profit_Margin'] = (category_summary['Profit'] / category_summary['Revenue'] * 100).round(2)
    return category_summary.sort_values(by='Revenue', ascending=False)

def get_region_sales(df):
    """
    Summarizes sales and profitability by geographical region.
    """
    if df.empty:
        return pd.DataFrame()
        
    region_summary = df.groupby('Region').agg(
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Orders=('Order ID', 'nunique')
    ).reset_index()
    
    region_summary['Profit_Margin'] = (region_summary['Profit'] / region_summary['Revenue'] * 100).round(2)
    return region_summary.sort_values(by='Revenue', ascending=False)

def get_top_products(df, n=10):
    """
    Retrieves the top N products by Revenue.
    """
    if df.empty:
        return pd.DataFrame()
        
    product_summary = df.groupby(['Product ID', 'Product Name', 'Category']).agg(
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Quantity_Sold=('Quantity', 'sum')
    ).reset_index()
    
    product_summary['Profit_Margin'] = (product_summary['Profit'] / product_summary['Revenue'] * 100).round(2)
    return product_summary.sort_values(by='Revenue', ascending=False).head(n)

def get_product_profitability_analysis(df):
    """
    Performs full profitability analysis on all products, categorizing them
    by profit margin and returns.
    """
    if df.empty:
        return pd.DataFrame()
        
    product_summary = df.groupby(['Product ID', 'Product Name', 'Category']).agg(
        Revenue=('Revenue', 'sum'),
        Profit=('Profit', 'sum'),
        Quantity_Sold=('Quantity', 'sum')
    ).reset_index()
    
    product_summary['Profit_Margin'] = (product_summary['Profit'] / product_summary['Revenue'] * 100).round(2)
    return product_summary.sort_values(by='Profit_Margin', ascending=False)

def get_repeat_customer_analysis(df):
    """
    Performs repeat customer analysis:
    - Calculates the percentage of repeat vs. one-time buyers
    - Distribution of order frequency per customer
    """
    if df.empty:
        return {"repeat_rate": 0.0, "distribution": pd.DataFrame()}
        
    # Count orders per customer
    customer_orders = df.groupby('Customer ID').agg(
        Order_Count=('Order ID', 'nunique'),
        Total_Revenue=('Revenue', 'sum')
    ).reset_index()
    
    total_customers = len(customer_orders)
    repeat_customers = len(customer_orders[customer_orders['Order_Count'] >= 2])
    
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0.0
    
    # Calculate frequency buckets
    # 1 order, 2 orders, 3 orders, 4 orders, 5+ orders
    def bucket_frequency(count):
        if count == 1:
            return "1 Order"
        elif count == 2:
            return "2 Orders"
        elif count == 3:
            return "3 Orders"
        elif count == 4:
            return "4 Orders"
        else:
            return "5+ Orders"
            
    customer_orders['Frequency_Bucket'] = customer_orders['Order_Count'].apply(bucket_frequency)
    
    distribution = customer_orders.groupby('Frequency_Bucket').agg(
        Customer_Count=('Customer ID', 'count'),
        Total_Revenue=('Total_Revenue', 'sum')
    ).reset_index()
    
    # Sort order for display
    order_mapping = {
        "1 Order": 1,
        "2 Orders": 2,
        "3 Orders": 3,
        "4 Orders": 4,
        "5+ Orders": 5
    }
    distribution['Sort_Order'] = distribution['Frequency_Bucket'].map(order_mapping)
    distribution = distribution.sort_values('Sort_Order').drop(columns=['Sort_Order'])
    
    return {
        "repeat_rate": repeat_rate,
        "distribution": distribution,
        "customer_orders": customer_orders
    }

def get_customer_segmentation(df):
    """
    Categorizes customers into segments using RFM principles:
    - Recency: Days since last order
    - Frequency: Total orders count
    - Monetary: Total revenue count
    """
    if df.empty:
        return pd.DataFrame()
        
    max_date = df['Order Date'].max()
    
    # Calculate R, F, M metrics per customer
    rfm = df.groupby(['Customer ID', 'Customer Name', 'Region']).agg(
        Recency_Days=('Order Date', lambda x: (max_date - x.max()).days),
        Frequency=('Order ID', 'nunique'),
        Monetary=('Revenue', 'sum')
    ).reset_index()
    
    # Segment customers using a simple rules-based approach:
    # 1. Champions: Recency <= 60 days, Frequency >= 4, Monetary >= 1000
    # 2. Loyal Customers: Recency <= 120 days, Frequency >= 3 (and not in Champions)
    # 3. New/Recent Customers: Recency <= 90 days, Frequency <= 2
    # 4. At Risk: Recency > 120 days, Frequency >= 3 (former frequent buyers)
    # 5. Lost: Recency > 180 days, Frequency <= 2
    # 6. About to Sleep: Everyone else
    
    def classify_customer(row):
        rec = row['Recency_Days']
        freq = row['Frequency']
        mon = row['Monetary']
        
        if rec <= 60 and freq >= 4 and mon >= 800:
            return "Champions"
        elif rec <= 120 and freq >= 3:
            return "Loyal Customers"
        elif rec <= 90 and freq <= 2:
            return "Recent/New Buyers"
        elif rec > 120 and freq >= 3:
            return "At Risk"
        elif rec > 180 and freq <= 2:
            return "Lost Customers"
        else:
            return "Need Nurturing"
            
    rfm['Segment'] = rfm.apply(classify_customer, axis=1)
    
    return rfm
