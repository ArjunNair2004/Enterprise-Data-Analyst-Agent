import os
import json
import sqlite3
import pandas as pd
from typing import TypedDict, Optional, Dict, Any, List
from sqlalchemy import create_engine, text

# FREE TIER IMPORTS
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

# --- DATABASE CONNECTION (SQLite) ---
DATABASE_URL = "sqlite:///data.db"
engine = create_engine(DATABASE_URL)

# --- MODEL INITIALIZATION ---
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


# --- AGENT STATE SPECIFICATION ---
class AgentState(TypedDict):
    """The state object that gets passed through the graph workflow."""
    question: str
    schema_context: str
    sql_query: str
    is_safe: bool
    sql_error: Optional[str]
    data_result: str
    raw_data: List[Dict[str, Any]] 
    iteration_count: int
    chart_config: Optional[Dict[str, Any]]
    final_response: str


# --- DYNAMIC SCHEMA READER ---
def get_current_db_schema(db_path="data.db") -> str:
    """Dynamically reads table names and column definitions directly from SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema_descriptions = []
        for table_tuple in tables:
            table_name = table_tuple[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            schema_descriptions.append(f"Table '{table_name}' has columns: {', '.join(col_names)}")
        
        conn.close()
        
        if not schema_descriptions:
            return "No tables found in database."
        return "\n".join(schema_descriptions)
    except Exception as e:
        return f"Error reading database schema: {e}"


# --- WORKFLOW NODES ---

def retrieve_schema(state: AgentState):
    """Retrieves current database tables and columns dynamically."""
    schema_context = get_current_db_schema()
    return {"schema_context": schema_context}


def generate_sql(state: AgentState):
    """Generates or fixes the SQLite query based on schema context and previous errors."""
    question = state["question"]
    error = state.get("sql_error", "")
    iteration = state.get("iteration_count", 0)
    schema_context = state.get("schema_context", "")

    system_prompt = f"""You are an expert SQLite Data Analyst. Your job is to write a syntactically correct SQLite query to answer the user's question.

Here is the database schema:
{schema_context}

