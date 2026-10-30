# DataNova AI Project Audit

**Audit Date:** October 1, 2026  
**Auditor:** Senior Full-Stack Engineer  
**Git Checkpoint:** `a2d9163` ("Before Windsurf completion")  
**Stack:** React 19 + Vite 8 (Frontend) | FastAPI 0.139 + SQLAlchemy 2.0 (Backend) | SQLite / Pydantic / Groq LLM / Scikit-Learn

---

## 1. Working

1. **Frontend Production Build:** Vite build succeeds without compilation errors (`dist/` created in ~480ms).
2. **FastAPI Server Startup & Health Check:** Backend boots cleanly with Uvicorn; `/health` returns `{"status": "Healthy"}` and `/` returns API welcome message.
3. **User Authentication (Local JWT):**
   - User registration (`POST /auth/signup`) with bcrypt password hashing.
   - User login (`POST /auth/login`) with credential validation and JWT issuance.
   - User profile retrieval (`GET /auth/me`) with Bearer token authentication.
4. **Protected Client Routes & Session Restoration:** React Router v7 routes protected with `ProtectedRoute`; sessions restore on refresh if token is valid.
5. **Theme Management:** Dark and Light mode switching with CSS variable mapping and `localStorage` persistence.
6. **Project Management:**
   - Create, list, fetch, update, and delete projects (`/projects` CRUD) with strict `owner_id` user isolation.
   - Active project state synchronized to `localStorage`.
7. **Dataset Upload & Statistical Profiling:**
   - Multi-format ingestion (`.csv`, `.xlsx`, `.xls`, `.json`) via `/upload/`.
   - Automated profiling (row/column counts, data types, missing values, duplicates, numeric statistics, quality scoring, correlation insights).
8. **AI Engine & Tool Registry:**
   - Dynamic loading and execution of 23 registered capabilities and 24 specialized tools.
   - Real-world end-to-end workflow execution (`test_real_workflow.py` plans and completes `analyze_dataset` and `scatter` plot generation).
9. **AI Code Generation Tools:**
   - Verified working standalone: `generate_python`, `generate_sql`, `explain_code`, `debug_code`, `optimize_code`, `convert_code` via Groq LLM integration.
10. **Machine Learning Pipeline:**
    - Automated problem detection (regression/classification).
    - Multi-model training and cross-validation (Linear Regression, Ridge, Lasso, Random Forest, Gradient Boosting).
    - Best model selection and metric evaluation (R², MAE, RMSE).
    - Serialized model persistence to `.pkl`.
11. **Report Export Service:**
    - HTML analysis report generation and file persistence.

---

## 2. Partially Working

1. **AI Chat Endpoint (`/chat/`):**
   - *Current Behavior:* Processes messages through `AIEngine`, routes tasks, and returns text and chart responses.
   - *Limitation:* Does not authenticate requests; does not verify user or project ownership; reads datasets solely from volatile in-memory `SessionManager`; does not record messages to the database.
2. **Dataset Management in UI:**
   - *Current Behavior:* Datasets upload successfully, display summary in `DatasetPanel`, and create a database record in `datasets` table.
   - *Limitation:* `DatasetContext.jsx` is purely in-memory React state. Upon browser refresh, `dataset` becomes `null`, forcing re-upload. `Datasets.jsx` does not fetch existing project datasets from `/projects/{id}/datasets`.
3. **ML Prediction Workflow (`test_ai_prediction.py`):**
   - *Current Behavior:* Generates plan with `train_model`, `evaluate_model`, and `predict`. Trains model and runs predictions successfully.
   - *Limitation:* The `evaluate_model` task fails when input specifies multiple columns because target extraction heuristically matches the longest column name ("Experience") instead of the real target ("Salary").
4. **Code Generation Planner Classification (`test_ai_code_capabilities.py`):**
   - *Current Behavior:* Explaining, debugging, and optimizing code works end-to-end.
   - *Limitation:* Natural language requests like *"Generate SQL to calculate average salary..."* or *"Convert this Python code to JavaScript..."* are misclassified by the planner as `data_question` instead of `generate_sql` or `convert_code`, causing failure when no dataset is loaded.
