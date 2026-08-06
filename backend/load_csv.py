import os
import pandas as pd
from sqlalchemy import create_engine

# Configuration
CSV_PATH = "superstore.csv"      
TABLE_NAME = "superstore"        
DATABASE_URL = "sqlite:///data.db" 

def ingest_csv_to_db():
    if not os.path.exists(CSV_PATH):
        print(f"Error: Could not find '{CSV_PATH}' in the current directory.")
        return

    print(f"Reading {CSV_PATH}...")
    
    # 1. Read the CSV file (handles common encoding variations)
    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_PATH, encoding="windows-1252")

    # 2. Clean column names for SQL & LLM safety
    # Converts "Order Date" -> "order_date", "Sub-Category" -> "sub_category"
    df.columns = (
        df.columns.str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("/", "_")
    )

    # 3. Write to Database
    engine = create_engine(DATABASE_URL)
    df.to_sql(TABLE_NAME, con=engine, if_exists="replace", index=False)

    print(f" Success! Loaded {len(df)} rows into table '{TABLE_NAME}'.")
    print("Cleaned Columns:", list(df.columns))

if __name__ == "__main__":
    ingest_csv_to_db()