# Retail Sales Analytics Dashboard

A portfolio-grade, full-stack data analytics and predictive forecasting platform designed for retail and e-commerce business intelligence. Built using Python, Streamlit, Pandas, Plotly, SQLite, and Scikit-learn, this application processes transactional records, builds customer profiles, evaluates product performance, and forecasts future sales trends.

## 🚀 Key Features

### 1. Executive Summary Dashboard
*   **KPI Cards**: Real-time display of Total Revenue, Total Profit, Profit Margin (%), Total Orders, and Active Customers, styled with premium CSS cards.
*   **Transaction Ledger**: Live search and pagination of recent transactions.
*   **Performance Metrics**: Fast breakdown of sales by category.

### 2. In-Depth Sales Analytics
*   **Monthly Performance Trends**: Double line chart detailing revenue and profit fluctuations over time.
*   **Product Category Sales**: Horizontal bar charts displaying revenue by inventory category.
*   **Regional Contribution**: Interactive donut charts highlighting geographical sales splits.
*   **Product Leaderboards**: Highlight of top 10 products by revenue.

### 3. Customer Cohorts & RFM Segmentation
*   **Loyalty Assessment**: Metrics on repeat vs. one-time buyer ratios and order frequency distributions.
*   **Behavioral RFM Engine**: Custom Recency, Frequency, and Monetary (RFM) segmentation classifying customers into behavioral groups (e.g., *Champions*, *Loyal*, *At Risk*, *Lost*).
*   **Interactive Scatter Plot**: Advanced 3D-feeling scatter plot showing Recency vs. Monetary value, sized by purchase frequency and colored by segment.

### 4. Product Portfolio & Margin Optimization
*   **Profitability Scatter**: Plotly scatter visual mapping product revenues against profit margins, sized by quantities sold.
*   **Velocity Tracking**: Tables highlighting the top 10 best-selling items and the bottom 10 slow-velocity/least-selling products to optimize inventory turnover.

### 5. Predictive Sales Forecasting
*   **Seasonal Trend Engine**: A statistical model combining OLS Linear Regression (for growth trends) and Multiplicative Seasonal Indices (for seasonal spikes) to project monthly sales.
*   **Confidence Intervals**: 95% confidence bounds (upper and lower bands) that adapt to forecasting horizons.
*   **Metrics Panel**: Model diagnostics showing $R^2$ fit coefficient, Mean Absolute Percentage Error (MAPE), and monthly growth rate percentage.

---

## 🛠️ Technology Stack & Architecture

*   **Front-End & UI**: Streamlit (with custom responsive CSS styles, card layouts, and tabs).
*   **Data Processing**: Pandas (cohort analysis, RFM clustering) & NumPy (seasonality adjustments, standard deviation bounds).
*   **Visualizations**: Plotly Express & Plotly Graph Objects (responsive, customized color palette).
*   **Database Layer**: SQLite3 (fully relational database, auto-healing on initialization).
*   **Machine Learning**: Scikit-learn (Linear Regression for forecasting trends).

```
retail-sales-analytics/
├── requirements.txt
├── README.md
├── app.py                     # Streamlit Main App Interface
├── database/
│   ├── __init__.py
│   ├── db_manager.py         # SQLite connection & query manager
│   └── init_db.py            # Synthetic transaction generator & database loader
├── utils/
│   ├── __init__.py
│   ├── data_processor.py     # Data cleaning, RFM segmentation, KPIs
│   ├── forecasting.py        # Trend fitting and forecasting algorithms
│   └── visualizer.py         # Plotly visualization blueprints
└── data/
    └── retail_sales_sample.csv # CSV backup of the SQLite dataset
```

---

## 🗄️ Database Schema & Dataset

The database generates over **12,500 transactions** spanning January 2024 to mid-2026. The database is auto-generated on first app launch with the following schema:

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| **Order ID** | TEXT (PK) | Unique identifier for each order transaction |
| **Order Date** | TEXT | Date when the order was placed (YYYY-MM-DD) |
| **Customer ID** | TEXT | Unique identifier for the customer |
| **Customer Name** | TEXT | Full name of the customer |
| **Product ID** | TEXT | Unique identifier for the product |
| **Product Name** | TEXT | Title of the product |
| **Category** | TEXT | Product department (Electronics, Apparel, Books, etc.) |
| **Region** | TEXT | Geographical buyer region (North, South, East, West) |
| **Quantity** | INTEGER | Number of items purchased |
| **Unit Price** | REAL | Cost per single product unit |
| **Revenue** | REAL | Calculated as `Quantity * Unit Price` |
| **Profit** | REAL | Revenue adjusted for margins, discounts, and returns |

---

## 🚀 Installation & Running

1.  **Clone the Repository**
    ```bash
    git clone <your-git-repo-link>
    cd retail-sales-analytics
    ```

2.  **Create and Activate Virtual Environment**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Streamlit Dashboard**
    ```bash
    streamlit run app.py
    ```
    *Note: The SQLite database file (`retail_sales.db`) and the sample CSV data will automatically generate in your folder on the first run.*

---

## 📝 Resume Bullet Points (ATS-Friendly)

*   **Built a portfolio-grade, full-stack retail analytics web application** using Streamlit, Python, and SQLite, processing 12,000+ sales transactions to generate interactive dashboards for executive KPIs, sales trends, and product margin analyses.
*   **Engineered an RFM (Recency, Frequency, Monetary) segmentation model** using Pandas and NumPy to classify customers into behavioral cohorts (e.g., Champions, At Risk, Lost), enabling targeted customer retention campaigns.
*   **Implemented a time-series forecasting module** combining Ordinary Least Squares (OLS) Linear Regression with Multiplicative Seasonal Indices (Ratio-to-Trend) to project future monthly revenues with 95% confidence intervals, achieving model fit diagnostics.
*   **Designed a modular, clean-code software architecture** with distinct database, data processing, statistical visualization, and user interface layers, optimizing database querying and data loading speeds using Streamlit caching.
