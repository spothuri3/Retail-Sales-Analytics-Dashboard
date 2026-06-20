import os
import sqlite3
import pandas as pd
import subprocess
import sys

def get_db_path():
    db_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(db_dir, "retail_sales.db")

def check_and_init_db():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Initializing database...")
        db_dir = os.path.dirname(os.path.abspath(__file__))
        init_script = os.path.join(db_dir, "init_db.py")
        
        # Import and run initialize_database dynamically
        try:
            sys.path.append(db_dir)
            from init_db import initialize_database
            initialize_database()
        except ImportError:
            # Fallback to subprocess if import fails
            subprocess.run([sys.executable, init_script], check=True)
        print("Database initialized successfully.")
    else:
        print("Database already exists.")

def load_sales_data():
    """
    Connects to the SQLite database and loads the sales data into a pandas DataFrame.
    """
    check_and_init_db()
    db_path = get_db_path()
    
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM sales"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df
