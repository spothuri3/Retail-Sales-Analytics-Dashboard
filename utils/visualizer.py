import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Premium Color Palette
COLORS = {
    "primary": "#3B82F6",      # Blue
    "secondary": "#10B981",    # Emerald Green
    "accent": "#8B5CF6",       # Purple
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Rose Red
    "dark": "#1F2937",         # Dark Slate
    "light": "#F3F4F6",        # Light Gray
    "grid": "#E5E7EB"          # Muted Border
}

def plot_monthly_trend(monthly_df):
    """
    Creates a double line chart showing Revenue and Profit trends over time.
    """
    if monthly_df.empty:
        return go.Figure()
        
    fig = go.Figure()
    
    # Revenue Line
    fig.add_trace(go.Scatter(
        x=monthly_df['Month_Str'],
        y=monthly_df['Revenue'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=6, symbol='circle'),
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
    ))
    
    # Profit Line
    fig.add_trace(go.Scatter(
        x=monthly_df['Month_Str'],
        y=monthly_df['Profit'],
        mode='lines+markers',
        name='Profit',
        line=dict(color=COLORS['secondary'], width=3, dash='dash'),
        marker=dict(size=6, symbol='diamond'),
        hovertemplate='<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Monthly Revenue & Profit Trend",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=60, b=40),
        height=400
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=COLORS['grid'])
    fig.update_yaxes(showgrid=True, gridcolor=COLORS['grid'])
    
    return fig

def plot_category_sales(category_df):
    """
    Creates a horizontal bar chart showing sales by category.
    """
    if category_df.empty:
        return go.Figure()
        
    # Sort by Revenue ascending for horizontal chart display ordering (highest at the top)
    df_sorted = category_df.sort_values(by='Revenue', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['Category'],
        x=df_sorted['Revenue'],
        orientation='h',
        marker_color=COLORS['primary'],
        text=df_sorted['Revenue'].apply(lambda x: f"${x/1e3:.1f}k"),
        textposition='outside',
        hovertemplate='<b>Category: %{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Revenue by Product Category",
        xaxis_title="Revenue ($)",
        yaxis_title="Category",
        plot_bgcolor="white",
        margin=dict(l=40, r=60, t=40, b=40),
        height=350
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=COLORS['grid'])
    return fig

def plot_region_donut(region_df):
    """
    Creates a donut chart showing the percentage of sales per Region.
    """
    if region_df.empty:
        return go.Figure()
        
    fig = go.Figure(data=[go.Pie(
        labels=region_df['Region'],
        values=region_df['Revenue'],
        hole=.4,
        marker=dict(colors=[COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['warning']]),
        textinfo='percent+label',
        hovertemplate='<b>Region: %{label}</b><br>Revenue: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Revenue Contribution by Region",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    
    return fig

def plot_top_products(top_products_df):
    """
    Creates a horizontal bar chart showing the top 10 products by revenue.
    """
    if top_products_df.empty:
        return go.Figure()
        
    df_sorted = top_products_df.sort_values(by='Revenue', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_sorted['Product Name'],
        x=df_sorted['Revenue'],
        orientation='h',
        marker_color=COLORS['accent'],
        hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.2f}<br>Qty Sold: %{customdata}<extra></extra>',
        customdata=df_sorted['Quantity_Sold']
    ))
    
    fig.update_layout(
        title="Top 10 Products by Revenue",
        xaxis_title="Revenue ($)",
        yaxis_title=None,
        plot_bgcolor="white",
        margin=dict(l=150, r=40, t=40, b=40),
        height=400
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=COLORS['grid'])
    return fig

def plot_customer_segments(rfm_df):
    """
    Creates a bar chart showing the customer distribution across RFM segments.
    """
    if rfm_df.empty:
        return go.Figure()
        
    segment_counts = rfm_df['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Customer_Count']
    
    # Sort segments logically
    segment_order = ["Champions", "Loyal Customers", "Recent/New Buyers", "Need Nurturing", "At Risk", "Lost Customers"]
    segment_counts['Segment'] = pd.Categorical(segment_counts['Segment'], categories=segment_order, ordered=True)
    segment_counts = segment_counts.sort_values('Segment')
    
    fig = go.Figure()
    
    # Map segments to distinct colors
    color_map = {
        "Champions": COLORS['secondary'],
        "Loyal Customers": COLORS['primary'],
        "Recent/New Buyers": COLORS['accent'],
        "Need Nurturing": COLORS['warning'],
        "At Risk": "#F97316", # Orange
        "Lost Customers": COLORS['danger']
    }
    
    fig.add_trace(go.Bar(
        x=segment_counts['Segment'],
        y=segment_counts['Customer_Count'],
        marker_color=[color_map.get(s, COLORS['dark']) for s in segment_counts['Segment']],
        text=segment_counts['Customer_Count'],
        textposition='outside',
        hovertemplate='<b>Segment: %{x}</b><br>Count: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Customer Segments (RFM Breakdown)",
        xaxis_title="Customer Segment",
        yaxis_title="Count of Customers",
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=40, b=40),
        height=400
    )
    
    fig.update_yaxes(showgrid=True, gridcolor=COLORS['grid'])
    return fig

def plot_rfm_scatter(rfm_df):
    """
    Creates an advanced interactive scatter plot: Recency vs. Monetary, colored by Segment, sized by Frequency.
    """
    if rfm_df.empty:
        return go.Figure()
        
    # Map segments to colors
    color_map = {
        "Champions": COLORS['secondary'],
        "Loyal Customers": COLORS['primary'],
        "Recent/New Buyers": COLORS['accent'],
        "Need Nurturing": COLORS['warning'],
        "At Risk": "#F97316",
        "Lost Customers": COLORS['danger']
    }
    
    fig = px.scatter(
        rfm_df,
        x="Recency_Days",
        y="Monetary",
        color="Segment",
        size="Frequency",
        color_discrete_map=color_map,
        hover_name="Customer Name",
        hover_data={"Customer ID": True, "Recency_Days": True, "Frequency": True, "Monetary": ":$,.2f", "Segment": False},
        title="RFM Scatter: Recency vs. Monetary (Size = Purchase Frequency)"
    )
    
    fig.update_layout(
        xaxis_title="Recency (Days since last purchase - Lower is better)",
        yaxis_title="Monetary Value ($ - Higher is better)",
        plot_bgcolor="white",
        height=450,
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=COLORS['grid'])
    fig.update_yaxes(showgrid=True, gridcolor=COLORS['grid'])
    
    return fig

def plot_repeat_customers_donut(repeat_dict):
    """
    Donut chart of One-Time vs. Repeat Customers.
    """
    rate = repeat_dict['repeat_rate']
    
    fig = go.Figure(data=[go.Pie(
        labels=["Repeat Customers", "One-Time Customers"],
        values=[rate, 100 - rate],
        hole=.4,
        marker=dict(colors=[COLORS['primary'], COLORS['grid']]),
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Percentage: %{value:.1f}%<extra></extra>'
    )])
    
    fig.update_layout(
        title="Customer Loyalty: Repeat vs. One-Time Buyers",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    
    return fig

def plot_order_frequency_distribution(distribution_df):
    """
    Bar chart showing customer count by purchase count buckets.
    """
    if distribution_df.empty:
        return go.Figure()
        
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=distribution_df['Frequency_Bucket'],
        y=distribution_df['Customer_Count'],
        marker_color=COLORS['secondary'],
        text=distribution_df['Customer_Count'],
        textposition='outside',
        hovertemplate='<b>Bucket: %{x}</b><br>Customers: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Distribution of Customer Purchase Frequency",
        xaxis_title="Purchase Count Bucket",
        yaxis_title="Number of Customers",
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=40, b=40),
        height=350
    )
    
    fig.update_yaxes(showgrid=True, gridcolor=COLORS['grid'])
    return fig

def plot_product_profitability_scatter(product_df):
    """
    Scatter plot showing Product Revenue vs Profit Margin %, sized by Quantity, colored by Category.
    """
    if product_df.empty:
        return go.Figure()
        
    fig = px.scatter(
        product_df,
        x="Revenue",
        y="Profit_Margin",
        color="Category",
        size="Quantity_Sold",
        hover_name="Product Name",
        hover_data={"Product ID": True, "Category": True, "Revenue": ":$,.2f", "Profit_Margin": ":.2f%", "Quantity_Sold": True},
        title="Product Profitability vs. Revenue (Size = Qty Sold)"
    )
    
    fig.update_layout(
        xaxis_title="Revenue ($)",
        yaxis_title="Profit Margin (%)",
        plot_bgcolor="white",
        height=450,
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.22, xanchor="center", x=0.5)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=COLORS['grid'])
    fig.update_yaxes(showgrid=True, gridcolor=COLORS['grid'])
    
    # Add horizontal line at 0% margin to clearly see unprofitable items
    fig.add_hline(y=0.0, line_dash="dash", line_color=COLORS['danger'], annotation_text="Break-even", annotation_position="bottom right")
    
    return fig

