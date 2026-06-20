import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import calendar

def generate_sales_forecast(df, forecast_months=6):
    """
    Generates a sales revenue forecast for the next `forecast_months` using a 
    combination of Linear Trend fitting and Seasonal Index multipliers.
    
    Returns:
        forecast_df (DataFrame): Historical and forecasted sales
        metrics (dict): R-squared and MAPE evaluation metrics
    """
    if df.empty:
        return pd.DataFrame(), {}
        
    # 1. Aggregate historical monthly sales
    hist_df = df.copy()
    hist_df['YearMonth'] = hist_df['Order Date'].dt.to_period('M')
    monthly_sales = hist_df.groupby('YearMonth')['Revenue'].sum().reset_index()
    monthly_sales = monthly_sales.sort_values('YearMonth').reset_index(drop=True)
    
    n_months = len(monthly_sales)
    if n_months < 6:
        # Not enough data for meaningful forecasting; fall back to simple average
        return _fallback_forecast(monthly_sales, forecast_months)
        
    # 2. Prepare X (time step: 0, 1, 2...) and y (Revenue)
    monthly_sales['Time_Index'] = np.arange(n_months)
    X = monthly_sales[['Time_Index']].values
    y = monthly_sales['Revenue'].values
    
    # 3. Fit Linear Regression to extract trend
    model = LinearRegression()
    model.fit(X, y)
    
    monthly_sales['Trend'] = model.predict(X)
    
    # 4. Calculate Seasonal Indices (Ratio-to-Trend method)
    # Seasonal index = Actual Revenue / Trend
    monthly_sales['Month_Number'] = monthly_sales['YearMonth'].dt.month
    monthly_sales['Seasonal_Ratio'] = monthly_sales['Revenue'] / monthly_sales['Trend']
    
    # Average seasonal ratio per calendar month (1-12)
    seasonal_indices = monthly_sales.groupby('Month_Number')['Seasonal_Ratio'].mean().to_dict()
    
    # Smooth seasonal index: if any month is missing in historical data, default to 1.0
    for m in range(1, 13):
        if m not in seasonal_indices:
            seasonal_indices[m] = 1.0
            
    # Calculate fit metrics on historical data
    fitted_values = monthly_sales['Trend'] * monthly_sales['Month_Number'].map(seasonal_indices)
    r2 = model.score(X, y)
    mape = np.mean(np.abs((y - fitted_values) / y)) * 100
    
    # 5. Generate forecasts for the future
    last_period = monthly_sales['YearMonth'].max()
    forecast_records = []
    
    # Calculate standard deviation of residuals for confidence intervals
    residuals = y - fitted_values
    std_residual = np.std(residuals)
    
    for i in range(1, forecast_months + 1):
        future_period = last_period + i
        future_time_index = n_months + i - 1
        future_month_num = future_period.month
        
        # Calculate base trend
        trend_pred = float(model.predict(np.array([[future_time_index]]))[0])
        # Apply seasonal multiplier
        seasonal_mult = seasonal_indices[future_month_num]
        forecast_val = max(0.0, trend_pred * seasonal_mult)
        
        # Add 95% confidence bounds (approx ± 1.96 * std_residual)
        # Increasing uncertainty over time: multiply std by a growing factor
        uncertainty_factor = np.sqrt(1 + (i * 0.15))
        upper_bound = round(forecast_val + (1.96 * std_residual * uncertainty_factor), 2)
        lower_bound = round(max(0.0, forecast_val - (1.96 * std_residual * uncertainty_factor)), 2)
        
        forecast_records.append({
            "YearMonth": future_period,
            "Month_Str": future_period.strftime("%b %Y"),
            "Date_Sort": future_period.to_timestamp(),
            "Revenue": round(forecast_val, 2),
            "Lower_Bound": lower_bound,
            "Upper_Bound": upper_bound,
            "Type": "Forecast"
        })
        
    forecast_out = pd.DataFrame(forecast_records)
    
    # 6. Format historical data to match output columns
    hist_out = pd.DataFrame({
        "YearMonth": monthly_sales['YearMonth'],
        "Month_Str": monthly_sales['YearMonth'].dt.strftime("%b %Y"),
        "Date_Sort": monthly_sales['YearMonth'].dt.to_timestamp(),
        "Revenue": monthly_sales['Revenue'].round(2),
        "Lower_Bound": monthly_sales['Revenue'].round(2),
        "Upper_Bound": monthly_sales['Revenue'].round(2),
        "Type": "Historical"
    })
    
    # Combine historical and forecast
    combined_df = pd.concat([hist_out, forecast_out], ignore_index=True)
    combined_df = combined_df.sort_values('Date_Sort').reset_index(drop=True)
    
    metrics = {
        "r2_score": r2,
        "mape": mape,
        "growth_rate_monthly": float(model.coef_[0] / y.mean() * 100) # percentage growth per month relative to mean
    }
    
    return combined_df, metrics

def _fallback_forecast(monthly_sales, forecast_months):
    """
    Fallback method in case we have very few historical months.
    """
    avg_sales = monthly_sales['Revenue'].mean() if not monthly_sales.empty else 1000.0
    last_period = monthly_sales['YearMonth'].max() if not monthly_sales.empty else pd.Period(datetime.now(), freq='M')
    
    forecast_records = []
    for i in range(1, forecast_months + 1):
        future_period = last_period + i
        forecast_records.append({
            "YearMonth": future_period,
            "Month_Str": future_period.strftime("%b %Y"),
            "Date_Sort": future_period.to_timestamp(),
            "Revenue": round(avg_sales, 2),
            "Lower_Bound": round(avg_sales * 0.8, 2),
            "Upper_Bound": round(avg_sales * 1.2, 2),
            "Type": "Forecast"
        })
        
    forecast_out = pd.DataFrame(forecast_records)
    
    hist_out = pd.DataFrame({
        "YearMonth": monthly_sales['YearMonth'],
        "Month_Str": monthly_sales['YearMonth'].dt.strftime("%b %Y"),
        "Date_Sort": monthly_sales['YearMonth'].dt.to_timestamp(),
        "Revenue": monthly_sales['Revenue'].round(2),
        "Lower_Bound": monthly_sales['Revenue'].round(2),
        "Upper_Bound": monthly_sales['Revenue'].round(2),
        "Type": "Historical"
    }) if not monthly_sales.empty else pd.DataFrame()
    
    combined = pd.concat([hist_out, forecast_out], ignore_index=True)
    metrics = {
        "r2_score": 0.0,
        "mape": 0.0,
        "growth_rate_monthly": 0.0
    }
    return combined, metrics
