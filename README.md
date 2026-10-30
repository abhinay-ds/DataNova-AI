# DataNova AI

> **Analyze • Visualize • Predict**  
> An AI-powered full-stack data analysis and machine learning platform built with FastAPI and React.

---

## 1. Product Overview & Key Features

DataNova AI enables analysts, developers, and data practitioners to ingest structured datasets, converse with an AI agent in natural language, perform automated exploratory data analysis, train predictive machine learning models, inspect historical execution tasks, and generate executive HTML reports—all scoped securely by project and user.

### Verified Core Capabilities
- **Multi-Format Dataset Ingestion**: Upload, inspect, and analyze CSV, Excel (`.xlsx`, `.xls`), and JSON datasets.
- **Persistent AI Chat Workspace**: Interactive conversational workspace powered by Groq LLM with deterministic fallback routines. Messages, multi-step execution plans, and tool cards persist across sessions.
- **Dataset Profiling & Quality Scoring**: Automated schema inspection, data shape metrics, missing value computation, duplicate checks, statistical distribution analysis, and data quality rating.
- **Interactive Visualizations**: Generates tailored chart assets (bar charts, scatter plots, line charts, distributions) saved to the project workspace.
- **Machine Learning Engine**: Automated target variable detection, model training (Linear Regression, Random Forest, etc.), cross-validation scoring, evaluation metrics (R², MAE, RMSE), and predictions.
- **Code & SQL Generation**: Natural-language to SQL translation, Python code explanation, optimization, debugging, and format conversion.
- **Comprehensive Executive Reports**: Generate complete HTML reports compiling data profiles, quality scores, insights, recommendations, and ML evaluation metrics.
- **Secure Report Viewer & Downloader**: Reports are protected with token-based authentication and strict project isolation.
- **Authentic Task Execution History**: Real-time tracking of completed and failed capabilities extracted from conversational execution pipelines.
- **Multi-Project Workspace**: Create and switch between projects. All datasets, conversations, reports, and tasks are strictly isolated per project and user.

---

## 2. Technology Stack