def plot_sales_forecast(forecast_df):
    """
    Plots historical and forecasted sales trends with standard deviation confidence interval bands.
    """
    if forecast_df.empty:
        return go.Figure()
        
    fig = go.Figure()
    
    # Split historical vs forecast
    hist = forecast_df[forecast_df['Type'] == 'Historical']
    fore = forecast_df[forecast_df['Type'] == 'Forecast']
    
    # Connect historical to the first forecasted point
    if not hist.empty and not fore.empty:
        # Append the last row of hist to the front of fore so the line is continuous
        last_hist_row = hist.iloc[[-1]].copy()
        last_hist_row['Type'] = 'Forecast' # rename type for plotting continuity
        fore_plot = pd.concat([last_hist_row, fore], ignore_index=True)
    else:
        fore_plot = fore
        
    # Historical Line
    fig.add_trace(go.Scatter(
        x=hist['Month_Str'],
        y=hist['Revenue'],
        mode='lines+markers',
        name='Historical Sales',
        line=dict(color=COLORS['primary'], width=3),
        hovertemplate='<b>%{x} (Actual)</b><br>Revenue: $%{y:,.2f}<extra></extra>'
    ))
    
    # Forecast Line
    fig.add_trace(go.Scatter(
        x=fore_plot['Month_Str'],
        y=fore_plot['Revenue'],
        mode='lines+markers',
        name='Forecasted Trend',
        line=dict(color=COLORS['accent'], width=3, dash='dash'),
        hovertemplate='<b>%{x} (Forecast)</b><br>Projected: $%{y:,.2f}<extra></extra>'
    ))
    
    # Confidence Interval Bounds
    if not fore.empty:
        # We plot the upper bound
        fig.add_trace(go.Scatter(
            x=fore_plot['Month_Str'].tolist() + fore_plot['Month_Str'].tolist()[::-1], # x, then x reversed
            y=fore_plot['Upper_Bound'].tolist() + fore_plot['Lower_Bound'].tolist()[::-1], # upper, then lower reversed
            fill='toself',
            fillcolor='rgba(139, 92, 246, 0.15)', # Semi-transparent accent color
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name='Confidence Interval (95%)'
        ))
        
    fig.update_layout(
        title="Sales Revenue Forecast with 95% Confidence Interval",
        xaxis_title="Month",
        yaxis_title="Revenue ($)",
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=60, b=40),
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor=COLORS['grid'])
    fig.update_yaxes(showgrid=True, gridcolor=COLORS['grid'])
    
    return fig
