import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Import modular components
from database.db_manager import load_sales_data
from utils.data_processor import (
    clean_data, calculate_kpis, get_monthly_trends, 
    get_category_sales, get_region_sales, get_top_products, 
    get_repeat_customer_analysis, get_customer_segmentation, 
    get_product_profitability_analysis
)
from utils.forecasting import generate_sales_forecast
from utils.visualizer import (
    plot_monthly_trend, plot_category_sales, plot_region_donut, 
    plot_top_products, plot_customer_segments, plot_rfm_scatter, 
    plot_repeat_customers_donut, plot_order_frequency_distribution, 
    plot_product_profitability_scatter, plot_sales_forecast
)

# 1. Page Configuration
st.set_page_config(
    page_title="Retail Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS styling for premium look & feel
st.markdown("""
    <style>
    /* Main Layout Styling */
    .main {
        background-color: #F8FAFC;
    }
    
    /* Premium Title Header */
    .title-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    }
    .title-header h1 {
        color: white !important;
        margin: 0;
        font-weight: 800;
        font-size: 2.2rem;
    }
    .title-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Styled Metric Cards */
    .kpi-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    }
    .kpi-title {
        color: #64748B;
        font-size: 0.85rem;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        color: #0F172A;
        font-size: 1.75rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }
    
    /* Variations for colors */
    .card-revenue { border-left-color: #3B82F6; }
    .card-profit { border-left-color: #10B981; }
    .card-margin { border-left-color: #8B5CF6; }
    .card-orders { border-left-color: #F59E0B; }
    .card-customers { border-left-color: #0F172A; }
    
    /* Section containers */
    .chart-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Load & Cache Database Data
@st.cache_data
def get_cleaned_data():
    raw_df = load_sales_data()
    return clean_data(raw_df)

try:
    df_all = get_cleaned_data()
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.info("Attempting to reinitialize the database...")
    from database.init_db import initialize_database
    initialize_database()
    df_all = get_cleaned_data()

# 4. Sidebar Controls & Filters
st.sidebar.image("https://img.icons8.com/color/96/dashboard.png", width=60)
st.sidebar.title("Dashboard Controls")
st.sidebar.markdown("Filter sales and buyer insights dynamically.")

# Filter A: Date Range
min_date = df_all['Order Date'].min().to_pydatetime()
max_date = df_all['Order Date'].max().to_pydatetime()

st.sidebar.subheader("📅 Date Selection")
date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter B: Region
st.sidebar.subheader("🗺️ Region Selection")
regions_list = sorted(list(df_all['Region'].unique()))
selected_regions = st.sidebar.multiselect(
    "Filter by Region",
    options=regions_list,
    default=regions_list
)

# Filter C: Category
st.sidebar.subheader("📦 Category Selection")
categories_list = sorted(list(df_all['Category'].unique()))
selected_categories = st.sidebar.multiselect(
    "Filter by Category",
    options=categories_list,
    default=categories_list
)

# Apply filters to dataset
if len(date_range) == 2:
    start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_dt, end_dt = pd.to_datetime(min_date), pd.to_datetime(max_date)

filtered_df = df_all[
    (df_all['Order Date'] >= start_dt) & 
    (df_all['Order Date'] <= end_dt) &
    (df_all['Region'].isin(selected_regions)) &
    (df_all['Category'].isin(selected_categories))
]

# Sidebar Metadata Summary
st.sidebar.markdown("---")
st.sidebar.caption("💡 **About the Platform:**")
st.sidebar.caption(
    "This full-stack analytics platform is integrated with an SQLite database, "
    "modularized with clean Pandas logic, and equipped with a Scikit-learn predictive forecasting module."
)
st.sidebar.caption(f"Showing **{len(filtered_df):,}** out of **{len(df_all):,}** records.")

# 5. Header Section
st.markdown("""
    <div class='title-header'>
        <h1>Retail Sales Analytics Platform</h1>
        <p>Real-time executive summaries, customer behavior analytics, product profitability, and machine learning sales forecasts.</p>
    </div>
""", unsafe_allow_html=True)

# Check if filtered data is empty
if filtered_df.empty:
    st.warning("⚠️ No data available matching the selected filters. Please expand your selections in the sidebar.")
else:
    # 6. Calculate KPIs
    kpis = calculate_kpis(filtered_df)

    # 7. Render Dashboard Tabs
    tab_executive, tab_sales, tab_customer, tab_product, tab_forecast = st.tabs([
        "📈 Executive Summary", 
        "📊 Sales Analytics", 
        "👥 Customer Analytics", 
        "🛍️ Product Analytics", 
        "🔮 Sales Forecasting"
    ])

    # ==================== TAB 1: EXECUTIVE SUMMARY ====================
    with tab_executive:
        # KPI Card Columns
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
                <div class='kpi-card card-revenue'>
                    <div class='kpi-title'>Total Revenue</div>
                    <div class='kpi-value'>${kpis['total_revenue']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
                <div class='kpi-card card-profit'>
                    <div class='kpi-title'>Total Profit</div>
                    <div class='kpi-value'>${kpis['total_profit']:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
                <div class='kpi-card card-margin'>
                    <div class='kpi-title'>Profit Margin</div>
                    <div class='kpi-value'>{kpis['profit_margin']:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
                <div class='kpi-card card-orders'>
                    <div class='kpi-title'>Total Orders</div>
                    <div class='kpi-value'>{kpis['total_orders']:,}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with col5:
            st.markdown(f"""
                <div class='kpi-card card-customers'>
                    <div class='kpi-title'>Active Customers</div>
                    <div class='kpi-value'>{kpis['total_customers']:,}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Monthly trend chart in Executive tab
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        monthly_trends = get_monthly_trends(filtered_df)
        trend_fig = plot_monthly_trend(monthly_trends)
        st.plotly_chart(trend_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bottom columns: Recent Orders & Quick Category Summary
        sub_col1, sub_col2 = st.columns([3, 2])
        
        with sub_col1:
            st.markdown("### 🕒 Recent Transaction Records")
            recent_orders = filtered_df.sort_values(by='Order Date', ascending=False).head(10)
            st.dataframe(
                recent_orders[[
                    'Order ID', 'Order Date', 'Customer Name', 'Category', 
                    'Product Name', 'Quantity', 'Revenue', 'Profit'
                ]],
                use_container_width=True,
                hide_index=True
            )
            
        with sub_col2:
            st.markdown("### 📊 Performance Summary by Category")
            cat_summary = get_category_sales(filtered_df)
            st.dataframe(
                cat_summary.rename(columns={
                    'Revenue': 'Total Revenue ($)',
                    'Profit': 'Total Profit ($)',
                    'Quantity_Sold': 'Units Sold',
                    'Profit_Margin': 'Margin (%)'
                }),
                use_container_width=True,
                hide_index=True
            )

    # ==================== TAB 2: SALES ANALYTICS ====================
    with tab_sales:
        st.markdown("## 📊 In-Depth Sales & Revenue Performance")
        
        # Primary Trend
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.plotly_chart(plot_monthly_trend(monthly_trends), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Grid of breakdown charts
        grid_col1, grid_col2 = st.columns(2)
        
        with grid_col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            category_df = get_category_sales(filtered_df)
            st.plotly_chart(plot_category_sales(category_df), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with grid_col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            region_df = get_region_sales(filtered_df)
            st.plotly_chart(plot_region_donut(region_df), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Top Products Chart
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        top_products = get_top_products(filtered_df, n=10)
        st.plotly_chart(plot_top_products(top_products), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ==================== TAB 3: CUSTOMER ANALYTICS ====================
    with tab_customer:
        st.markdown("## 👥 Customer Cohorts & RFM Segmentation")
        
        # Top Metrics for Repeat Customers
        repeat_analysis = get_repeat_customer_analysis(filtered_df)
        
        rep_col1, rep_col2 = st.columns(2)
        with rep_col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.plotly_chart(plot_repeat_customers_donut(repeat_analysis), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with rep_col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.plotly_chart(plot_order_frequency_distribution(repeat_analysis['distribution']), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Customer Segmentation using RFM
        st.markdown("### 🏆 Customer Segmentation Profile (RFM Analysis)")
        st.markdown(
            "Customers are segmented based on their **Recency** (days since last purchase), "
            "**Frequency** (number of orders), and **Monetary** value (total spend)."
        )
        
        rfm_df = get_customer_segmentation(filtered_df)
        
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.plotly_chart(plot_customer_segments(rfm_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.plotly_chart(plot_rfm_scatter(rfm_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Segment Customer Database Details
        st.markdown("### 🔍 Customer Segmentation Directory")
        selected_segment = st.selectbox(
            "Filter Directory by Segment", 
            options=["All Segments"] + sorted(list(rfm_df['Segment'].unique()))
        )
        
        disp_rfm = rfm_df.copy()
        if selected_segment != "All Segments":
            disp_rfm = disp_rfm[disp_rfm['Segment'] == selected_segment]
            
        st.dataframe(
            disp_rfm.rename(columns={
                'Recency_Days': 'Days Since Last Order',
                'Frequency': 'Total Orders',
                'Monetary': 'Total Spend ($)',
                'Segment': 'Customer Classification'
            }).sort_values('Total Spend ($)', ascending=False),
            use_container_width=True,
            hide_index=True
        )

    # ==================== TAB 4: PRODUCT ANALYTICS ====================
    with tab_product:
        st.markdown("## 🛍️ Product Portfolio & Margin Optimization")
        
        # Product Margin scatter
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        product_profitability = get_product_profitability_analysis(filtered_df)
        st.plotly_chart(plot_product_profitability_scatter(product_profitability), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Top Sellers vs. Bottom Sellers
        p_col1, p_col2 = st.columns(2)
        
        with p_col1:
            st.markdown("### 🔥 Top 10 Best Selling Products (by Quantity)")
            top_qty_products = product_profitability.sort_values(by='Quantity_Sold', ascending=False).head(10)
            st.dataframe(
                top_qty_products.rename(columns={
                    'Quantity_Sold': 'Units Sold',
                    'Revenue': 'Revenue ($)',
                    'Profit': 'Profit ($)',
                    'Profit_Margin': 'Margin (%)'
                }),
                use_container_width=True,
                hide_index=True
            )
            
        with p_col2:
            st.markdown("### ⚠️ Bottom 10 Least Selling Products (by Quantity)")
            bottom_qty_products = product_profitability.sort_values(by='Quantity_Sold', ascending=True).head(10)
            st.dataframe(
                bottom_qty_products.rename(columns={
                    'Quantity_Sold': 'Units Sold',
                    'Revenue': 'Revenue ($)',
                    'Profit': 'Profit ($)',
                    'Profit_Margin': 'Margin (%)'
                }),
                use_container_width=True,
                hide_index=True
            )
            
        # Category margin comparison
        st.markdown("### 💡 Product Category Profitability Performance")
        st.dataframe(
            category_df.rename(columns={
                'Revenue': 'Total Revenue ($)',
                'Profit': 'Total Profit ($)',
                'Quantity_Sold': 'Units Sold',
                'Profit_Margin': 'Profit Margin (%)'
            }),
            use_container_width=True,
            hide_index=True
        )

    # ==================== TAB 5: SALES FORECASTING ====================
    with tab_forecast:
        st.markdown("## 🔮 Predictive Sales Revenue Forecasting")
        st.markdown(
            "This forecasting module uses historical sales to train an Ordinary Least Squares (OLS) "
            "Linear Trend regression model combined with dynamic Multiplicative Seasonal Indices (Ratio-to-Trend method) "
            "to project revenue with 95% confidence intervals."
        )
        
        # Control Horizon
        forecast_horizon = st.slider("Select Forecast Horizon (Months)", min_value=3, max_value=12, value=6, step=1)
        
        # Generate Forecast on full/filtered data? 
        # Forecast is most stable when trained on the full region/category dataset but restricted by selections if appropriate.
        # Let's run it on the filtered dataset to show how the forecast responds to filters!
        forecast_data, forecast_metrics = generate_sales_forecast(filtered_df, forecast_horizon)
        
        if forecast_data.empty:
            st.warning("Not enough monthly historical records to generate a forecasting model. Please expand your date range.")
        else:
            # Model KPI Cards
            f_col1, f_col2, f_col3 = st.columns(3)
            
            with f_col1:
                st.markdown(f"""
                    <div class='kpi-card card-revenue'>
                        <div class='kpi-title'>Model R-Squared Fit (R²)</div>
                        <div class='kpi-value'>{forecast_metrics['r2_score']:.4f}</div>
                    </div>
                """, unsafe_allow_html=True)
                
            with f_col2:
                st.markdown(f"""
                    <div class='kpi-card card-profit'>
                        <div class='kpi-title'>Mean Abs Pct Error (MAPE)</div>
                        <div class='kpi-value'>{forecast_metrics['mape']:.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
                
            with f_col3:
                st.markdown(f"""
                    <div class='kpi-card card-margin'>
                        <div class='kpi-title'>Avg Monthly growth trend</div>
                        <div class='kpi-value'>{forecast_metrics['growth_rate_monthly']:+.2f}%</div>
                    </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.plotly_chart(plot_sales_forecast(forecast_data), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Show Forecasted Data points table
            st.markdown("### 📅 Projected Monthly Revenue Forecast Points")
            forecast_only = forecast_data[forecast_data['Type'] == 'Forecast'].copy()
            st.dataframe(
                forecast_only[['Month_Str', 'Revenue', 'Lower_Bound', 'Upper_Bound']].rename(columns={
                    'Month_Str': 'Projected Month',
                    'Revenue': 'Point Forecast ($)',
                    'Lower_Bound': 'Lower Bound (95% CI) ($)',
                    'Upper_Bound': 'Upper Bound (95% CI) ($)'
                }),
                use_container_width=True,
                hide_index=True
            )