- **Backend**:
  - [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+) — High-performance asynchronous web framework
  - [SQLAlchemy](https://www.sqlalchemy.org/) & [SQLite](https://sqlite.org/) — Relational data modeling with foreign key constraints
  - [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings` — Data validation and environment settings management
  - [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [Scikit-learn](https://scikit-learn.org/) — Data processing, statistics, and machine learning
  - [Matplotlib](https://matplotlib.org/) & [Seaborn](https://seaborn.pydata.org/) — Visualization generation
  - [python-jose](https://github.com/mpdavis/python-jose) & [bcrypt](https://github.com/pyca/bcrypt) — JWT token handling and secure password hashing
- **Frontend**:
  - [React 19](https://react.dev/) with [Vite](https://vitejs.dev/)
  - [React Router DOM](https://reactrouter.com/) (v7) — Client-side SPA routing
  - [Lucide React](https://lucide.dev/) — Iconography
  - CSS custom properties — Responsive light/dark theme design
- **AI / LLM Integration**:
  - [Groq Cloud](https://groq.com/) API via OpenAI Python SDK (`openai/gpt-oss-120b`) with robust offline heuristics and fallback capabilities.

---

## 3. Directory Structure

```text
DataNova-AI/
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI REST endpoints
│   │   │   ├── analysis.py       # GET /projects/{id}/analyses, /charts
│   │   │   ├── auth.py           # POST /auth/signup, /login, GET /auth/me
│   │   │   ├── chat.py           # POST /chat/ (AI orchestration)
│   │   │   ├── conversations.py  # GET /projects/{id}/conversations
│   │   │   ├── datasets.py       # GET/DELETE /projects/{id}/datasets
│   │   │   ├── dependencies.py   # JWT auth & user resolver
│   │   │   ├── projects.py       # CRUD /projects
│   │   │   ├── report.py         # POST /reports/generate, GET /reports
│   │   │   ├── tasks.py          # GET /projects/{id}/tasks
│   │   │   └── upload.py         # POST /upload/ dataset ingestion
│   │   ├── core/                 # Bootstrap, AI engine context & config
│   │   ├── models/               # SQLAlchemy models (User, Project, Dataset, Conversation, Message, etc.)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/             # Core business logic (File, ML, Report, Password, JWT)
│   │   ├── database.py           # Database connection & session setup
│   │   └── main.py               # FastAPI entrypoint, middleware, routers
│   ├── datanova.db               # SQLite database file
│   ├── requirements.txt          # Python dependencies
│   └── .env.example              # Backend environment template
├── frontend/
│   ├── src/
│   │   ├── components/           # Navbar, Sidebar, ChatArea, ChatInput, DatasetPanel, Cards
│   │   ├── context/              # AuthContext, ProjectContext, ChatContext, DatasetContext
│   │   ├── pages/                # Login, Signup, Dashboard, Workspace, Datasets, Reports, Tasks
│   │   ├── services/             # API client methods (api.js)
│   │   └── App.jsx               # Route definitions & layout wrappers
│   ├── package.json              # NPM dependencies & scripts
│   └── .env.example              # Frontend environment template
└── README.md
```

---

## 4. Getting Started & Installation

### Prerequisites
- **Python**: Version 3.10 to 3.14
- **Node.js**: Version 18+ and `npm`
- (Optional) **Groq API Key**: For live LLM completions (fallback routines operate if unconfigured).

---

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   - On Windows:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `backend/.env` with your settings:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   JWT_SECRET_KEY=your-secure-random-secret-key
   ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

5. **Start the FastAPI server**:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   The backend API documentation will be available at `http://127.0.0.1:8000/docs`.

---

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   Ensure `frontend/.env` points to your backend:
   ```env
   VITE_API_URL=http://127.0.0.1:8000
   ```

4. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

5. **Build for production**:
   ```bash
   npm run build
   ```

---

## 5. End-to-End User Flow

1. **Register & Log In**:
   - Visit `/signup`, register a new account, and authenticate at `/login`. A secure JWT token is stored in local session memory.
2. **Select or Create a Project**:
   - Access the dashboard or workspace. Create a dedicated project (e.g., "Customer Churn Analysis").
3. **Upload a Dataset**:
   - In the workspace or on `/datasets`, upload a CSV, Excel, or JSON file. DataNova AI profiles the dataset, checks quality, and loads it into your project.
4. **Chat & Analyze**:
   - In `/workspace`, ask questions in natural language (e.g., *"Show summary statistics"*, *"Create a distribution plot of age"*, *"Train a predictive model on churn"*).
   - Responses stream back as structured interactive cards (profiling cards, charts, code snippets, model evaluations).
5. **Inspect Tasks & Capabilities**:
   - Visit `/tasks` to inspect every capability routine executed during your chat sessions, complete with prompts and completion statuses.
6. **Generate & Download Reports**:
   - Visit `/reports`, select your dataset, and click **Generate Report**.
   - View the executive HTML report in a secure browser tab or click **Download** to save it locally.

---

## 6. Security & Storage Architecture

- **Authentication**: Stateless JWT (`HS256`) tokens with configurable expiration. Passwords hashed using `bcrypt` (gensalt).
- **Authorization & Isolation**: Every private endpoint verifies that `project.owner_id == current_user.id`. Requests across user boundaries return `404 Not Found` to prevent project enumeration.
- **Authenticated Report Delivery**: Reports are **not** exposed via unauthenticated public static routes. They require valid session tokens passed via header or query parameter.
- **Directory Traversal Protection**: Uploaded file names and report downloads are sanitized using `Path(...).name` basenames to prevent path manipulation.
- **Sanitized Error Handling**: Internal 500 error handlers log full traces server-side while presenting clean, non-sensitive messages to API clients.
- **CORS Protection**: Restricted to explicitly whitelisted origins via `ALLOWED_ORIGINS`.

---

## 7. Storage, Containerization & Deployment

- **Persistent Storage Solution**: DataNova AI supports a unified `DATA_DIR` environment variable. When deploying with Docker or cloud providers, mounting a persistent volume to `/data` automatically persists `datanova.db`, uploaded files (`uploads/`), generated charts (`outputs/charts/`), and HTML reports (`static/reports/`).
- **PostgreSQL Support**: For managed databases, set `DATABASE_URL=postgresql://user:password@host:5432/dbname`. The `psycopg2-binary` driver is pre-installed.
- **Docker Compose**: Production-ready `docker-compose.yml` is provided at the repository root with persistent named volume `datanova_persistent_data`.
- **Render Blueprint**: Full Infrastructure-as-Code specification in [`render.yaml`](render.yaml) provisioning FastAPI with a 10 GB persistent disk and React static frontend.
- **Complete Deployment Guide**: See [`deployment/DEPLOYMENT_GUIDE.md`](deployment/DEPLOYMENT_GUIDE.md) for step-by-step instructions across VPS, Render, Railway, and Vercel.