5. **Static File Serving for Generated Charts & Reports:**
   - *Current Behavior:* Charts are served at `/charts/{filename}` from `outputs/charts`.
   - *Limitation:* Mount path is relative; fails if backend is launched from repository root. Reports stored in `static/reports/` are never mounted in FastAPI, rendering generated HTML reports inaccessible over HTTP.

---

## 3. Broken

1. **Planner Standalone Unit Tests (`test_planner.py` & `test_orchestrator.py`):**
   - *Current Behavior:* Crash immediately with `ValueError: Capability registry is not available.`
   - *Cause:* Tests instantiate `AIContext` without setting `capability_registry`, which `PlannerAgent.execute()` strictly requires.
2. **Prompt Dispatch in `ChatMessages.jsx`:**
   - *Current Behavior:* Clicking quick suggestion buttons inside chat messages produces no action.
   - *Cause:* `ChatMessages.jsx` dispatches `new CustomEvent("datanova:prompt", { detail: { prompt } })`, while `ChatInput.jsx` expects `typeof event.detail === "string"`.
3. **Linux / Docker File Casing Mismatch:**
   - *Current Behavior:* Frontend imports `MainLayout.jsx` in `Workspace.jsx` and `Chat.jsx`, but Git tracks the file as `Mainlayout.jsx` (lowercase `l`).
   - *Impact:* Works on case-insensitive Windows, but immediately breaks on Linux CI and Docker containers with `Module not found`.
4. **Backend `requirements.txt` Encoding:**
   - *Current Behavior:* Encoded in UTF-16LE with Byte Order Mark (BOM) due to Windows PowerShell output redirection.
   - *Impact:* Fails standard Linux/Docker `pip install -r requirements.txt` and fails automated text file viewers.

---

## 4. Missing

1. **Conversation & Message Persistence:**
   - `conversations` and `messages` tables exist in SQLite but have 0 records.
   - No backend endpoints exist to create, list, retrieve, or delete conversations or message histories.
2. **Analysis & Chart History Persistence:**
   - `analyses` and `charts` tables exist in SQLite but have 0 records.
   - No backend endpoints exist to save or query past analyses or charts per project.
3. **Empty API Routers in `backend/app/api/`:**
   - `analysis.py` (0 bytes)
   - `profile.py` (0 bytes)
   - `report.py` (0 bytes)
   - `sql.py` (0 bytes)
   - `tasks.py` (0 bytes)
   - `visualization.py` (0 bytes)
   - `workspace.py` (0 bytes)
4. **Empty Auth Modules in `backend/app/auth/`:**
   - `auth_service.py` (0 bytes)
   - `oauth_service.py` (0 bytes)
   - `routes.py` (0 bytes)
5. **Frontend Pages Implementation:**
   - `Reports.jsx` is a static placeholder with no report listing, preview, or download.
   - `Tasks.jsx` is a static placeholder with no task history or live execution tracking.
6. **Database Migrations:**
   - `backend/alembic.ini` is 0 bytes; no Alembic migration environment exists. Tables are created only on startup via `Base.metadata.create_all()`.
7. **Containerization:**
   - `backend/Dockerfile` is 0 bytes.

---

## 5. Frontend Status

### Routing & Architecture
- React 19 + Vite 8 + React Router v7.
- Root routes: `/` (Landing), `/login` (Auth), `/dashboard` (Overview), `/workspace` (AI Workspace), `/datasets` (Dataset Manager), `/reports` (Reports), `/tasks` (Tasks), `/settings` (Settings).
- Production build succeeds (`npm run build` passes).

