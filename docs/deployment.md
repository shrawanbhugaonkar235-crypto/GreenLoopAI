# GreenLoopAI — Deployment & Operations Guide

## 1. System Requirements
* **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 22.04+).
* **Python**: 3.10+ (Installed with virtualenv).
* **Java**: OpenJDK 17 or Eclipse Temurin 17.
* **Maven**: 3.8+ (for building Spring Boot).
* **Database**: PostgreSQL 15+ (or SQLite for local single-node development).
* **Docker & Docker Compose** (Optional, for containerized deployment).

---

## 2. Option A: Local Bare-Metal Execution (Recommended for Viva/Evaluation)

### Step 1: Start PostgreSQL (Optional) / SQLite is pre-configured
If running PostgreSQL locally:
```powershell
# Create database
CREATE DATABASE greenloop_db;
```

### Step 2: Start the AI Service (FastAPI)
```powershell
cd ai-service
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
* Interactive API Documentation (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
* Health Status: [http://localhost:8000/health](http://localhost:8000/health)

### Step 3: Start the Security Gateway (Spring Boot)
```powershell
cd security-service
mvn spring-boot:run
```
* Security Gateway runs at: [http://localhost:8080](http://localhost:8080)

### Step 4: Open Frontend Application
Simply open `frontend/index.html` in any modern web browser or serve via:
```powershell
cd frontend
python -m http.server 3000
```
Open [http://localhost:3000](http://localhost:3000).

---

## 3. Option B: Docker Compose Deployment

```powershell
# In project root directory:
docker-compose up --build -d
```

### Services Overview
* **Frontend UI**: [http://localhost:3000](http://localhost:3000)
* **Spring Security Gateway**: [http://localhost:8080](http://localhost:8080)
* **FastAPI AI Engine & Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **PostgreSQL Database**: `localhost:5432` (`greenloop_db`)

---

## 4. Environment Variables Reference

| Variable | Service | Default | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | AI Service | `sqlite:///./greenloop.db` | PostgreSQL or SQLite connection URI |
| `OPENAI_API_KEY` | AI Service | `None` | OpenAI API key for real AI Assistant |
| `OPENAI_MODEL` | AI Service | `gpt-4o-mini` | Model name for chat responses |
| `YOLO_MODEL_PATH` | AI Service | `models/yolov8n.pt` | Path to YOLO weights |
| `FASTAPI_SERVICE_TOKEN` | Gateway & AI | `dev-internal-secret-token` | Internal security communication token |
| `FRONTEND_ORIGIN` | Gateway | `http://localhost:3000` | Allowed CORS origins |
