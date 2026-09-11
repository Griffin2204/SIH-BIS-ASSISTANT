# BIS Assistant Production Deployment Guide

This document provides complete instructions for preparing, configuring, and deploying the AI-powered BIS Assistant system into production environments.

---

## 1. System Architecture & Persistence Strategy

The system consists of two primary services:
1. **Frontend**: React + Vite SPA, served via Nginx in production.
2. **Backend**: FastAPI API service hosting the multilingual RAG engine, document processing, and vector search.

### Critical Persistence Requirements
The backend state is persisted in two directories:
- **`backend/documents/uploads/`** (Configurable via `UPLOAD_DIR`): Holds uploaded PDF, DOCX, and TXT source documents.
- **`backend/vector_store/`** (Configurable via `CHROMA_PERSIST_DIRECTORY`): Holds ChromaDB's SQLite database (`chroma.sqlite3`) and HNSW vector index files.

> [!WARNING]
> **Ephemeral Container Storage Risk**:
> In standard stateless cloud containers (e.g. serverless containers or basic container dynos without persistent disks), any files written to local disk are lost upon container restart or redeployment.

### Recommended Production Architecture:
- **Persistent Disk / Volume Mount**: Mount a persistent block volume to the container (e.g. `/data`) and configure:
  - `UPLOAD_DIR=/data/uploads`
  - `CHROMA_PERSIST_DIRECTORY=/data/vector_store`
- This ensures all ChromaDB embeddings and source files survive redeployments without needing to migrate to an external vector database.

---

## 2. Environment Variables Reference

### Backend Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `HOST` | String | `0.0.0.0` | Network binding interface. |
| `PORT` | Integer | `8000` | Port for the backend server to listen on. |
| `ENVIRONMENT` | String | `development` | Set to `production` in production environments (disables CORS wildcards). |
| `UPLOAD_DIR` | String | `./documents/uploads` | Path to store uploaded document files (mount to persistent disk in production). |
| `CHROMA_PERSIST_DIRECTORY` | String | `./vector_store` | Path where ChromaDB persists vector tables (mount to persistent disk in production). |
| `CHROMA_COLLECTION_NAME` | String | `bis_documents_multilingual` | Name of the active ChromaDB vector collection. |
| `CORS_ALLOWED_ORIGINS` | String | `http://localhost:5173,...` | Comma-separated list of allowed frontend origins (e.g., `https://assistant.example.com`). |
| `LLM_PROVIDER` | String | `gemini` | LLM backend provider (`gemini` or `openai`). |
| `LLM_MODEL` | String | `gemini-2.5-flash` | LLM model identifier. |
| `LLM_API_KEY` | String | (None) | Secret API key for Google Gemini or OpenAI. Never commit to source control. |
| `MULTILINGUAL_ENABLED` | Boolean | `true` | Enables multilingual embedding model & query routing. |
| `MULTILINGUAL_EMBEDDING_MODEL` | String | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Multilingual embedding model. |
| `RATE_LIMIT_ENABLED` | Boolean | `true` | Toggles in-memory sliding-window rate limiting. |
| `RATE_LIMIT_MAX_REQUESTS` | Integer | `30` | Maximum requests allowed per IP within the rate limit window. |
| `RATE_LIMIT_WINDOW_SECONDS` | Integer | `60` | Duration of the rate limit sliding window in seconds. |

### Frontend Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | String | `http://127.0.0.1:8000` (dev) / `""` (prod) | Backend API endpoint URL. In reverse-proxied production environments, leave blank to use same-origin relative URLs. |

---

## 3. Docker & Docker Compose Deployment

### Option A: Complete Multi-Container Stack (Recommended for VM / VPS)

1. Clone repository on production host.
2. Set your environment variables in `.env` or pass them directly:
   ```bash
   export LLM_API_KEY="your_production_gemini_key"
   ```
3. Launch services using Docker Compose:
   ```bash
   docker compose up -d --build
   ```
4. Verification:
   - Frontend is available at `http://<host-ip>/` (port 80).
   - Backend API is available at `http://<host-ip>:8000/`.
   - Volumes `bis_uploads` and `bis_vector_store` ensure persistent document and vector storage across container rebuilds.

### Option B: Independent Backend Container

Build and run backend container with a volume mount:
```bash
docker build -t bis-assistant-backend ./backend

docker run -d \
  --name bis-backend \
  -p 8000:8000 \
  -v /var/data/bis_uploads:/data/uploads \
  -v /var/data/bis_vectors:/data/vector_store \
  -e ENVIRONMENT=production \
  -e CORS_ALLOWED_ORIGINS="https://my-frontend-domain.com" \
  -e LLM_PROVIDER=gemini \
  -e LLM_API_KEY="your_api_key_here" \
  bis-assistant-backend
```

---

## 4. Cloud Platform Deployment Recommendations

### 1. Railway / Render / Fly.io (Single-service or PaaS)
- **Backend Service**:
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Attach a **Persistent Volume** mounted at `/data`.
  - Set environment variables:
    - `UPLOAD_DIR=/data/uploads`
    - `CHROMA_PERSIST_DIRECTORY=/data/vector_store`
    - `CORS_ALLOWED_ORIGINS=https://your-frontend-app.vercel.app`
- **Frontend Service**:
  - Deploy to Vercel, Netlify, or Cloudflare Pages.
  - Set build environment variable: `VITE_API_BASE_URL=https://your-backend-app.railway.app`.

### 2. AWS / GCP Container Deployment
- **AWS**: Deploy backend as an ECS Fargate task with an attached **Amazon EFS** (Elastic File System) volume mounted to `/data`.
- **GCP**: Deploy to Cloud Run with **Cloud Storage FUSE Volume Mount** or GCE VM with persistent SSD.

---

## 5. Pre-Deployment Verification Checklist

- [x] All 38 automated security & functional tests pass (`test_phase13.py`).
- [x] All 125 backward regression tests pass (Phases 9, 10, 11, 12).
- [x] Frontend builds cleanly without TypeScript or bundling warnings (`npm run build`).
- [x] No API keys, secret tokens, or private credentials committed to Git.
- [x] Production CORS configuration restricts origins and disallows wildcard `*`.
- [x] Rate limiting active on expensive endpoints (`/ask`, `/retrieve`, `/bis/search`, `/documents/upload`).
- [x] Security headers active on all API responses (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Cache-Control`).
- [x] Local filesystem paths and raw embeddings redacted from all client responses.
