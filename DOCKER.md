# PrivAI Docker Setup

This docker-compose configuration runs the PrivAI MVP locally with:
- backend: FastAPI on port 8000
- frontend: React app on port 3000

The setup mounts local volumes for uploads and FAISS index so your data persists across container restarts.

## Prerequisites
- Docker 20+
- Docker Compose v2

## Environment Variables
Create a `.env` file at the project root (same folder as `docker-compose.yml`) with your DB credentials and settings:

```
# Database (read-only recommended)
DB_URL=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=

# App
PRIVAI_DEBUG=false
OPENAI_API_KEY=
```

Notes:
- If you don't need a database, you can leave DB values empty. The backend will still run.
- `REACT_APP_API_URL` for the frontend is set in the compose file to target the `backend` service via Docker DNS.

## Build & Run

### 1) Build images
```
docker compose build
```

### 2) Start services
```
docker compose up
# or in background
docker compose up -d
```

### 3) Open the apps
- Backend API: http://localhost:8000 (docs at /docs)
- Frontend UI (dev server): http://localhost:3000

### 4) Stop services
```
docker compose down
```

## Volumes & Persistence
The following host folders are mounted into the backend container:
- `./backend/uploads` -> `/app/uploads` (stores uploaded files)
- `./backend/data/faiss_index` -> `/app/data/faiss_index` (stores FAISS index files)

These ensure data persists between container restarts.

## Production Notes
- For production, build the frontend image and run it behind nginx. You can swap the `frontend` service to use the Dockerfile provided in `frontend/Dockerfile` instead of the Node dev server:

```
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  ports:
    - "3000:80"  # nginx serves on 80 inside container
  environment:
    - REACT_APP_API_URL=http://backend:8000
  depends_on:
    backend:
      condition: service_healthy
```

- Consider removing the source bind-mounts and using named volumes or COPY-only images for immutability in prod.

## Troubleshooting
- If port 3000/8000 is already in use, change the left-hand side of the port mappings in `docker-compose.yml`.
- Windows users: ensure file sharing is enabled for the drive to allow bind mounts.
- If the frontend cannot reach the backend, verify `REACT_APP_API_URL=http://backend:8000` and backend health.
