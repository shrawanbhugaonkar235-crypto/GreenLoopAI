# GreenLoopAI — Security Architecture & Guidelines

## Security Gateway Layer (Spring Boot + Spring Security)

The Java Spring Boot service acts as the **Protected Security Gateway / API Barrier** for all incoming external requests.

### 1. Authentication & Authorization
- **OAuth2 Resource Server**: Validates incoming JWT bearer tokens issued by standard OAuth2 / OIDC providers (e.g., Keycloak, Auth0, Okta).
- **Token Verification**:
  - Signature integrity
  - Token expiration (`exp`) and not-before (`nbf`)
  - Issuer URI validation (`iss`)
  - Audience match (`aud`)
  - Scope and Role extraction (`CITIZEN`, `MUNICIPAL`, `PRODUCER`, `ADMIN`)

### 2. Rate Limiting Architecture
- **In-Memory Token Bucket Limiter**: Protects endpoints against denial-of-service, abuse, and excessive AI cost consumption without requiring external Redis databases.
- Configurable `requests-per-minute` and `burst-capacity`.
- Returns `HTTP 429 Too Many Requests` when limits are exceeded.

### 3. Security Headers Enforcement
- `Content-Security-Policy (CSP)`: Strict directive preventing untrusted inline execution or unauthorized script sources.
- `X-Frame-Options: DENY`: Prevents Clickjacking attacks.
- `X-Content-Type-Options: nosniff`: Prevents MIME-type sniffing.
- `Strict-Transport-Security (HSTS)`: Enforces HTTPS communication.
- `Referrer-Policy: strict-origin-when-cross-origin`.

### 4. Correlation Tracing & Sanitized Logging
- Every request is tagged with a unique `X-Request-Id` UUID.
- **Sensitive Data Redaction**: Loggers record method, URI, duration, and status code, but **STRICTLY NEVER** log:
  - `Authorization` headers or JWT tokens
  - `OPENAI_API_KEY`
  - Passwords or private keys
  - Uploaded image binaries
  - Sensitive prompt payloads

### 5. Service-to-Service Internal Authentication
- Spring Boot communicates with FastAPI over a private network channel with `X-Service-Token: ${FASTAPI_SERVICE_TOKEN}` header verification to prevent direct unauthorized access to internal AI services.