### Components & Layout
- **MainLayout:** Resizable 3-column layout (Sidebar, Chat Area, Dataset Panel) with pointer-event drag handlers and responsive mobile drawer.
- **ChatArea:** Dual-mode component showing welcome prompt tiles when empty and `ChatMessages` during an active conversation.
- **ChatInput:** Large monolithic component (1,720 lines) supporting file attachment, stage progress animation, suggestion handling, and message submission.
- **DatasetPanel:** 3-tab inspector (Overview, Columns, Sample Data) showing dataset metadata, shape, missing values, and column summaries.
- **Sidebar:** Collapsible navigation with brand logo, primary links, and project shortcuts.
- **Navbar:** Workspace breadcrumbs, theme toggle button, and sidebar/dataset panel toggles.

### Contexts
- **AuthContext:** Restores session via `/auth/me` on mount using stored JWT.
- **ProjectContext:** Loads projects from API, manages active project, syncs to `localStorage`.
- **DatasetContext:** Stores active dataset object; loses state on page refresh.
- **ChatContext:** Stores array of message cards; loses state on page refresh.
- **ThemeContext:** Manages light/dark theme attributes on `document.documentElement` and `document.body`.

### Frontend Issues Identified
1. **ChatMessages Event Format Inconsistency:**
   - File: `frontend/src/components/chat/ChatMessages.jsx`
   - Component: `sendPromptToComposer`
   - Current behavior: `window.dispatchEvent(new CustomEvent("datanova:prompt", { detail: { prompt } }))`
   - Problem: `ChatInput.jsx` line 1305 expects `detail` to be a string. Event is ignored.
   - Required fix: Pass string directly: `{ detail: prompt }`.
   - Priority: HIGH
2. **File Casing Discrepancy:**
   - File: `frontend/src/components/layout/Mainlayout.jsx`
   - Component: File naming
   - Current behavior: Git index holds `Mainlayout.jsx`, imports use `MainLayout.jsx`.
   - Problem: Fails on case-sensitive Linux/Docker builds.
   - Required fix: Git mv to `MainLayout.jsx`.
   - Priority: CRITICAL
3. **Volatile Dataset Context:**
   - File: `frontend/src/context/DatasetContext.jsx`
   - Component: `DatasetProvider`
   - Current behavior: `useState(null)` without syncing to active project datasets or `localStorage`.
   - Problem: Refreshing `/workspace` leaves dataset panel blank even when files exist in project.
   - Required fix: Fetch project datasets from `/projects/{activeProject.id}/datasets` on mount/project change.
   - Priority: HIGH
4. **Hardcoded Recent Items in Sidebar:**
   - File: `frontend/src/components/layout/Sidebar.jsx`
   - Component: `recent` list
   - Current behavior: Displays dummy items: `["Titanic Analysis", "Customer Churn", "Sales Dashboard"]`.
   - Problem: Misleading mock data instead of real user projects.
   - Required fix: Populate from `useProject().projects`.
   - Priority: MEDIUM
5. **Placeholder Pages:**
   - File: `frontend/src/pages/Datasets.jsx`, `Reports.jsx`, `Tasks.jsx`
   - Component: Page components
   - Current behavior: Static marketing stubs.
   - Problem: User cannot view past datasets, download reports, or inspect tasks.
   - Required fix: Connect to backend endpoints.
   - Priority: HIGH

---

## 6. Backend Status

### Startup & Route Registration
- FastAPI app initializes in `backend/app/main.py`.
- Health check route `/health` and root `/` respond with 200 OK.
- CORS middleware is configured for `http://localhost:5173` and `http://127.0.0.1:5173`.

### Backend Route Redundancy & Clutter
- `upload_router` is imported and registered twice in `main.py` (lines 5/12 and 39/45).
- Multiple duplicate files exist between `backend/app/auth` and `backend/app/services`.
- Seven empty route files exist in `backend/app/api/` that clutter the module tree.

### Backend Issues Identified
1. **Unauthenticated Chat Route:**
   - File: `backend/app/api/chat.py`
   - Component: `chat` endpoint
   - Current behavior: `async def chat(request: ChatRequest):` has no `Depends(get_current_user)`.
   - Problem: Anyone can invoke LLM generation and consume API quota without authentication.
   - Required fix: Inject `current_user: User = Depends(get_current_user)` and validate project access.
   - Priority: CRITICAL
