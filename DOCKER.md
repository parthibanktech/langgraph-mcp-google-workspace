# 🐳 Docker & Docker Compose Deployment Guide

This guide details how to build, run, and manage the **Gmail & Google Drive MCP Server** project using **Docker** and **Docker Compose**.

---

## 🏗️ Container Architecture

The containerized environment consists of two isolated, orchestrated services on a custom bridge network (`mcp-network`):

```
                     ┌─────────────────────────────────────────┐
                     │             Docker Host                 │
                     │                                         │
  Port 5173 ─────────► [ mcp_frontend ] (Nginx + React SPA)   │
                     │          │                              │
                     │          │ Reverse Proxy /api/*         │
                     │          ▼                              │
  Port 8000 ─────────► [ mcp_backend ] (FastAPI Python App)   │
                     │          │                              │
                     │          ├── Volume: credential.json    │
                     │          ├── Volume: token.json         │
                     │          └── Volume: logs/              │
                     └─────────────────────────────────────────┘
```

1. **`mcp_backend`**:
   - **Base**: `python:3.11-slim`
   - **Port**: `8000:8000` (FastAPI REST API & Interactive Swagger UI at `http://localhost:8000/docs`)
   - **Volumes**: Persists Google OAuth tokens and audit logs.
   - **Healthcheck**: Periodically probes `/health`.

2. **`mcp_frontend`**:
   - **Base**: Multi-stage build (`node:20-alpine` -> `nginx:alpine`)
   - **Port**: `5173:80` (React UI dashboard at `http://localhost:5173`)
   - **Reverse Proxy**: Nginx routes frontend `/api/` calls directly to `http://backend:8000`.

---

## ⚡ Quickstart Commands

### 1. Build and Start Containers

```bash
docker compose up --build -d
```

- `-d`: Runs containers in detached (background) mode.
- `--build`: Rebuilds Docker images with any fresh code changes.

---

### 2. Verify Service Status

```bash
docker compose ps
```

Expected Output:
```
NAME           IMAGE                        COMMAND                  SERVICE     CREATED         STATUS                   PORTS
mcp_backend    gmail_agent_backend          "uvicorn api:app --h…"   backend     10 seconds ago  healthy                  0.0.0.0:8000->8000/tcp
mcp_frontend   gmail_agent_frontend         "/docker-entrypoint.…"   frontend    5 seconds ago   Up 5 seconds             0.0.0.0:5173->80/tcp
```

---

### 3. Access Application Interfaces

- 🎨 **React UI Dashboard**: [http://localhost:5173](http://localhost:5173)
- 📚 **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🏥 **Backend Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### 4. View Container Logs

```bash
# Stream logs for all services
docker compose logs -f

# Stream logs for backend only
docker compose logs -f backend

# Stream logs for frontend only
docker compose logs -f frontend
```

---

### 5. Stop and Remove Containers

```bash
# Stop containers without deleting volumes
docker compose stop

# Stop and remove containers and network
docker compose down
```

---

## 🔒 Prerequisites & Credentials Mount

Ensure `backend/credential.json` and `backend/token.json` exist before running `docker compose up`. They are mounted read-only (`credential.json`) and read-write (`token.json`) into `/app/` inside the `mcp_backend` container.

```bash
gmail_agent_development/
├── backend/
│   ├── credential.json    <-- Required Google Service Account / OAuth credentials
│   └── token.json         <-- Generated user authentication token
```
