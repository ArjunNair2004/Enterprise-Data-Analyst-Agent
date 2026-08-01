import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# This matches the credentials we set in our docker-compose.yml file.
DB_USER = "admin"
DB_PASSWORD = "password123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ecommerce_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def test_connection():
    """
    Tests the connection to the Postgres database and runs a sample query.
    """
    print(f"Attempting to connect to {DB_NAME} at {DB_HOST}...")
    
    try:
        # Create a SQLAlchemy engine
        engine = create_engine(DATABASE_URL)
        
        # We will use pandas to read the SQL query and easily print it as a DataFrame
        query = """
            SELECT 
                u.full_name,
                o.order_date,
                o.status,
                o.gross_amount,
                o.discount_amount
            FROM users u
            JOIN orders o ON u.user_id = o.user_id
            ORDER BY o.order_date DESC;
        """
        
        with engine.connect() as connection:
            print("Connection successful! Fetching recent orders...\n")
            
            # Execute the query and load results into a Pandas DataFrame
            df = pd.read_sql(text(query), connection)
            
            if df.empty:
                print("The database is connected, but no data was found.")
            else:
                print(df.to_markdown(index=False))
                print("\nPhase 1 Complete: Database and seed data are fully operational!")
                
    except SQLAlchemyError as e:
        print("\n❌ Connection failed! Ensure your Docker container is running.")
        print("Run: 'docker-compose up -d' in your terminal first.")
        print(f"Error Details: {e}")

if __name__ == "__main__":
    test_connection()