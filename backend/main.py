from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import sqlite3
import os
import shutil
import uvicorn

# Import your LangGraph wrapper function
from agent import process_user_query

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    dataset_name: Optional[str] = None

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handles CSV uploads, cleans the data, and writes it dynamically to SQLite."""
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb+") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read CSV with encoding fallback just in case
        try:
            df = pd.read_csv(temp_path)
        except UnicodeDecodeError:
            df = pd.read_csv(temp_path, encoding="latin1")

        # Clean column names for SQL safety (e.g. "Order Date" -> "order_date")
        df.columns = (
            df.columns.str.strip()
            .str.replace(" ", "_")
            .str.replace("-", "_")
            .str.lower()
        )

        # Overwrite database with the new table
        conn = sqlite3.connect("data.db")
        df.to_sql("uploaded_data", conn, if_exists="replace", index=False)
        conn.close()

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            "status": "success",
            "filename": file.filename,
            "message": "Dataset imported successfully."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Passes user messages to the LangGraph agent and returns the response."""
    try:
        agent_responses = process_user_query(request.message)
        return {"responses": agent_responses}
    except Exception as e:
        return {"responses": [{
            "role": "agent", 
            "type": "text", 
            "content": f"System Error: {str(e)}"
        }]}

# --- Run the server directly using Python ---
if __name__ == "__main__":
    print("Starting FastAPI server...")
    # This automatically reloads the server if you save changes to the code
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)