2. **Duplicate Upload Router Registration:**
   - File: `backend/app/main.py`
   - Component: `app.include_router(upload_router)`
   - Current behavior: Included twice.
   - Problem: Unnecessary route table duplication.
   - Required fix: Remove redundant import and inclusion.
   - Priority: LOW
3. **Hardcoded Secrets Fallback:**
   - File: `backend/app/services/jwt_service.py`
   - Component: `SECRET_KEY`
   - Current behavior: Defaults to `"datanova-development-secret-change-this"`.
   - Problem: Security vulnerability if environment variable is omitted in production.
   - Required fix: Enforce secure random key or raise error in production mode.
   - Priority: HIGH
4. **Static Report Directory Not Mounted:**
   - File: `backend/app/main.py`
   - Component: Static file mounts
   - Current behavior: Only `/charts` is mounted.
   - Problem: HTML reports exported to `static/reports/` cannot be served to clients.
   - Required fix: Add `app.mount("/static", StaticFiles(directory="static"), name="static")`.
   - Priority: HIGH
5. **UTF-16LE Encoded Requirements File:**
   - File: `backend/requirements.txt`
   - Component: Dependency specification
   - Current behavior: UTF-16LE with BOM encoding.
   - Problem: Breaks standard Linux/Docker pip installation.
   - Required fix: Re-encode to clean UTF-8 without BOM.
   - Priority: HIGH

---

## 7. Database Status

### Verified Relationships & Cascade Configuration
```
User (id)
  └── 1:N ──> Project (id, owner_id FK -> users.id, cascade="all, delete-orphan")
                ├── 1:N ──> Dataset (id, project_id FK -> projects.id, cascade="all, delete-orphan")
                ├── 1:N ──> Conversation (id, project_id FK -> projects.id ondelete CASCADE)
                │             └── 1:N ──> Message (id, conversation_id FK -> conversations.id ondelete CASCADE)
                ├── 1:N ──> Analysis (id, project_id FK -> projects.id, cascade="all, delete-orphan")
                └── 1:N ──> Chart (id, project_id FK -> projects.id, cascade="all, delete-orphan")
```

### Actual Database Records in `datanova.db`
- `users`: 2 records
- `projects`: 2 records
- `datasets`: 2 records
- `conversations`: **0 records**
- `messages`: **0 records**
- `analyses`: **0 records**
- `charts`: **0 records**

### Database Issues Identified
1. **Zero Conversation/Message Persistence:**
   - File: `backend/app/api/chat.py`
   - Component: `chat` endpoint
   - Current behavior: Reads and writes only to in-memory `SessionManager`.
   - Problem: Database tables `conversations` and `messages` remain completely empty.
   - Required fix: Lookup or create `Conversation` in database and persist incoming and outgoing messages to `messages` table.
   - Priority: CRITICAL
2. **Missing SQLite Foreign Key Enforcement:**
   - File: `backend/app/database.py`
   - Component: `engine` setup
   - Current behavior: Connects to SQLite without enabling foreign keys.
   - Problem: SQLite ignores `ON DELETE CASCADE` unless `PRAGMA foreign_keys = ON` is executed on connection.
   - Required fix: Add SQLAlchemy event listener for connect: `dbapi_con.execute("PRAGMA foreign_keys=ON")`.
   - Priority: HIGH
3. **Duplicate Database Configuration:**
   - File: `backend/database.py` vs `backend/app/database.py`
   - Component: Engine and Base definitions
   - Current behavior: Two identical database configuration files exist.
   - Problem: Architecture duplication; potential for model registry conflicts.
   - Required fix: Remove unused root `backend/database.py`.
   - Priority: MEDIUM
4. **Pydantic Model in SQLAlchemy Models Directory:**
   - File: `backend/app/models/workspace.py`
   - Component: `Workspace` class
   - Current behavior: Inherits from `pydantic.BaseModel` inside `app/models/`.
   - Problem: Violates architectural boundaries; confusion between ORM and Pydantic schemas.
   - Required fix: Move to `app/schemas/workspace.py`.
   - Priority: LOW
