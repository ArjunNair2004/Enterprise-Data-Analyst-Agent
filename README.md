Enterprise Data Analyst Agent 📊
An agentic Text-to-SQL application that autonomously executes and self-corrects SQL queries against a PostgreSQL database using LangGraph.

🏗️ Architecture
graph TD
    User((User)) -->|Question| Streamlit[Streamlit UI]
    Streamlit -->|Prompt| LangGraph[LangGraph Agent]
    LangGraph -->|Retrieve| VectorDB[(ChromaDB: Schema)]
    LangGraph -->|Generate/Fix| LLM[GPT-4o]
    LangGraph -->|Execute| Postgres[(Postgres DB)]
    Postgres -->|Result/Error| LangGraph


🚀 Getting Started
Prerequisites:
Docker Desktop
Python 3.9+
OpenAI API Key
Database Setup:
docker-compose up -d


Install Dependencies:
pip install -r requirements.txt

Environment Configuration:
Create a .env file and add your credentials:
OPENAI_API_KEY=your_key_here


Run the Application:
streamlit run app.py


📋 Features
Self-Healing SQL: The agent catches psycopg2 errors and re-prompts the LLM to fix the query.
Semantic Schema Retrieval: Uses vector embeddings to only pass relevant table schemas to the LLM.
Loop Safeguards: Max iteration limits to prevent infinite API loops.

### How to add this:
1. Create a file named `README.md` in your project folder.
2. Paste the text above into it.
3. Run these commands in your terminal:
   ```bash
   git add README.md
   git commit -m "Add project documentation and architecture"
   git push



