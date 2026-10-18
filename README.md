# AI Data Analyst Agent



A full-stack, containerized AI application that allows users to interact with and analyze a supermarket dataset using natural language. Built with a decoupled microservice architecture, this project leverages LLMs to generate and execute SQL queries dynamically, providing intuitive data insights.



## 🏗 Architecture



The application is built on a modern, decoupled architecture using Docker for seamless cross-platform deployment:



*   **Frontend (Client):** A fast, responsive user interface built with **React** and **Vite**. (Runs on Node 20).

*   **Backend (API):** A robust, high-performance REST API built with **FastAPI** and **Python**.

*   **AI Engine:** Integrates **LangChain** and **Groq** for rapid, high-accuracy natural language processing and SQL generation.

*   **Database:** SQLite database for local dataset management and querying.

*   **Infrastructure:** Fully containerized using **Docker** and **Docker Compose** for environment consistency.



## 🚀 Features



*   **Natural Language to SQL:** Chat with your data. The AI engine translates conversational questions into precise SQL queries.

*   **Decoupled Microservices:** Clean separation of concerns between the React frontend and FastAPI backend.

*   **Interactive API Docs:** Auto-generated Swagger UI for easy backend endpoint testing.

*   **One-Click Deployment:** A single Docker command spins up the entire environment, handling all networking and dependency management.



## 🛠 Tech Stack



*   **Frontend:** React, Vite, JavaScript/JSX

*   **Backend:** Python 3, FastAPI, Uvicorn

*   **AI / LLM:** LangChain, Groq API

*   **DevOps:** Docker, Docker Compose

*   **Data:** SQLite, Supermarket Dataset



## ⚙️ Local Setup & Installation



### Prerequisites

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

*   A valid [Groq API Key](https://console.groq.com/keys).



### 1. Clone the Repository

```bash

git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)

cd your-repo-name