5. **No Migration System:**
   - File: `backend/alembic.ini`
   - Component: Schema migrations
   - Current behavior: Empty 0-byte file; schema is created dynamically on app boot via `create_all()`.
   - Problem: Production schema evolution is impossible without manual database surgery.
   - Required fix: Initialize proper Alembic migration environment.
   - Priority: MEDIUM

---

## 8. Authentication Status

### Working Elements
- User signup (`POST /auth/signup`) validates email duplication, hashes password with `bcrypt`, creates `User`, returns JWT.
- User login (`POST /auth/login`) checks credentials, returns JWT.
- User profile (`GET /auth/me`) validates JWT Bearer token and returns user profile.
- Client token storage (`localStorage.getItem("datanova_access_token")`) and authorization headers in `services/api.js`.
- Client route guarding with `ProtectedRoute`.

### Deficiencies & Non-Working Elements
- **OAuth / Google Infrastructure:** Completely absent. `app/auth/oauth_service.py` is 0 bytes. No OAuth routes exist.
- **Passwordless Login:** No infrastructure or endpoints exist.
- **Chat Endpoint Isolation:** `/chat/` does not verify user identity. Anyone with network access can post messages.

---

## 9. AI & Data Analysis Status

### Working Capabilities
- Dataset Profiling: Computes row counts, column counts, null values, data types, and numerical summaries.
- Code Generation Tools: Groq-backed generation for Python, SQL, code explanation, debugging, optimization, and conversion.
- Machine Learning Workflows: Full pipeline (`analyze_dataset` -> `train_model` -> `evaluate_model`) executes and saves `models/latest_model.pkl`.
- Visualizations: Generates Matplotlib/Seaborn scatter plots, bar charts, boxplots, histograms, and heatmaps.

### AI Issues Identified
1. **Target Extraction Bug in MLAgent:**
   - File: `backend/app/services/agents/ml_agent.py`
   - Component: `extract_target` & `execute`
   - Current behavior: Sorts dataset columns by length descending and checks substring containment in user message.
   - Problem: In query `"Predict the salary for Age 29 and Experience 5"`, `"Experience"` (10 chars) matches before `"Salary"` (6 chars), misidentifying the target as `"Experience"`.
   - Required fix: Respect target from `task.input_data` or `_previous_results` first, parse grammar/intent, and avoid naive length-based string search.
   - Priority: HIGH
2. **Planner Misclassification of Code Queries:**
   - File: `backend/app/core/planner/planner_agent.py` & `app/prompts/planner_prompt.py`
   - Component: Planner intent classification
   - Current behavior: Code generation requests without explicit datasets (e.g., `"Generate SQL for employees..."`) get assigned to `data_question`.
   - Problem: `DataQueryAgent` fails with `"Please upload a dataset first."` instead of executing `generate_sql`.
   - Required fix: Update planner rules to direct pure SQL/Python/conversion queries to code generation tools when no dataset is present.
   - Priority: HIGH
3. **Groq Model Identifier Fallback:**
   - File: `backend/app/services/llm_service.py`
   - Component: `LLMService.MODEL`
   - Current behavior: Set to `"openai/gpt-oss-120b"`.
   - Problem: Non-standard model ID; works on Groq API currently but prone to deprecation.
   - Required fix: Align with official supported Groq model identifiers (e.g. `llama-3.3-70b-versatile`).
   - Priority: MEDIUM

---

## 10. Persistence Status

