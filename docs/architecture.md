# GreenLoopAI — System Architecture

## Overview
**GreenLoopAI** is an AI-powered platform for smart waste verification and automated Extended Producer Responsibility (EPR) compliance.

Core Pipeline Workflow:
```text
SCAN ──► DETECT ──► VERIFY ──► RECYCLE ──► REWARD ──► EPR
(Input)  (Vision)   (OCR/EXIF) (Guidance) (Tokens)   (Compliance)
```

## System Component Topology

```text
                                  USER BROWSER
                                       │
                                       ▼
                       ┌───────────────────────────────┐
                       │     FRONTEND APPLICATION      │
                       │     Vanilla HTML5 / CSS3 / JS │
                       └───────────────┬───────────────┘
                                       │
                                       │ HTTPS / JSON & Multipart
                                       ▼
                       ┌───────────────────────────────┐
                       │      SECURITY GATEWAY         │
                       │   Java 17 + Spring Boot 3.3   │
                       │   Spring Security OAuth2 JWT  │
                       │   Rate Limiting & Audit Logs  │
                       │   CORS & Security Headers     │
                       └───────────────┬───────────────┘
                                       │
                                       │ Internal Authorized Proxy
                                       │ (X-Service-Token + X-Request-Id)
                                       ▼
                       ┌───────────────────────────────┐
                       │        AI BACKEND SERVICE     │
                       │       Python 3 + FastAPI      │
                       │   Dynamic Scoring & Valuation │
                       └───────────────┬───────────────┘
                                       │
              ┌────────────────────────┴────────────────────────┐
              ▼                                                 ▼
   ┌─────────────────────┐                           ┌─────────────────────┐
   │ COMPUTER VISION &   │                           │ OPENAI RESPONSES    │
   │ AUTHENTICITY PIPELINE│                          │ API (Official SDK)  │
   │ • YOLO (Ultralytics)│                           │ • Stateless         │
   │ • OCR Engine        │                           │ • In-Memory Context │
   │ • EXIF Validator    │                           │ • store=False       │
   └─────────────────────┘                           └─────────────────────┘
```

## Key Architectural Principles

1. **Zero Database Architecture**:
   No PostgreSQL, MySQL, SQLite, MongoDB, Redis, or local file persistence. All operations are pure functional streams deriving immediate compliance proofs and verification assessments.

2. **No Mock or Simulated AI Responses**:
   The system only reports results from active models. When models are unconfigured, clear status codes (`503 AI detection model unavailable`, `AI_SERVICE_NOT_CONFIGURED`) are returned.

3. **Isolated Secret Boundary**:
   The OpenAI API key and service credentials exist exclusively on backend servers and are never exposed to the frontend or browser.

4. **Multi-Modal Verification Engine**:
   - **Vision (YOLO)**: Detects physical waste item classes (Plastic bottles, aluminum cans, cardboard, e-waste).
   - **Brand OCR**: Detects brand logos and text inscriptions matching registered EPR producers.
   - **Authenticity Analyzer**: Inspects hardware EXIF headers, camera sensors, and temporal integrity.
   - **Composite Scorer**: Dynamically blends detection, brand, and authenticity signals into a transparent score.
