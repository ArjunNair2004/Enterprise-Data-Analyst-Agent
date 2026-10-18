AI Data Analyst Agent
A full-stack, containerized microservice application that enables non-technical users to analyze complex relational datasets using natural language. Rather than relying on traditional vector-based RAG, this project utilizes a LangGraph state machine to dynamically generate, validate, and execute precise SQL queries directly against a local database.

🏗 Architecture
The application is built on a modern, decoupled architecture using Docker for seamless cross-platform deployment:

Frontend (Client): A fast, responsive user interface built with React and Vite (Node 20 environment).

Backend (API): A robust, asynchronous REST API built with FastAPI and Python.

AI Orchestration: Utilizes LangGraph to manage a stateful workflow that connects the LLM, the database, and self-correction loops.

LLM Engine: Integrates the Groq API (using gpt-oss-120b) for ultra-low-latency natural language processing and SQL generation.

Database: SQLite database for local dataset management.

Infrastructure: Fully containerized using Docker and Docker Compose for environment consistency across Windows, macOS, and Linux.

🚀 Advanced Features
Dynamic Schema Injection: Bypasses the limitations of RAG by querying the SQLite database at runtime using PRAGMA table_info. The LLM always has the live, 100% accurate blueprint of the database.

Autonomous Error Correction: If the LLM generates a SQL query with a syntax error or a missing column, the LangGraph workflow catches the database error, feeds it back to the LLM, and automatically rewrites the query (up to 3 retries) before showing a failure to the user.

Security Guardrails: A deterministic validation node intercepts all generated SQL before execution, strictly blocking any state-changing or destructive commands (DROP, DELETE, UPDATE, INSERT).

Dynamic Visualizations: The AI analyzes its own data output. If it detects plottable numeric aggregations, it generates a JSON configuration to tell the React frontend exactly how to render a chart (Bar, Line, or Pie).

One-Click Deployment: A single Docker command spins up the isolated custom network, handles port forwarding, and installs all dependencies automatically.

🛠 Tech Stack
Frontend: React, Vite, JavaScript, Recharts

Backend: Python 3.11, FastAPI, Uvicorn, Pandas, SQLAlchemy

AI Engine: LangChain, LangGraph, Groq API

DevOps: Docker, Docker Compose

⚙️ Local Setup & Installation
Prerequisites
Docker Desktop installed and running.

A valid Groq API Key.

1. Clone the Repository
Bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
2. Environment Variables
Create a .env file inside the backend/ directory and add your Groq API key:

Code snippet
GROQ_API_KEY=your_actual_api_key_here
3. Run the Application
Start the isolated microservices using Docker Compose from the root directory:

Bash
docker-compose up --build
(Use docker-compose up -d to run in the background).

4. Access the Services
Once the containers are running, you can access the application at:

Frontend UI: http://localhost:5173

Backend API Docs: http://localhost:8000/docs

🛑 Stopping the Application
To gracefully stop the application and remove the internal Docker network, run:

Bash
docker-compose down