| Item | Survives Refresh? | Where It Is Stored | Notes / Problems |
| :--- | :--- | :--- | :--- |
| **Authentication** | **YES** | `localStorage` (`datanova_access_token`) | Verified via `/auth/me`. |
| **Selected Project** | **YES** | `localStorage` (`datanova_project`) | Restored via `ProjectContext`. |
| **Project List** | **YES** | SQLite (`projects` table) | Fetched via `GET /projects`. |
| **Uploaded Datasets** | **PARTIAL** | Files on disk + SQLite (`datasets` table) | DB record exists, but React `DatasetContext` loses state on refresh; `Datasets.jsx` does not query project datasets. |
| **Conversations** | **NO** | Volatile in-memory `SessionManager` | Not saved to DB; lost on refresh or server restart. |
| **Messages** | **NO** | React `useState` & in-memory `SessionManager` | Zero rows in `messages` table; lost on refresh. |
| **Analyses** | **NO** | None | Zero rows in `analyses` table. |
| **Charts** | **NO** | PNG files on disk | Files exist in `outputs/charts/`, but metadata not stored in `charts` table or restored on client. |

---

## 11. File Storage Status

1. **Uploaded Datasets:**
   - *Current Storage:* Saved to relative path `uploads/{uuid}_{filename}` in current working directory.
   - *Issue:* Inconsistent location depending on whether server is started from root or `backend/`.
   - *Production Recommendation:* Use persistent cloud object storage (AWS S3, GCP Cloud Storage) with pre-signed URLs.
2. **Generated Charts:**
   - *Current Storage:* Saved to `backend/outputs/charts/{uuid}.png`.
   - *Issue:* Over 180 chart files are tracked in Git.
   - *Production Recommendation:* Store in cloud object storage or clean temp cache directory; ignore from Git.
3. **Generated Reports:**
   - *Current Storage:* Saved to `backend/static/reports/datanova_report_{timestamp}.html`.
   - *Issue:* Folder is not mounted as a static endpoint in FastAPI; files cannot be accessed over HTTP.
4. **Trained ML Models:**
   - *Current Storage:* Saved to `backend/models/latest_model.pkl`.
   - *Issue:* Overwrites a single file; committed to Git.
   - *Production Recommendation:* Version model artifacts per project/user in storage bucket.

---

## 12. Security Issues

1. **Unprotected Chat Endpoint:**
   - File: `backend/app/api/chat.py`
   - Problem: No authentication guard. Any client can trigger costly Groq LLM queries.
   - Fix: Add `get_current_user` dependency.
   - Priority: CRITICAL
2. **Hardcoded Fallback JWT Secret:**
   - File: `backend/app/services/jwt_service.py`
   - Problem: Uses fallback string `"datanova-development-secret-change-this"`.
   - Fix: Require explicit `JWT_SECRET_KEY` in production settings.
   - Priority: HIGH
3. **Committed Database & API Keys in Repository:**
   - File: `backend/datanova.db`, `backend/.env`
   - Problem: Live SQLite database with password hashes and live `.env` with Groq API key exist in local working tree.
   - Fix: Revoke/rotate exposed keys, ensure `.env` and `*.db` are strictly ignored by Git.
   - Priority: CRITICAL
4. **Permissive CORS Configuration:**
   - File: `backend/app/main.py`
   - Problem: Hardcoded `allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"]`.
   - Fix: Load allowed origins from environment settings.
   - Priority: MEDIUM

---

## 13. Git & Repository Issues

### Suspicious Tracked Files in Git Index (189 Files Identified)
The following files are currently committed or tracked in Git and should be removed from source control:
- `backend/datanova.db` (Committed SQLite database containing user and project data)
- `backend/models/latest_model.pkl` (44KB binary model pickle)
- `backend/outputs/charts/*.png` (180+ generated chart images)
- `backend/charts/histogram.png` (Orphaned chart image)
- `backend/response.json` (Scratch debug JSON dump)
- `backend/planner_backup.txt` (59KB temporary backup file)
- `backend/package-lock.json` (Erroneously placed in backend root)

### `.gitignore` Deficiencies
The root `.gitignore` is missing rules for:
- `*.db`, `*.sqlite`, `*.sqlite3`
- `backend/outputs/`
- `backend/charts/`
- `backend/models/*.pkl`
- `backend/static/reports/`
- `response.json`
- `*_backup.txt`

---

## 14. UX Issues

