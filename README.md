<div align="center">

# 🤖 Enterprise Data Analyst Agent

**A full-stack, containerized AI application that lets you analyze a dataset in plain English. An LLM turns your question into SQL, runs it against a database, and returns the answer in a React chat interface.**

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Uvicorn-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Vite-61DAFB?logo=react&logoColor=black)
![LangChain](https://img.shields.io/badge/LangChain-Groq-1C3C3C?logo=langchain&logoColor=white)
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
- [How Natural Language to SQL Works](#-how-natural-language-to-sql-works)
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

The **Enterprise Data Analyst Agent** removes the SQL barrier between people and their data. Instead of writing queries, a user asks a question such as *"Which product category had the highest sales?"*. The AI engine converts it into a SQL query, the backend executes it on the database, and the result is shown in the chat interface.

The project is split into three decoupled parts:

- **Frontend** – a fast, responsive chat interface built with React and Vite.
- **Backend** – a high-performance REST API built with FastAPI.
- **AI engine** – LangChain with the Groq API for rapid natural-language processing and SQL generation.

A SQLite database holds the dataset (a supermarket dataset is used for the demo), and Docker Compose starts the entire environment with a single command.

The longer-term goal is a true *enterprise* analyst that can also read corporate financial PDFs such as 10-K reports. See the [Roadmap](#-roadmap-financial-document-rag).

---

## 📸 Screenshots

<!-- TODO: Add screenshots to the repo (for example in a docs/ folder) and replace the placeholders below:
| Chat Interface | Generated SQL & Result | Swagger UI |
|:---:|:---:|:---:|
| ![Chat](docs/chat.png) | ![Result](docs/result.png) | ![Swagger](docs/swagger.png) |
-->

*Screenshots coming soon.*

---

## ✨ Key Features

- **Natural language to SQL** – chat with your data. The AI engine translates conversational questions into precise SQL queries.
- **Dynamic query execution** – generated SQL runs against the database and the results come back in the chat.
- **Decoupled microservices** – clean separation of concerns between the React frontend and the FastAPI backend.
- **Fast LLM inference** – the Groq API gives low-latency responses through LangChain.
- **Interactive API docs** – auto-generated Swagger UI for easy backend endpoint testing.
- **One-click deployment** – a single Docker command spins up the whole environment, handling networking and dependencies.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React, Vite, JavaScript/JSX (Node 20) |
| **Backend** | Python 3, FastAPI, Uvicorn |
| **AI / LLM** | LangChain, Groq API |
| **Database** | SQLite (Supermarket dataset) |
| **DevOps** | Docker, Docker Compose |

---

## 🧱 System Architecture

```
┌────────────────────────┐        HTTP / JSON        ┌──────────────────────────┐
│   Frontend (React)     │ ────────────────────────► │      FastAPI Backend     │
│  • Vite dev/build      │                           │  • REST endpoints        │
│  • Chat interface      │ ◄──────────────────────── │  • Request validation    │
└────────────────────────┘      answer / results     │  • Swagger UI at /docs   │
                                                     └───────┬───────────┬──────┘
                                                             │           │
                                              run SQL        │           │  question + schema
                                                    ┌────────▼───────┐ ┌─▼──────────────────┐
                                                    │ SQLite         │ │ LangChain + Groq   │
                                                    │ (dataset)      │ │ (SQL generation)   │
                                                    └────────────────┘ └────────────────────┘

        All services are containerized and started together with Docker Compose.
```

---

## 📂 Project Structure

```
Enterprise-Data-Analyst-Agent/
├── backend/                    # FastAPI app, LangChain/Groq logic, SQLite database
├── frontend/                   # React + Vite user interface
├── docker-compose.yml          # Runs the frontend and backend together
├── .gitignore
└── README.md                   # Project documentation
```

> 📝 Expand this tree with the individual files inside `backend/` and `frontend/` if you want a more detailed view.

---

## 🤖 How Natural Language to SQL Works

| Step | What happens |
|---|---|
| **1. Question** | The user types a question in the React chat interface |
| **2. Request** | The frontend sends it to the FastAPI backend over REST |
| **3. Prompting** | LangChain combines the question with the database schema and sends it to the LLM via Groq |
| **4. SQL generation** | The LLM returns a SQL query that answers the question |
| **5. Execution** | The backend runs the query on SQLite and collects the rows |
| **6. Response** | The result is returned as JSON and displayed in the chat |

> ⚠️ LLM-generated SQL should be treated with care. Use a read-only database connection, or validate queries before execution, when working with data you cannot afford to modify.

---

## 📋 Prerequisites

| Requirement | Version / Notes |
|---|---|
| **Docker Desktop** | Installed and **running** |
| **Groq API key** | Get one from the [Groq console](https://console.groq.com/keys) |
| **Git** | To clone the repository |
| **Web browser** | Any modern browser |

Python and Node.js are only needed if you run the services outside Docker (the frontend runs on Node 20).

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/ArjunNair2004/Enterprise-Data-Analyst-Agent.git
cd Enterprise-Data-Analyst-Agent
```

### 2. Add your Groq API key

Provide your key to the backend, for example through an environment file:

```bash
# backend/.env  (never commit this file)
GROQ_API_KEY=your_groq_api_key_here
```

> 📝 Use the variable name and file location your backend actually reads, and update this step to match.

### 3. Build and start everything

```bash
docker compose up --build
```

This builds the frontend and backend images, sets up networking, and starts both services.

### 4. Open the application

| Service | URL |
|---|---|
| Frontend | `http://localhost:5173` |
| Backend API | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |

> 📝 These are the usual Vite and FastAPI ports. Check `docker-compose.yml` and change them here if yours differ.

### 5. Stop the application

```bash
docker compose down
```

---

## 💡 Usage

1. **Open the frontend** in your browser.
2. **Ask a question** about the dataset in plain English, for example:
   - *"How many products are in each category?"*
   - *"What are the top 5 best-selling items?"*
   - *"What was the total revenue last month?"*
3. **Read the answer** returned in the chat.
4. **Test the API directly** by opening Swagger UI at `/docs` and trying the endpoints.

---

## ⚙️ Configuration

| Setting | Location | Default / Notes |
|---|---|---|
| Groq API key | Environment variable / `.env` | Required for the LLM to respond |
| Frontend / backend ports | `docker-compose.yml` | Update the README if you change them |
| Database | SQLite file in `backend/` | Replace it to analyze your own dataset |
| LLM model | Backend AI engine code | Any model available on Groq |

> 🔐 **Security tip:** never commit your API key. Keep it in a `.env` file that is listed in `.gitignore`.

---

## 🧯 Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `docker compose` can't connect to the Docker daemon | Docker Desktop is not running | Start Docker Desktop and retry |
| Backend returns an authentication error | Missing or invalid Groq API key | Check the key and restart the containers |
| `Port is already allocated` | Another service uses the port | Stop that service or change the port in `docker-compose.yml` |
| Frontend loads but gets no answers | Backend not reachable | Run `docker compose logs backend` and check for errors |
| Wrong or failing SQL | The model misread the schema or question | Rephrase the question and make it more specific |
| Changes don't appear after editing code | Stale image | Rebuild with `docker compose up --build` |

---

## 🔮 Roadmap: Financial Document RAG

The next phase extends the agent from structured databases to unstructured corporate documents such as 10-K reports, which contain dense text, nested tables, and graphs.

- **PDF ingestion** – parse financial filings into text, tables, and images.
- **Vision-Language Model captioning** – send charts and graphs to a VLM so visual content becomes searchable text.
- **Structured table extraction** – convert tables into structured JSON for accurate numerical reasoning.
- **Vector database** – embed text, captions, and tables for semantic search.
- **Retrieval pipeline** – retrieve the right context before the LLM answers (Retrieval-Augmented Generation).
- **Hybrid routing** – decide per question whether to use SQL over structured data or retrieval over documents.

Other ideas:

- **Read-only SQL guardrails** – validate generated queries before they run.
- **Bring your own data** – upload CSV or database files from the interface.
- **Charts** – return visualizations alongside tabular answers.
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
