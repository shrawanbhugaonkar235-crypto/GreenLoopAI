# GreenLoopAI — AI-Powered Platform for Smart Waste Verification & Automated EPR Compliance

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Spring Boot](https://img.shields.io/badge/SpringBoot-3.2.0-6DB33F?logo=springboot)](https://spring.io/projects/spring-boot)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8n-blue?logo=ultralytics)](https://ultralytics.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **B.Tech Major Project** | Production-Structured Full-Stack Software Application
> 
> **Core Workflow**: `DETECT → VERIFY → REWARD → TRACK → COMPLY`

---

## 1. Executive Summary

**GreenLoopAI** is an enterprise-grade artificial intelligence platform that bridges citizen recycling actions with automated Extended Producer Responsibility (EPR) regulatory compliance.

Using computer vision (**YOLOv8**), optical character and barcode recognition (**EasyOCR / OpenCV**), image provenance analysis (**EXIF Authenticity**), and an immutable transaction ledger, GreenLoopAI automates the entire lifecycle:
1. **DETECT**: Real-time object identification and material taxonomy classification.
2. **VERIFY**: Multi-signal authenticity, brand matching, and composite verification scoring.
3. **REWARD**: Minting citizen **GreenCoins** through idempotent financial ledger transactions.
4. **TRACK**: Relational audit trails for municipal waste streams and collection history.
5. **COMPLY**: Generating regulatory-compliant EPR evidence certificates for brand producers (CPCB EPR standard).

---

## 2. Multi-Tier Architecture

```text
                                  CITIZEN / MUNICIPAL / PRODUCER / ADMIN
                                                    │
                                                    ▼
                                     ┌─────────────────────────────┐
                                     │      FRONTEND APPLICATION   │
                                     │                             │
                                     │  HTML5 + CSS3 + Vanilla JS  │
                                     │  Mobile-First Responsive UI │
                                     │  Role Context Switcher      │
                                     │  Bottom-Right AI Assistant  │
                                     └──────────────┬──────────────┘
                                                    │
                                                    │ HTTPS / REST (Port 8080)
                                                    ▼
                                     ┌─────────────────────────────┐
                                     │     SPRING BOOT GATEWAY     │
                                     │                             │
                                     │  Spring Security & JWT RBAC │
                                     │  Rate Limiter & Audit Log   │
                                     │  Security Headers & CORS    │
                                     │  Reverse Proxy to AI Engine │
                                     └──────────────┬──────────────┘
                                                    │
                                                    │ Internal Service Secret
                                                    ▼
                                     ┌─────────────────────────────┐
                                     │      FASTAPI AI ENGINE      │
                                     │                             │
                                     │  YOLOv8 Object Detection    │
                                     │  EasyOCR & Barcode Reader   │
                                     │  EXIF Authenticity Checker  │
                                     │  Composite Scoring Engine   │
                                     │  EPR Regulatory Processor   │
                                     │  OpenAI Responses Assistant │
                                     └──────────────┬──────────────┘
                                                    │
                      ┌─────────────────────────────┼─────────────────────────────┐
                      │                             │                             │
                      ▼                             ▼                             ▼
             ┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
             │   POSTGRESQL    │           │     YOLOv8      │           │     OPENAI      │
             │   DATABASE      │           │  Neural Weights │           │  Responses API  │
             │                 │           │                 │           │                 │
             │  SQLAlchemy ORM │           │  models/        │           │  Controlled     │
             │  Alembic Ledger │           │  yolov8n.pt     │           │  Context Only   │
             └─────────────────┘           └─────────────────┘           └─────────────────┘
```

---

## 3. Technology Stack

* **Frontend**: HTML5, CSS3, Vanilla JavaScript (No React/Vue/TS/Bootstrap/Tailwind). Lightweight, mobile-first responsive, 0 external runtime dependencies.
* **Security Gateway**: Java 17 + Spring Boot 3 + Spring Security + JWT Resource Server + Bucket4j Rate Limiter.
* **AI & Verification Engine**: Python 3.10+ + FastAPI + Ultralytics YOLOv8 + EasyOCR + OpenCV 5 + Pillow.
* **Database & ORM**: PostgreSQL 16 (or SQLite in local development) + SQLAlchemy 2.0 + Alembic Migrations.
* **AI Assistant**: OpenAI Responses API (`gpt-4o-mini`) with server-side secret management and controlled contextual prompts.

---

## 4. Role-Based Capabilities (RBAC)

| Role | Capabilities & Views |
| :--- | :--- |
| **`CITIZEN`** | Waste image verification, GreenCoins balance & transactions, own scan history, AI Assistant. |
| **`MUNICIPAL`** | City-wide category distribution, diversion metrics, municipal waste collection trends. |
| **`PRODUCER`** | Brand-specific recovery credits, EPR certificate auditing, compliance status verification. |
| **`ADMIN`** | System health diagnostics, security audit logs, database connection monitoring. |

---

## 5. Quick Start Runbook

### Option 1: Bare-Metal Local Run (Fastest for Viva Demo)

1. **Start FastAPI AI Backend**:
   ```powershell
   cd ai-service
   pip install -r requirements.txt
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   * Swagger OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

2. **Start Spring Boot Gateway**:
   ```powershell
   cd security-service
   mvn spring-boot:run
   ```
   * Security Gateway: [http://localhost:8080](http://localhost:8080)

3. **Launch Frontend Application**:
   Open `frontend/index.html` directly in your browser or run:
   ```powershell
   cd frontend
   python -m http.server 3000
   ```
   * Access UI: [http://localhost:3000](http://localhost:3000)

---

### Option 2: Docker Compose Orchestration

```powershell
docker-compose up --build -d
```

---

## 6. Automated Verification Test Suite

Run backend test verification:
```powershell
cd ai-service
python -m pytest -v
```
Output:
```text
======================= 15 passed, 6 warnings in 21.19s =======================
```

---

## 7. Project Documentation

Comprehensive documentation for faculty review and viva:
* [Architecture Design Document](docs/architecture.md)
* [Database Relational Design & ER Diagram](docs/database-design.md)
* [REST API Contract & Documentation](docs/api-documentation.md)
* [Multi-Stage Verification Pipeline Guide](docs/verification-pipeline.md)
* [Extended Producer Responsibility (EPR) Module](docs/epr-module.md)
* [Security, JWT & RBAC Guide](docs/security.md)
* [AI Assistant Architecture](docs/ai-assistant.md)
* [Deployment & Operations Guide](docs/deployment.md)
* [Testing & QA Strategy](docs/testing.md)

---

## 8. Viva Presentation Quick Reference

* **Why FastAPI for AI?** Asynchronous ASGI performance, native Pydantic schema validation, and high-throughput threadpool offloading for heavy PyTorch/YOLO/OCR inference.
* **Why Spring Boot Gateway?** Strict separation of security concerns: Spring Security enforces JWT validation, RBAC claims, rate-limiting, CORS, and audit headers before forwarding authorized traffic to the AI service.
* **How are GreenCoins computed?** $\text{GreenCoins} = (\text{Composite Score} \times 0.5) + \text{Tier Bonus} + \text{EPR Brand Bonus}$. All transactions are minted into an immutable ledger with unique verification keys to prevent duplicate rewards.
* **How does EPR Compliance work?** Uses CPCB-aligned recyclability multipliers ($\text{PET}=1.2, \text{Aluminum}=1.5, \text{Cardboard}=0.85, \text{E-Waste}=2.0$) multiplied by weight and verification quality to generate cryptographic audit evidence.