1. **Lost Context on Page Reload:**
   - Navigating away from `/workspace` or reloading the browser completely resets conversation history and unloads the active dataset from the UI.
2. **Non-Functional Quick Prompts in Conversation:**
   - Suggestion chips rendered inside `ChatMessages` do not populate the composer when clicked due to the event structure mismatch.
3. **Disorienting Empty Placeholders:**
   - Clicking "Reports", "Datasets", or "Tasks" in the sidebar leads to barren stub screens with no data, even if the user has uploaded datasets or run analyses.
4. **Mock Recent Analysis in Sidebar:**
   - Sidebar displays hardcoded dummy analysis names that do not link to real projects.
5. **No Loading Indicator on Code Generation / ML Training:**
   - Multi-step ML tasks can take 5-10 seconds; user only sees generic loading state without step progression.

---

## 15. Deployment Status

- **Docker:** `backend/Dockerfile` is 0 bytes. `docker/` directory contains only `.gitkeep`. Containerization is not implemented.
- **Deployment Scripts:** `deployment/` contains only `.gitkeep`.
- **Environment Configuration:** No centralized environment template. Backend `.env.example` is 0 bytes.
- **Production Asset Build:** Frontend Vite build succeeds, but client chunk size exceeds 600kB without dynamic code splitting.

---

## 16. Remaining Work

1. **Backend Route Cleanup & Consolidation:**
   - Eliminate duplicate imports in `main.py`.
   - Remove duplicate auth services in `backend/app/auth/`.
   - Delete 0-byte dummy route files.
2. **Database Persistence for Chat & Workspace:**
   - Link chat endpoint to `conversations` and `messages` tables.
   - Implement conversation list and message history retrieval APIs.
   - Automatically restore latest conversation on `/workspace`.
3. **Dataset Restoration on Project Selection:**
   - Implement `GET /projects/{id}/active-dataset` or connect `DatasetContext` to `getProjectDatasets`.
4. **Fix Agent Intent & Classification Bugs:**
   - Fix `MLAgent.extract_target` to prevent column length matching bugs.
   - Fix `PlannerAgent` routing for standalone code generation prompts.
5. **Fix Frontend Prompt Event Bug:**
   - Unify `datanova:prompt` custom event detail format.
6. **Git Cleanup & `.gitignore` Hardening:**
   - Untrack `datanova.db`, model pickles, and generated chart PNGs.
   - Update `.gitignore`.
7. **Complete Reports & Tasks Views:**
   - Implement report listing/viewing and task audit logging.

---

## 17. Recommended Implementation Order

### Phase 1: High-Priority Fixes & Cleanups (No Architecture Changes)
1. Fix `Mainlayout.jsx` file casing in Git index to protect Linux/Docker builds.
2. Fix UTF-16LE encoding of `backend/requirements.txt`.
3. Fix CustomEvent bug in `ChatMessages.jsx` so suggestion chips function.
4. Fix `MLAgent.extract_target` logic to correctly prioritize target columns.
5. Remove duplicate route imports in `backend/app/main.py` and mount `/static`.

### Phase 2: Database Persistence & User Isolation
1. Authenticate `/chat/` with `get_current_user` and validate project ownership.
2. Implement conversation and message persistence in `chat.py` saving to `conversations` and `messages` tables.
3. Add backend endpoints:
   - `GET /projects/{project_id}/conversations`
   - `GET /projects/{project_id}/conversations/{conversation_id}/messages`
4. Update `DatasetContext` and `ChatContext` to load active project data from database on mount.

### Phase 3: Git & Repository Sanitization
1. Update `.gitignore` with database, chart output, model artifact, and temporary file rules.
2. Untrack (using `git rm --cached`) `datanova.db`, `latest_model.pkl`, and 180+ chart PNGs without deleting local files.

### Phase 4: Feature Completion
1. Implement real dataset listing in `Datasets.jsx`.
2. Connect `Reports.jsx` to list and view exported HTML reports.
3. Populate `Sidebar.jsx` recent items dynamically from active user projects.
4. Prepare clean Dockerfile and production configuration.