Rules:
1. Return ONLY the raw SQL query. Do not include markdown formatting, backticks (```), or explanations.
2. For visual comparisons or categorical questions (e.g., "by category", "for each region"), group by the category and aggregate metrics WITHOUT using 'LIMIT 1', so we can chart all categories."""

    # Feed previous execution errors back to the LLM for self-correction
    if error:
        system_prompt += f"\n\nWARNING: Your previous query failed with this error:\n{error}\nRewrite the query to fix it."
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
    
    response = llm.invoke(messages)
    clean_sql = response.content.replace("```sql", "").replace("```", "").strip()
    
    return {
        "sql_query": clean_sql, 
        "iteration_count": iteration + 1
    }


def validate_sql(state: AgentState):
    """Security Guardrail: Intercepts and blocks destructive or non-READ queries."""
    sql = state["sql_query"].upper()
    forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE"]
    
    # Must start with SELECT or CTE (WITH)
    if not (sql.startswith("SELECT") or sql.startswith("WITH")):
        return {
            "is_safe": False,
            "sql_error": "Security Violation: Only SELECT and CTE (WITH) queries are permitted."
        }
    
    for kw in forbidden_keywords:
        if f" {kw} " in f" {sql} " or sql.startswith(kw):
            return {
                "is_safe": False,
                "sql_error": f"Security Violation: Command '{kw}' is strictly prohibited."
            }
            
    return {"is_safe": True, "sql_error": ""}


def execute_sql(state: AgentState):
    """Executes the safe SQL query against SQLite data.db."""
    query = state["sql_query"]
    print(f"\n[Executing SQL]:\n{query}")
    
    try:
        with engine.connect() as connection:
            df = pd.read_sql(text(query), connection)
            result_str = df.to_markdown(index=False) if not df.empty else "No results found."
            
            raw_data = df.to_dict(orient="records") if not df.empty else []
            
            return {"data_result": result_str, "raw_data": raw_data, "sql_error": ""}
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n[SQL Error Caught]: {error_msg}")
        return {"sql_error": error_msg, "data_result": "", "raw_data": []}


def generate_chart_config(state: AgentState):
    """Generates chart metadata if the dataset warrants visualization."""
    data = state.get("data_result", "")
    if not data or "No results found" in data or state.get("sql_error"):
        return {"chart_config": None}

    prompt = f"""Analyze the user question and SQL query results.
Only set "should_render": true IF the data contains AT LEAST ONE NUMERIC column (e.g., total sales, profit, count, average) that can be plotted on an axis.
Do NOT generate a chart for plain list results, distinct text values, or single text responses.

User Question: "{state['question']}"
Data Results:
{data}

Return JSON with this structure:
{{
  "should_render": true/false,
  "chart_type": "bar" | "line" | "pie",
  "x_axis": "column_name",
  "y_axis": "column_name",
  "title": "Chart Title"
}}
Return ONLY valid JSON with no markdown tags or explanations."""

    try:
        response = llm.invoke(prompt)
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        config = json.loads(clean_json)
        return {"chart_config": config if config.get("should_render") else None}
    except Exception:
        return {"chart_config": None}


def generate_english_response(state: AgentState):
    """Translates raw query results into a clear, executive-friendly response."""
    question = state["question"]
    raw_data = state.get("data_result", "")
    error = state.get("sql_error", "")
    
    if error:
        return {"final_response": f"I couldn't complete your request due to an error: {error}"}
    
    prompt = f"""You are a professional Data Analyst presenting findings to a non-technical manager.
The user asked: "{question}"

Here are the query results from the database:
{raw_data}

Write a direct, clear, natural language answer in proper English. 
- Do not mention SQL, database column names, code, or technical implementation details.
- State key insights and findings clearly in 1-3 complete sentences."""

    response = llm.invoke(prompt)
    return {"final_response": response.content.strip()}


# --- ROUTING LOGIC ---

def route_after_validation(state: AgentState):
    """Routes based on safety validation."""
    if not state.get("is_safe", True):
        return "generate_english_response"
    return "execute_sql"


def route_after_execution(state: AgentState):
    """Routes to self-correction loop or proceeds to visualization and response."""
    if state.get("sql_error"):
        # Stop after 3 attempts to prevent infinite API loops
        if state.get("iteration_count", 0) >= 3:
            return "generate_english_response"
        return "generate_sql"
    
    return "generate_chart_config"


# --- GRAPH ASSEMBLY ---

def build_agent():
    """Compiles nodes and conditional edges into a runnable LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("retrieve_schema", retrieve_schema)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate_sql", validate_sql)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("generate_chart_config", generate_chart_config)
    workflow.add_node("generate_english_response", generate_english_response)
    
    # Set entry point
    workflow.set_entry_point("retrieve_schema")
    
    # Edges
    workflow.add_edge("retrieve_schema", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")
    
    # Conditional security check
    workflow.add_conditional_edges(
        "validate_sql",
        route_after_validation,
        {
            "execute_sql": "execute_sql",
            "generate_english_response": "generate_english_response"
        }
    )
    
    # Conditional error correction loop
    workflow.add_conditional_edges(
        "execute_sql",
        route_after_execution,
        {
            "generate_sql": "generate_sql",
            "generate_chart_config": "generate_chart_config",
            "generate_english_response": "generate_english_response"
        }
    )
    
    workflow.add_edge("generate_chart_config", "generate_english_response")
    workflow.add_edge("generate_english_response", END)
    
    return workflow.compile()

# Initialize compiled graph executor
agent_executor = build_agent()


# --- FASTAPI INTEGRATION WRAPPER ---
def process_user_query(question: str):
    """Wrapper function to be imported and called by FastAPI main.py."""
    initial_state = {
        "question": question,
        "schema_context": "",
        "sql_query": "",
        "is_safe": True,
        "sql_error": "",
        "data_result": "",
        "raw_data": [], 
        "iteration_count": 0,
        "chart_config": None,
        "final_response": ""
    }
    
    result = agent_executor.invoke(initial_state)

    # Base response is always the English text
    responses = [
        {
            "role": "agent",
            "type": "text",
            "content": result.get("final_response", "Error processing request.")
        }
    ]

    # Append chart response if LLM configured one and we have data
    chart = result.get("chart_config")
    data = result.get("raw_data", [])

    if chart and chart.get("should_render") and data:
        responses.append({
            "role": "agent",
            "type": "chart",
            "data": data,
            "x_key": chart.get("x_axis"),
            "y_key": chart.get("y_axis")
        })

    return responses


# --- TERMINAL EXECUTION TEST ---
if __name__ == "__main__":
    test_question = "Which product category generated the highest total profit?"
    print(f"Testing Question: '{test_question}'\n" + "-"*50)
    
    initial_state = {
        "question": test_question,
        "schema_context": "",
        "sql_query": "",
        "is_safe": True,
        "sql_error": "",
        "data_result": "",
        "raw_data": [], 
        "iteration_count": 0,
        "chart_config": None,
        "final_response": ""
    }
    
    result = agent_executor.invoke(initial_state)

    print(f"\n[Generated SQL]: {result.get('sql_query')}")
    print(f"[Is Safe]: {result.get('is_safe')}")
    print(f"[Chart Config]: {result.get('chart_config')}")
    print(f"\n[Final Response]:\n{result.get('final_response')}")