import os
import sqlite3
import json
import sys

try:
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.agent import process_user_query
except ImportError as e:
    print(f"\n[❌ FAILED] Import Error: {e}")
    print("Ensure you are in the correct directory and all dependencies are installed.")
    sys.exit(1)

def run_diagnostics():
    print("=== Starting AI Analyst Backend Diagnostics ===\n")

    # ---------------------------------------------------------
    # TEST 1: SQLite Database
    # ---------------------------------------------------------
    print("1. Testing SQLite Database Connection...")
    if not os.path.exists("data.db"):
        print("   [❌ FAILED] 'data.db' not found in the current directory.")
    else:
        try:
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if tables:
                table_names = [t[0] for t in tables]
                print(f"   [✅ SUCCESS] Connected to data.db. Found tables: {table_names}")
            else:
                print("   [⚠️ WARNING] Connected to data.db, but no tables were found.")
            conn.close()
        except Exception as e:
            print(f"   [❌ FAILED] Database error: {e}")

    # ---------------------------------------------------------
    # TEST 2: LangGraph Agent
    # ---------------------------------------------------------
    print("\n2. Testing LangGraph Agent (agent.py)...")
    try:
        # We use a phrasing that encourages a multi-row response for the chart
        test_query = "Show me the total profit for each region."
        print(f"   Sending test query: '{test_query}'")
        
        response = process_user_query(test_query)
        
        if isinstance(response, list) and len(response) > 0:
            print("   [✅ SUCCESS] Agent processed query without crashing.")
            
            # Check if chart JSON was generated
            has_chart = any(r.get("type") == "chart" for r in response)
            has_text = any(r.get("type") == "text" for r in response)
            
            if has_chart and has_text:
                print("   [✅ SUCCESS] Agent successfully returned both Text and Chart configurations.")
            elif has_text:
                print("   [⚠️ WARNING] Agent returned Text, but no Chart configuration.")
            else:
                print("   [⚠️ WARNING] Agent returned an unexpected list format.")
        else:
            print("   [❌ FAILED] Agent returned an empty or invalid response.")
    except Exception as e:
        print(f"   [❌ FAILED] Agent execution error: {e}")

    # ---------------------------------------------------------
    # TEST 3: FastAPI Endpoints
    # ---------------------------------------------------------
    print("\n3. Testing FastAPI Endpoints (main.py)...")
    try:
        client = TestClient(app)
        payload = {"message": "Compare total sales by category."}
        print("   Simulating React POST request to /api/chat...")
        
        response = client.post("/api/chat", json=payload)
        
        if response.status_code == 200:
            print("   [✅ SUCCESS] Endpoint responded with HTTP 200 OK.")
            data = response.json()
            if "responses" in data:
                print("   [✅ SUCCESS] JSON payload matches the format expected by React.")
            else:
                print("   [❌ FAILED] JSON payload missing the required 'responses' key.")
        else:
            print(f"   [❌ FAILED] Endpoint returned status code {response.status_code}.")
            print(f"   Details: {response.text}")
    except Exception as e:
        print(f"   [❌ FAILED] API testing error: {e}")

    print("\n=== Diagnostics Complete ===")

if __name__ == "__main__":
    # Ensure Groq API Key is present before running
    if not os.environ.get("GROQ_API_KEY"):
        print("\n[⚠️ WARNING] GROQ_API_KEY is not set in your environment variables.")
        print("Make sure you load your .env file or export the variable before running tests.\n")
    
    run_diagnostics()