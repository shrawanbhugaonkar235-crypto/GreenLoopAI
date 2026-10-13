# GreenLoopAI — API Contract

## Endpoints Specification

### 1. Health & Readiness
- **Route**: `GET /api/health`
- **Access**: Public
- **Response**:
```json
{
  "status": "UP",
  "gateway": "GreenLoopAI Spring Security Gateway",
  "version": "1.0.0",
  "services": {
    "fastapi_backend": {
      "status": "UP",
      "components": {
        "openai_assistant": { "configured": true, "model": "gpt-4o-mini" },
        "yolo_detection": { "available": true },
        "ocr_engine": { "available": true },
        "authenticity_engine": { "available": true }
      }
    }
  }
}
```

---

### 2. Real AI Assistant Chat
- **Route**: `POST /api/v1/assistant/chat`
- **Access**: Protected (JWT / Gateway authorized)
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt-token>` (when OAuth2 enabled)
- **Request Body**:
```json
{
  "message": "What is EPR compliance?",
  "messages": [
    { "role": "user", "content": "What is EPR compliance?" }
  ],
  "context": {
    "page": "dashboard"
  }
}
```
- **Response**:
```json
{
  "answer": "Extended Producer Responsibility (EPR) is an environmental policy approach...",
  "model": "gpt-4o-mini",
  "tokens_used": 142,
  "request_id": "9f623049-7e7a-4224-a212-32b4f62080a9"
}
```

---

### 3. Multi-Modal Waste Verification
- **Route**: `POST /api/v1/verification/verify`
- **Access**: Protected (JWT / Gateway authorized)
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `image`: Binary file (JPEG, PNG, WebP; max 10MB)
- **Response**:
```json
{
  "verified": true,
  "verification_id": "VER-8A31D084F9B2",
  "verification_score": 90.5,
  "status": "VERIFICATION_SUCCESSFUL",
  "detected_objects": [
    {
      "label": "Bottle",
      "confidence": 0.9421,
      "category": "Plastic",
      "box": { "x1": 45.2, "y1": 80.5, "x2": 320.0, "y2": 780.4 }
    }
  ],
  "brand_detection": {
    "text": "Coca-Cola 500ml",
    "brand": "Coca-Cola",
    "confidence": 0.912,
    "status": "DETECTED"
  },
  "authenticity": {
    "exif_present": true,
    "camera_make": "Apple",
    "camera_model": "iPhone 14",
    "software": null,
    "timestamp_valid": true,
    "score": 0.90,
    "flags": []
  },
  "score_breakdown": {
    "detection_score": 94.21,
    "brand_score": 91.2,
    "authenticity_score": 90.0,
    "composite_score": 90.5
  },
  "reward": {
    "greencoins_awarded": 70,
    "reward_tier": "PLATINUM",
    "calculation_basis": "Score 90.5% (94.2% detect + 91.2% brand + 90.0% auth) + EPR Brand Bonus (Coca-Cola)"
  },
  "processing_time_ms": 142.5,
  "notes": "Multi-signal real verification completed."
}
```

---

### 4. EPR Compliance Processing
- **Route**: `POST /api/v1/epr/process`
- **Access**: Protected (JWT / Gateway authorized)
- **Request Body**:
```json
{
  "verification_id": "VER-8A31D084F9B2",
  "waste_category": "Plastic",
  "material_type": "PET",
  "weight_kg": 0.5,
  "brand": "Coca-Cola",
  "verification_score": 90.5
}
```
- **Response**:
```json
{
  "evidence_id": "EPR-20261003-7BA2F4C1",
  "verification_id": "VER-8A31D084F9B2",
  "compliance_status": "COMPLIANT",
  "epr_credits_generated": 0.543,
  "target_category": "Plastic",
  "recyclability_tier": "TIER_1_HIGH",
  "timestamp": "2026-10-03T18:00:00.000Z",
  "regulatory_standard": "CPCB EPR Guidelines (Category I - Rigid Plastic)",
  "calculation_summary": "0.50 kg × 1.2 (Material factor) × 0.91 (Quality score) = 0.543 Credits"
}
```
