# GreenLoopAI — Database Architecture & ER Design

## 1. Overview
GreenLoopAI employs a normalized relational database schema (PostgreSQL in production, SQLite in local dev) designed for transaction safety, audit integrity, and regulatory compliance under Extended Producer Responsibility (EPR) frameworks.

---

## 2. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ VERIFICATION_RECORDS : "submits"
    USERS ||--o{ GREENCOIN_TRANSACTIONS : "holds"
    USERS ||--o{ AUDIT_LOGS : "generates"
    USERS ||--o{ ASSISTANT_SESSIONS : "initiates"
    
    VERIFICATION_RECORDS ||--o{ VERIFICATION_SIGNALS : "contains"
    VERIFICATION_RECORDS ||--o| GREENCOIN_TRANSACTIONS : "rewards"
    VERIFICATION_RECORDS ||--o| EPR_RECORDS : "certifies"
    
    ASSISTANT_SESSIONS ||--o{ ASSISTANT_MESSAGES : "logs"

    USERS {
        string id PK "UUID"
        string email UK "Indexed"
        string full_name
        string password_hash
        string role "CITIZEN | MUNICIPAL | PRODUCER | ADMIN"
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    VERIFICATION_RECORDS {
        string id PK "VER-UUID"
        string user_id FK "Indexed"
        string image_hash
        string file_name
        float file_size_bytes
        string waste_category "Indexed"
        string detected_label
        float detection_confidence
        text ocr_text
        string brand_name "Indexed"
        string barcode_value
        float authenticity_score
        float detection_score
        float brand_score
        float composite_score
        string status "PENDING | VERIFIED | REJECTED | REVIEW_REQUIRED | FAILED"
        datetime created_at "Indexed"
    }

    VERIFICATION_SIGNALS {
        string id PK "UUID"
        string verification_id FK "Indexed"
        string signal_type "YOLO | OCR | BARCODE | AUTHENTICITY | SCORE"
        float confidence
        json payload
        datetime timestamp
    }

    GREENCOIN_TRANSACTIONS {
        string id PK "UUID"
        string user_id FK "Indexed"
        string verification_id FK "Unique / Idempotency"
        int amount
        string transaction_type "EARNED | REDEEMED | BONUS"
        string reward_tier "BRONZE | SILVER | GOLD | PLATINUM"
        string calculation_basis
        datetime timestamp "Indexed"
    }

    EPR_RECORDS {
        string id PK "UUID"
        string verification_id FK "Unique"
        string evidence_id UK "EPR-Date-UUID"
        string brand_name "Indexed"
        string material_type "Indexed"
        string waste_category
        float weight_kg
        float epr_credits_generated
        string recyclability_tier "TIER_1_HIGH | TIER_2_MEDIUM | TIER_3_STANDARD"
        string compliance_status "COMPLIANT | PENDING_AUDIT | REJECTED"
        string regulatory_standard
        string calculation_summary
        datetime timestamp "Indexed"
    }

    AUDIT_LOGS {
        string id PK "UUID"
        string user_id FK "Optional"
        string action "Indexed"
        string endpoint
        string method
        string ip_address
        string request_id
        int status_code
        json details
        datetime timestamp "Indexed"
    }

    ASSISTANT_SESSIONS {
        string id PK "UUID"
        string user_id FK
        string title
        datetime created_at
        datetime updated_at
    }

    ASSISTANT_MESSAGES {
        string id PK "UUID"
        string session_id FK
        string role "user | assistant | system"
        text content
        int tokens_used
        string model_name
        datetime created_at
    }
```

---

## 3. Relational Tables Specification

### 3.1. `users`
* **`id`** (`VARCHAR(36)`): Primary Key (UUID v4).
* **`email`** (`VARCHAR(255)`): Unique, Case-insensitive, Indexed.
* **`full_name`** (`VARCHAR(255)`): User's full legal/display name.
* **`password_hash`** (`VARCHAR(255)`): Cryptographic hash (SHA-256 + salt or Argon2id).
* **`role`** (`ENUM`): `CITIZEN`, `MUNICIPAL`, `PRODUCER`, `ADMIN`.
* **`is_active`** (`BOOLEAN`): Account active status.

### 3.2. `verification_records`
* **`id`** (`VARCHAR(36)`): Primary Key formatted as `VER-[HEX12]`.
* **`user_id`** (`VARCHAR(36)`): Foreign Key references `users(id)`.
* **`image_hash`** (`VARCHAR(64)`): SHA-256 content hash for duplicate-image prevention.
* **`waste_category`** (`VARCHAR(100)`): Primary taxonomy category (Plastic, Cardboard, Metal, Glass, E-Waste).
* **`authenticity_score`**, **`detection_score`**, **`brand_score`**, **`composite_score`** (`FLOAT`): Real computed verification breakdown signals.
* **`status`** (`ENUM`): `VERIFIED`, `REJECTED`, `PENDING`, `REVIEW_REQUIRED`, `FAILED`.

### 3.3. `greencoin_transactions`
* **`id`** (`VARCHAR(36)`): Primary Key (UUID v4).
* **`verification_id`** (`VARCHAR(36)`): Unique foreign key ensuring **idempotent reward allocation** (no double crediting).
* **`amount`** (`INTEGER`): Number of GreenCoins awarded.
* **`reward_tier`** (`ENUM`): `BRONZE`, `SILVER`, `GOLD`, `PLATINUM`.

### 3.4. `epr_records`
* **`id`** (`VARCHAR(36)`): Primary Key (UUID v4).
* **`evidence_id`** (`VARCHAR(100)`): Unique compliance hash `EPR-YYYYMMDD-[HEX8]`.
* **`epr_credits_generated`** (`FLOAT`): Multiplied credit value ($Weight \times Factor \times Quality$).
* **`compliance_status`** (`ENUM`): `COMPLIANT`, `PENDING_AUDIT`, `REJECTED`.

---

## 4. Transactional Safety & Atomicity
Verification workflows execute inside an isolated ACID database transaction:
1. `SAVE verification_records`
2. `SAVE verification_signals`
3. `SAVE greencoin_transactions` (idempotent)
4. `SAVE epr_records`
5. `COMMIT` or `ROLLBACK` on error.
