# GreenLoopAI — Complete REST API Documentation

## 1. Authentication & Security Headers

### Gateway Request Headers
All API calls routed through Spring Boot or direct to FastAPI support:
* **`Authorization`**: `Bearer <JWT_TOKEN>` (User session authentication).
* **`X-Service-Token`**: Internal gateway-to-service secret token.
* **`X-Request-Id`**: Distributed correlation identifier for end-to-end tracing.
* **`X-User-Id`** & **`X-User-Role`**: User context propagated by Spring Security.

---

## 2. API Endpoints

### 2.1. Authentication & RBAC (`/api/v1/auth`)

#### `POST /api/v1/auth/register`
* **Request**:
  ```json
  {
    "email": "user@example.com",
    "full_name": "Alex Johnson",
    "password": "SecurePassword123",
    "role": "CITIZEN"
  }
  ```
* **Response** (`201 Created`):
  ```json
  {
    "success": true,
    "access_token": "jwt_...",
    "token_type": "Bearer",
    "expires_in_seconds": 86400,
    "user": {
      "id": "c1f7a0...",
      "email": "user@example.com",
      "full_name": "Alex Johnson",
      "role": "CITIZEN",
      "is_active": true
    }
  }
  ```

#### `POST /api/v1/auth/login`
* **Request**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123"
  }
  ```

---

### 2.2. Waste Verification Pipeline (`/api/v1/verification`)

#### `POST /api/v1/verification/verify`
Executes the **DETECT → VERIFY → REWARD → TRACK → COMPLY** pipeline.
* **Content-Type**: `multipart/form-data`
* **Body**: `image` (binary file: `.jpg`, `.png`, `.webp`, max 10MB)
* **Response** (`200 OK`):
  ```json
  {
    "verified": true,
    "verification_id": "VER-7F9B1E4A0C2D",
    "verification_score": 86.5,
    "status": "VERIFICATION_SUCCESSFUL",
    "detected_objects": [
      {
        "label": "Bottle",
        "confidence": 0.942,
        "category": "Plastic",
        "box": { "x1": 45.2, "y1": 32.1, "x2": 280.4, "y2": 450.0 }
      }
    ],
    "brand_detection": {
      "brand": "Bisleri",
      "confidence": 0.95,
      "barcode": "8901234567890",
      "text": "Bisleri with added minerals",
      "status": "DETECTED"
    },
    "authenticity": {
      "authentic": true,
      "score": 0.88,
      "status": "CAMERA_CAPTURE"
    },
    "score_breakdown": {
      "detection_score": 94.2,
      "brand_score": 95.0,
      "authenticity_score": 88.0,
      "composite_score": 86.5
    },
    "reward": {
      "greencoins_awarded": 58,
      "reward_tier": "PLATINUM",
      "calculation_basis": "Score 86.5% + EPR Brand Bonus (Bisleri)"
    },
    "processing_time_ms": 245.5,
    "notes": "Multi-signal real verification completed."
  }
  ```

#### `GET /api/v1/verification/history`
* **Query Parameters**: `user_id`, `category`, `status`, `skip` (default 0), `limit` (default 50)
* **Response**: List of historical scan records with GreenCoins and EPR evidence IDs.

---

### 2.3. GreenCoins Ledger (`/api/v1/green-coins`)

#### `GET /api/v1/green-coins/balance`
* **Response**:
  ```json
  {
    "success": true,
    "user_id": "c1f7a0...",
    "total_balance": 142
  }
  ```

#### `GET /api/v1/green-coins/transactions`
* **Response**: Immutable transaction ledger records with timestamp and tier.

---

### 2.4. EPR Compliance Module (`/api/v1/epr`)

#### `GET /api/v1/epr/records`
* **Response**: Verified EPR compliance records for regulatory audits.

#### `GET /api/v1/epr/summary`
* **Response**: Aggregated brand credits, total weight diverted, and compliance statistics.

---

### 2.5. Platform Analytics (`/api/v1/analytics`)

#### `GET /api/v1/analytics/summary`
* **Response**: Real aggregated metrics calculated dynamically from database tables.

---

### 2.6. AI Assistant (`/api/v1/assistant`)

#### `POST /api/v1/assistant/chat`
* **Request**:
  ```json
  {
    "messages": [
      { "role": "user", "content": "How are GreenCoins calculated for unbranded cardboard?" }
    ],
    "context": { "page": "verification-result" }
  }
  ```
* **Response**:
  ```json
  {
    "answer": "GreenCoins are calculated using composite scoring:...",
    "model": "gpt-4o-mini",
    "tokens_used": 184
  }
  ```
