# DataNova AI — Production Deployment Guide

This guide details the verified deployment pathways for DataNova AI, with explicit handling for persistent storage (SQLite, uploaded datasets, charts, reports, and machine learning models).

---

## 1. Storage Architecture & Ephemeral Hosting Warning

> [!WARNING]
> **CRITICAL STORAGE WARNING: Do not deploy DataNova AI to ephemeral containers without a persistent disk!**  
> DataNova AI stores relational records in SQLite (`datanova.db`), uploaded files in `uploads/`, rendered visualizations in `outputs/charts/`, and generated HTML reports in `static/reports/`.  
> Standard free-tier serverless or container platforms (e.g., basic Heroku dynos, free Render web services without disks, Vercel serverless functions) have ephemeral filesystems that **wipe all files on restart, sleep, or redeployment**.

To prevent data loss, DataNova AI supports a dedicated `DATA_DIR` configuration:
- When `DATA_DIR` is set (e.g. `DATA_DIR=/data`), the backend automatically anchors `datanova.db`, `/uploads/`, `/outputs/charts/`, and `/static/reports/` inside that single directory.
- Mounting a single persistent volume or disk to `DATA_DIR` ensures all projects, datasets, chats, and reports survive restarts.
- Alternatively, if you wish to use managed cloud databases, set `DATABASE_URL=postgresql://user:pass@host:5432/dbname` (PostgreSQL driver `psycopg2-binary` is already pre-installed).

---

## 2. Environment Variables Specification

### Backend Variables

| Variable | Required | Default (Dev) | Production Description |
| :--- | :---: | :--- | :--- |
| `GROQ_API_KEY` | Optional* | `""` | Free Groq Cloud LLM API key from [console.groq.com](https://console.groq.com/keys). Fallback heuristics operate if unset. |
| `JWT_SECRET_KEY` | **Yes** | Dev fallback | 64-char random hex string used to sign session tokens. Generate via `openssl rand -hex 32`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Optional | `60` | Duration of user session token in minutes (e.g. `120`). |
| `ALLOWED_ORIGINS` | **Yes** | Localhost | Comma-separated list of public frontend domains without trailing slashes (e.g. `https://datanova.yourdomain.com`). |
| `DATABASE_URL` | Optional | `sqlite:///datanova.db` | Connection string. For persistent disk: `sqlite:////data/datanova.db`. For Postgres: `postgresql://...`. |
| `DATA_DIR` | **Yes** (in container) | `""` | Directory mounted to persistent storage (e.g. `/data` or `/var/data`). |
| `ENVIRONMENT` | Optional | `development` | Set to `production` in production environments. |
| `PORT` | Optional | `8000` | Port listened to by Uvicorn (assigned dynamically by Render/Railway/Heroku). |

### Frontend Variables

| Variable | Required | Default (Dev) | Production Description |
| :--- | :---: | :--- | :--- |
| `VITE_API_URL` | **Yes** | `http://127.0.0.1:8000` | The public HTTPS URL of the deployed FastAPI backend (e.g. `https://api.datanova.yourdomain.com`). No trailing slash. |

---

## 3. Hosting Pathways

### Pathway A: Docker Compose on VPS (DigitalOcean / AWS EC2 / Hetzner)

This is the most cost-effective and self-contained approach.

1. **Clone repository on VPS**:
   ```bash
   git clone https://github.com/your-username/DataNova-AI.git
   cd DataNova-AI
   ```
2. **Create production `.env`**:
   ```bash
   cp backend/.env.example .env
   ```
   Generate a secret key:
   ```bash
   openssl rand -hex 32
   ```
   Fill in `.env`:
   ```env
   GROQ_API_KEY=gsk_...
   JWT_SECRET_KEY=<generated-key>
   ALLOWED_ORIGINS=https://your-domain.com,http://your-domain.com
   VITE_API_URL=https://api.your-domain.com
   DATA_DIR=/data
   ENVIRONMENT=production
   ```
3. **Start services with Docker Compose**:
   ```bash
   docker compose up -d --build
   ```
4. **Verify running containers**:
   ```bash
   docker compose ps
   curl http://localhost:8000/health
   ```
   The named volume `datanova_persistent_data` permanently persists your SQLite database and all uploaded files across container rebuilds.

---

### Pathway B: Render (Web Service with Persistent Disk + Static Site)

Render natively supports both persistent disks and automated Blueprints.

1. **Push your repository to GitHub / GitLab**.
2. **Log into Render Dashboard** ([render.com](https://render.com)).
3. **Deploy via Blueprint**:
   - Click **New +** → **Blueprint**.
   - Connect your repository.
   - Render will read [`render.yaml`](file:///d:/DataNova-AI/render.yaml) automatically, provisioning:
     - A FastAPI Web Service with an attached 10 GB Persistent Disk mounted at `/data`.
     - A React frontend Static Site.
4. **Configure Secrets**:
   - In the `datanova-backend` dashboard, set `GROQ_API_KEY` (if using Groq).
   - In the `datanova-backend` dashboard, set `ALLOWED_ORIGINS` to the URL of the static site.
   - In the `datanova-frontend` dashboard, ensure `VITE_API_URL` matches your backend URL (e.g., `https://datanova-backend.onrender.com`).
5. **Trigger Deploy**:
   - Both services build and deploy. Persistent Disk maintains your data indefinitely.

---

### Pathway C: Split Hosting (Vercel / Cloudflare Pages + Railway with Volume)

1. **Frontend on Vercel**:
   - Import `frontend/` folder into Vercel.
   - Framework Preset: **Vite**.
   - Root Directory: `frontend`.
   - Build Command: `npm run build`.
   - Output Directory: `dist`.
   - Environment Variable: `VITE_API_URL=https://your-railway-app.up.railway.app`.
2. **Backend on Railway**:
   - New Project → Deploy from GitHub repo.
   - Root Directory: `backend`.
   - Add Volume: Mount volume to `/data`.
   - Set Environment Variables:
     - `DATA_DIR=/data`
     - `JWT_SECRET_KEY=<secure-random-secret>`
     - `ALLOWED_ORIGINS=https://your-vercel-site.vercel.app`
     - `ENVIRONMENT=production`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 4. Pre-Flight Verification Checklist

Before opening the platform to users, execute these checks:

- [ ] `GET /health` on the backend returns `{"status": "Healthy", "database": "connected"}` with HTTP 200.
- [ ] `GET /` on the backend returns status 200 without exposing sensitive environment keys.
- [ ] Unauthenticated requests to private routes (e.g. `GET /projects`) receive HTTP 401.
- [ ] User signup (`POST /auth/signup`) and login (`POST /auth/login`) issue valid JWT tokens.
- [ ] Uploading a dataset creates the physical file in the persistent data volume (`/data/uploads`).
- [ ] Generating an executive report creates the report in `/data/static/reports` and allows viewing via authenticated Blob URL.
- [ ] CORS is restricted to your frontend domain; browser console shows no CORS pre-flight errors.
