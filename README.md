# PrivAI – Privacy‑First College AI (MVP)

PrivAI is a privacy‑first AI assistant for colleges. All processing happens locally, enabling secure document upload, ingestion (chunk → embed → FAISS), and retrieval‑augmented chat.

This README is the developer quickstart for running, developing, and packaging the PrivAI MVP.


## 1) Prerequisites
- Python 3.11+
- Node.js 18+ and npm 8+
- Git
- (Optional) Docker & Docker Compose v2


## 2) Folder Structure
```
privai-app/
├─ backend/                  # FastAPI backend
│  ├─ app/
│  │  ├─ api/               # Upload, connect-db, ingest, chat
│  │  ├─ core/              # chunker, embeddings, vector_db, rag, config, logging
│  │  ├─ main.py            # Full app entry
│  │  └─ main_simple.py     # Simplified app (no heavy deps)
│  ├─ uploads/              # Uploaded files (mounted in docker-compose)
│  ├─ data/faiss_index/     # FAISS persistence (mounted in docker-compose)
│  ├─ requirements.txt
│  ├─ run.py                # Uvicorn runner
│  └─ Dockerfile
│
├─ frontend/                # React + Tailwind front-end (CRA)
│  ├─ src/                  # Components, pages, hooks, utils
│  ├─ public/
│  ├─ package.json
│  └─ Dockerfile            # Multi-stage build (nginx)
│
├─ electron-app/            # Desktop wrapper (Electron)
│  ├─ src/ (main.js, preload.js)
│  ├─ scripts/ (build/dev/package)
│  └─ assets/
│
├─ samples/                 # Demo dataset & scripts
│  ├─ students.csv
│  ├─ marks.csv
│  ├─ feedback.csv
│  ├─ policies.pdf / NAAC_criteria.pdf (via generate_pdfs.py)
│  ├─ sample_queries.txt
│  └─ README_samples.md
│
├─ docker-compose.yml       # Backend + Frontend (dev) composition
├─ DOCKER.md                # Docker usage guide
└─ README.md                # This file
```


## 3) Backend – Python Setup
### Create virtual environment
```bash
cd privai-app/backend
python -m venv venv --upgrade-deps

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### Install dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Run FastAPI (simplified, minimal deps)
```bash
python -m app.main_simple
# Server: http://localhost:8000
# Docs:   http://localhost:8000/docs
```

### Run FastAPI (full stack)
```bash
python -m app.main
# Requires additional deps like faiss-cpu, sentence-transformers
```


## 4) Frontend – React Setup
```bash
cd privai-app/frontend
npm install
npm start
# App: http://localhost:3000
```
If `react-scripts` is missing, install:
```bash
npm install react-scripts --save
```


## 5) Upload Sample Data → Ingest → Chat
### Generate PDFs (if not present)
```bash
cd privai-app/samples
python generate_pdfs.py
```

### Upload files (CSV + PDF)
```bash
# from repo root (adjust paths if needed)
curl -F "file=@samples/students.csv" http://localhost:8000/upload/
curl -F "file=@samples/marks.csv" http://localhost:8000/upload/
curl -F "file=@samples/feedback.csv" http://localhost:8000/upload/
curl -F "file=@samples/policies.pdf" http://localhost:8000/upload/
curl -F "file=@samples/NAAC_criteria.pdf" http://localhost:8000/upload/
```

### Start ingestion
```bash
curl -X POST http://localhost:8000/ingest/
```

### Ask queries (examples)
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"query": "List students with unpaid fees this semester"}'

curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize placement feedback 2024"}'
```
See more in `samples/sample_queries.txt`.


## 6) Docker Compose (Dev)
```bash
cd privai-app
# create .env with DB creds (see DOCKER.md)
docker compose build
docker compose up
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```
Volumes (host → container):
- `./backend/uploads` → `/app/uploads`
- `./backend/data/faiss_index` → `/app/data/faiss_index`

Switch to production frontend (nginx) as shown in `DOCKER.md`.


## 7) Electron Desktop (Optional)
```bash
cd privai-app/electron-app
npm install
npm run dev  # starts backend, frontend, and Electron in dev
# or
npm run build && npm run dist
```


## 8) Troubleshooting
### Backend
- `ModuleNotFoundError: fastapi` → `pip install fastapi uvicorn python-multipart structlog`
- `pdfplumber / pandas / python-docx missing` → optional for testing; install as needed.
- Port 8000 busy → change port or free it:
```bash
# Windows
netstat -ano | findstr :8000
TASKKILL /PID <PID> /F
```

### Frontend
- `react-scripts not recognized` → `npm install react-scripts --save`
- Port 3000 busy → change port `set PORT=3001 && npm start` (Windows) or `PORT=3001 npm start` (Unix)

### Docker
- File sharing on Windows: enable drive sharing in Docker Desktop.
- Frontend can’t reach backend → confirm `REACT_APP_API_URL=http://backend:8000` in compose env.

### PDFs generation
- `reportlab` missing → `pip install reportlab`


## 9) API Quick Reference
- `POST /upload/` (multipart) → upload PDF/CSV/DOCX
- `POST /connect-db/` (json) → `{ "db_url": "..." }`
- `POST /ingest/` → chunk → embed → store
- `POST /chat/` (json) → `{ "query": "..." }`
- `GET /health` → `{ status, version, uptime }`


## 10) Screens / CLI
```text
Backend start (simplified):
  INFO:     Started server process [12345]
  INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

Upload example:
  curl -F "file=@samples/students.csv" http://localhost:8000/upload/
  {"status":"success","message":"File students.csv uploaded successfully","file_id":"file_..."}

Ingestion example:
  curl -X POST http://localhost:8000/ingest/
  {"status":"success","message":"Data ingestion completed successfully","chunks_processed":10}

Chat example:
  curl -X POST http://localhost:8000/chat/ -H "Content-Type: application/json" -d '{"query":"What is PrivAI?"}'
  {"answer":"Mock response...","sources":[],"metadata":{...}}
```


## 11) Notes
- The simplified backend (`main_simple.py`) returns mock chat answers but exercises the full flow and APIs.
- The full pipeline (`main.py` + `core/*`) supports chunking, embeddings (`sentence-transformers`), FAISS storage, and RAG chat when optional deps are installed.
- All data is processed locally. No cloud calls by default.
