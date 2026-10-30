# DataNova AI — REST API Reference

All backend API endpoints are hosted by FastAPI at `http://localhost:8000`. Authenticated requests require the `Authorization: Bearer <token>` header.

---

## 1. Authentication (`/auth`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `POST` | `/auth/signup` | Register a new user account | No |
| `POST` | `/auth/login` | Authenticate user credentials and issue 24-hour JWT | No |
| `POST` | `/auth/demo` | Authenticate as one-click demo user (`demo@datanova.ai`) | No |
| `POST` | `/auth/guest` | Issue temporary guest session token (ID: 0, ephemeral) | No |
| `POST` | `/auth/refresh` | Renew existing JWT token without re-login | Bearer Token |
| `GET` | `/auth/me` | Fetch authenticated user profile | Bearer Token |

---

## 2. Projects & Datasets (`/projects`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `GET` | `/projects` | List all projects owned by the authenticated user | Bearer Token |
| `POST` | `/projects` | Create a new project (restricted for guest users) | Bearer Token |
| `GET` | `/projects/{id}` | Retrieve project details by ID | Bearer Token |
| `DELETE` | `/projects/{id}` | Delete a project and its associated artifacts | Bearer Token |
| `POST` | `/projects/{id}/datasets/upload` | Upload and register CSV/XLSX/JSON dataset | Bearer Token |
| `GET` | `/projects/{id}/datasets` | List all datasets associated with a project | Bearer Token |
| `GET` | `/projects/{id}/datasets/{dataset_id}/analysis` | Compute on-demand profiling and quality metrics | Bearer Token |
| `DELETE` | `/projects/{id}/datasets/{dataset_id}` | Remove a dataset from a project | Bearer Token |

---

## 3. Conversational AI & Orchestration (`/chat`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `POST` | `/chat` | Submit conversational inquiry or analysis request | Bearer Token |
| `GET` | `/projects/{id}/conversations` | Retrieve project conversation list | Bearer Token |
| `GET` | `/projects/{id}/conversations/{conv_id}/messages` | Retrieve chronological message history | Bearer Token |

---

## 4. Reports, Visualizations & Tasks

| Method | Endpoint | Description | Auth Required |
|---|---|---|:---:|
| `POST` | `/projects/{id}/reports/generate` | Generate executive HTML report for a dataset | Bearer Token |
| `GET` | `/projects/{id}/reports` | List generated HTML reports | Bearer Token |
| `GET` | `/projects/{id}/reports/{report_id}/view` | View generated HTML report in browser | Bearer Token |
| `GET` | `/projects/{id}/analyses` | Retrieve historical analysis records | Bearer Token |
| `GET` | `/projects/{id}/charts` | Retrieve project chart metadata | Bearer Token |
| `GET` | `/projects/{id}/tasks` | Retrieve real execution task audit log | Bearer Token |
