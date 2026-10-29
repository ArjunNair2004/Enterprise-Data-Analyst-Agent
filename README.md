<div align="center">

# 🤖 Enterprise Data Analyst Agent

**A full-stack, containerized AI data analyst. Import any CSV file, ask questions in plain English, and a LangGraph agent writes and safely runs the SQL, explains the result in simple language, and draws a chart when the data calls for one.**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Uvicorn-009688?logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-1C3C3C?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036)
![React](https://img.shields.io/badge/React-Vite-61DAFB?logo=react&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Screenshots](#-screenshots)
- [Key Features](#-key-features)
- [Tech Stack](#️-tech-stack)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [How the Agent Works](#-how-the-agent-works)
- [API Endpoints](#-api-endpoints)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Usage](#-usage)
- [Configuration](#️-configuration)
- [Troubleshooting](#-troubleshooting)
- [Roadmap: Financial Document RAG](#-roadmap-financial-document-rag)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 🔎 Overview

The **Enterprise Data Analyst Agent** removes the SQL barrier between people and their data. A user imports a CSV file, asks a question such as *"Which product category generated the highest total profit?"*, and gets a short plain-English answer, plus a bar chart when the result is numeric.

The project is split into three decoupled parts:

- **Frontend** – a React and Vite chat interface with drag-and-drop CSV import, Recharts charts, voice input, and spoken answers.
- **Backend** – a FastAPI REST API that handles CSV uploads and chat requests.
- **AI agent** – a LangGraph workflow, powered by LangChain and the Groq API, that reads the dataset schema, generates SQL, validates it, executes it, corrects its own errors, and writes the answer.

The agent is **dataset-agnostic**. Uploaded data is stored in SQLite, and the agent reads the table and column names at runtime, so no code changes are needed to analyze a different dataset. The Superstore sales dataset is included as a demo. Docker Compose starts the whole environment with one command.

The longer-term goal is a true *enterprise* analyst that can also read corporate financial PDFs such as 10-K reports. See the [Roadmap](#-roadmap-financial-document-rag).

---

## 📸 Screenshots

<!-- TODO: Add screenshots to the repo (for example in a docs/ folder) and replace the placeholders below:
| Dashboard & Import | Answer with Chart | Swagger UI |
|:---:|:---:|:---:|
| ![Dashboard](docs/dashboard.png) | ![Chart](docs/chart.png) | ![Swagger](docs/swagger.png) |
-->

*Screenshots coming soon.*

---

## ✨ Key Features

- **Natural language to SQL** – chat with your data; the LLM translates questions into SQLite queries.
- **Works with any CSV** – drag and drop a file; column names are cleaned and the schema is detected automatically.
- **Self-correcting queries** – if a query fails, the error is sent back to the model and the query is rewritten, up to 3 attempts.
- **SQL safety guardrail** – only read-only `SELECT` / `WITH` queries run; destructive commands such as `DROP`, `DELETE`, `UPDATE`, and `INSERT` are blocked.
- **Automatic charts** – when the result has a numeric column, the agent returns a chart configuration and the frontend draws a bar chart with Recharts.
- **Plain-English answers** – results are summarized for non-technical users, without SQL or column names.
- **Voice input and spoken answers** – speak your question and hear the answer, using the browser Web Speech API (best in Chrome or Edge).
- **Interactive API docs** – auto-generated Swagger UI for testing the backend.
- **One-command deployment** – Docker Compose builds and starts both services.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React, Vite, JavaScript/JSX, Tailwind CSS classes, Recharts, react-dropzone, lucide-react, Web Speech API |
| **Backend** | Python 3, FastAPI, Uvicorn, Pydantic, Pandas, SQLAlchemy |
| **AI / LLM** | LangGraph, LangChain (`langchain-groq`), Groq API (`openai/gpt-oss-120b`, temperature 0) |
| **Database** | SQLite (`data.db`) |
| **DevOps** | Docker, Docker Compose |

---

## 🧱 System Architecture

```
┌────────────────────────┐   /api/upload (CSV)       ┌──────────────────────────┐
│   Frontend (React)     │ ────────────────────────► │      FastAPI Backend     │
│  • CSV drag & drop     │   /api/chat (question)    │  main.py                 │
│  • Chat + Recharts     │ ────────────────────────► │  • Pydantic validation   │
│  • Voice in / out      │ ◄──────────────────────── │  • CORS, Swagger /docs   │
└────────────────────────┘    text + chart messages  └───────┬───────────┬──────┘
                                                             │           │
                                         CSV → table         │           │  question
                                                    ┌────────▼───────┐ ┌─▼───────────────────────┐
                                                    │ SQLite         │ │ LangGraph agent         │
                                                    │ data.db        │◄┤ agent.py                │
                                                    │ uploaded_data  │ │ LangChain + Groq LLM    │
                                                    └────────────────┘ └─────────────────────────┘

        Frontend and backend are containerized and started together with Docker Compose.
```

---

## 📂 Project Structure

```
Enterprise-Data-Analyst-Agent/
├── backend/                    # FastAPI API + AI agent
│   ├── main.py                 # FastAPI endpoints (/api/upload, /api/chat)
│   ├── agent.py                # LangGraph agent: schema → SQL → validate → execute → chart → answer
│   ├── load_csv.py             # Script for loading a CSV into SQLite
│   ├── init.sql                # Database initialization script
│   ├── superstore.csv          # Sample dataset
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Backend container image
├── frontend/                   # React + Vite user interface
│   ├── src/                    # React components (App.jsx)
│   ├── index.html
│   ├── package.json            # Node dependencies
│   └── Dockerfile              # Frontend container image
├── docker-compose.yml          # Runs the frontend and backend together
├── .gitignore
└── README.md                   # Project documentation
```

---

## 🤖 How the Agent Works

The agent is a LangGraph state graph. Each node reads and updates a shared state (question, schema, SQL, errors, results, chart config).

| Step | Node | What happens |
|---|---|---|
| 1 | `retrieve_schema` | Reads table and column names directly from SQLite (`sqlite_master`, `PRAGMA table_info`) |
| 2 | `generate_sql` | The LLM writes a SQLite query from the schema and question; earlier errors are included in the prompt |
| 3 | `validate_sql` | Guardrail: allows only `SELECT` / `WITH`, blocks destructive commands. Unsafe queries skip execution |
| 4 | `execute_sql` | Runs the query with SQLAlchemy and Pandas. On failure, loops back to step 2 (max 3 attempts) |
| 5 | `generate_chart_config` | The LLM decides whether a chart makes sense and returns type, axes, and title as JSON |
| 6 | `generate_english_response` | The LLM turns the result into a short, non-technical answer |

The API then returns a list of messages (a text answer and, if applicable, a chart) which the frontend renders and reads aloud.

> ⚠️ The guardrail uses keyword checks. For sensitive data, also use a read-only database connection.

---

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/upload` | Upload a CSV file. Columns are cleaned (for example `Order Date` → `order_date`) and the data replaces the `uploaded_data` table in `data.db` |
| `POST` | `/api/chat` | Send `{ "message": "...", "dataset_name": "..." }` and receive `{ "responses": [...] }` with text and chart messages |
| `GET` | `/docs` | Interactive Swagger UI |

> Importing a new CSV replaces the previously loaded dataset.

---

## 📋 Prerequisites

| Requirement | Version / Notes |
|---|---|
| **Docker Desktop** | Installed and **running** |
| **Groq API key** | Get one from the [Groq console](https://console.groq.com/keys) |
| **Git** | To clone the repository |
| **Web browser** | Chrome or Edge recommended (voice features) |

Python 3 and Node.js 20 are only needed if you run the services without Docker.

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/ArjunNair2004/Enterprise-Data-Analyst-Agent.git
cd Enterprise-Data-Analyst-Agent
```

### 2. Add your Groq API key

Create `backend/.env` (never commit this file):

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Build and start everything

```bash
docker compose up --build
```

### 4. Open the application

| Service | URL |
|---|---|
| Frontend | `http://localhost:5173` |
| Backend API | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |

### 5. Stop the application

```bash
docker compose down
```

### Running without Docker (optional)

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (in a second terminal)
cd frontend
npm install
npm run dev
```

---

## 💡 Usage

1. **Import a dataset** – drag a CSV file (for example `backend/superstore.csv`) into the sidebar.
2. **Ask a question** – type it, or click the microphone and speak. For example:
   - *"Which product category generated the highest total profit?"*
   - *"Show total sales by region."*
   - *"How many orders were placed in each year?"*
3. **Read or listen to the answer** – a short explanation appears, and a bar chart is added when the result is numeric.
4. **Test the API directly** – open Swagger UI at `/docs`.

---

## ⚙️ Configuration

| Setting | Location | Default / Notes |
|---|---|---|
| Groq API key | `backend/.env` | `GROQ_API_KEY`, required |
| LLM model | `backend/agent.py` | `openai/gpt-oss-120b`, temperature 0 |
| Max SQL retries | `backend/agent.py` | 3 attempts |
| Allowed frontend origin (CORS) | `backend/main.py` | `http://localhost:5173` |
| Ports | `docker-compose.yml` | Backend `8000`, frontend `5173` |
| Database file | `backend/data.db` | SQLite, table `uploaded_data` |

> 🔐 **Security tip:** never commit your API key. Keep it in `backend/.env`, which should be listed in `.gitignore`.

---

## 🧯 Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `docker compose` can't connect to the Docker daemon | Docker Desktop is not running | Start Docker Desktop and retry |
| "Failed to connect to backend server" alert on upload | Backend not running on port 8000 | Check `docker compose logs backend` |
| Authentication error from the model | Missing or invalid Groq API key | Check `GROQ_API_KEY` in `backend/.env` and restart |
| CORS error in the browser console | Frontend served from a different origin | Add that origin to `allow_origins` in `backend/main.py` |
| Answer says "I couldn't complete your request" | The generated SQL kept failing, or was blocked by the guardrail | Rephrase the question and make it more specific |
| Chat input is disabled | No dataset imported yet | Import a CSV file first |
| Voice input does nothing | Browser does not support speech recognition | Use Chrome or Edge |
| `Port is already allocated` | Another service uses 8000 or 5173 | Stop that service or change the port in `docker-compose.yml` |

---

## 🔮 Roadmap: Financial Document RAG

The next phase extends the agent from structured CSV data to unstructured corporate documents such as 10-K reports, which contain dense text, nested tables, and graphs.

- **PDF ingestion** – parse financial filings into text, tables, and images.
- **Vision-Language Model captioning** – send charts and graphs to a VLM so visual content becomes searchable text.
- **Structured table extraction** – convert tables into structured JSON for accurate numerical reasoning.
- **Vector database** – embed text, captions, and tables for semantic search.
- **Retrieval pipeline** – retrieve the right context before the LLM answers (Retrieval-Augmented Generation).
- **Hybrid routing** – decide per question whether to use SQL over structured data or retrieval over documents.

Other ideas:

- **Stronger SQL safety** – a read-only connection and a SQL parser instead of keyword checks.
- **Multi-table datasets** – several CSV files and joins instead of a single replaceable table.
- **More chart types** – line and pie charts.
- **Conversation memory** – follow-up questions that refer to earlier answers.
- **Cloud deployment** – host the containers on AWS or Google Cloud.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

No license has been specified for this repository yet. Add a `LICENSE` file (for example MIT) to define how others may use the code.

---

## 👤 Author

**Arjun Nair** – [@ArjunNair2004](https://github.com/ArjunNair2004)

If you found this project useful, consider giving it a ⭐ on GitHub!
