import os
import json
import pandas as pd
from typing import TypedDict
from sqlalchemy import create_engine, text

# FREE TIER IMPORTS
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

# Database credentials (matching our docker-compose)
DB_USER = "admin"
DB_PASSWORD = "password123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ecommerce_db"
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# 1. Initialize our FREE LLM (Updated to the new Llama 3.3 model)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# 2. Initialize FREE local embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

class AgentState(TypedDict):
    """The state object that gets passed through the graph."""
    question: str
    schema_context: str
    sql_query: str
    sql_error: str
    data_result: str
    iteration_count: int

def get_retriever():
    """Loads the data dictionary into a local vector database for semantic search."""
    if not os.path.exists("data_dictionary.json"):
        raise FileNotFoundError("data_dictionary.json is missing! Please create it.")
        
    with open("data_dictionary.json", "r") as f:
        data_dict = json.load(f)
        
    docs = []
    # Convert each table definition into a searchable document
    for table in data_dict.get("tables", []):
        content = f"Table: {table['table_name']}\nDescription: {table['description']}\nColumns:\n"
        for col in table.get("columns", []):
            content += f"- {col['name']} ({col['type']}): {col.get('description', '')}\n"
        
        # Add business logic if present
        if "business_logic_rules" in table:
            content += "Business Rules:\n"
            for rule in table["business_logic_rules"]:
                content += f"- {rule}\n"
                
        docs.append(Document(page_content=content, metadata={"table": table['table_name']}))
        
    # Store in a local ChromaDB instance using our free embeddings
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 2})

def generate_sql(state: AgentState):
    """Generates or fixes the SQL query based on the state."""
    question = state["question"]
    error = state.get("sql_error", "")
    iteration = state.get("iteration_count", 0)
    
    # Retrieve relevant schema only on the first iteration to save tokens
    if iteration == 0:
        retriever = get_retriever()
        docs = retriever.invoke(question)
        schema_context = "\n\n".join([d.page_content for d in docs])
    else:
        schema_context = state["schema_context"]

    system_prompt = f"""You are a PostgreSQL expert. Your job is to write a SQL query to answer the user's question.
    Here is the database schema and business logic:
    {schema_context}
    
    Return ONLY the raw SQL query. No markdown formatting, no backticks, no explanations. Just the SQL."""
    
    # If there was an error in a previous loop, feed it back to the LLM to self-correct
    if error:
        system_prompt += f"\n\nWARNING: Your previous query failed with this error:\n{error}\nRewrite the query to fix it."
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
    
    response = llm.invoke(messages)
    # Clean the output just in case the LLM disobeys formatting instructions
    clean_sql = response.content.replace("```sql", "").replace("```", "").strip()
    
    return {
        "sql_query": clean_sql, 
        "schema_context": schema_context,
        "iteration_count": iteration + 1
    }

def execute_sql(state: AgentState):
    """Executes the SQL against the local Postgres database."""
    query = state["sql_query"]
    print(f"\n[Executing SQL]:\n{query}")
    
    try:
        with engine.connect() as connection:
            # Execute query and format as a markdown table using Pandas
            df = pd.read_sql(text(query), connection)
            result_str = df.to_markdown(index=False) if not df.empty else "No results found."
            return {"data_result": result_str, "sql_error": ""}
            
    except Exception as e: # <--- CHANGED: Catch ALL exceptions, including Pandas DatabaseError
        error_msg = str(e)
        print(f"\n[SQL Error Caught]: {error_msg}")
        return {"sql_error": error_msg, "data_result": ""}

def route_after_execution(state: AgentState):
    """Decides what to do next based on execution results."""
    if state["sql_error"]:
        # Hard stop after 3 tries to prevent infinite API loops
        if state["iteration_count"] >= 3:
            return "end" 
        return "generate_sql" # Loop back and let the LLM try to fix the error
    return "end" # Success!

def build_agent():
    """Compiles the nodes and edges into a runnable LangGraph."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("execute_sql", execute_sql)
    
    # Set entry point
    workflow.set_entry_point("generate_sql")
    
    # Add conditional edges for the self-healing loop
    workflow.add_edge("generate_sql", "execute_sql")
    workflow.add_conditional_edges(
        "execute_sql",
        route_after_execution,
        {
            "generate_sql": "generate_sql",
            "end": END
        }
    )
    
    return workflow.compile()

# Initialize the compiled graph for export
agent_executor = build_agent()