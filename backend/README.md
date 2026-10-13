# GreenLoopAI — Backend & MongoDB Atlas Integration

GreenLoopAI is an AI-powered smart waste verification and citizen rewards platform. Citizens upload segregated waste photos; the pipeline executes Ultralytics YOLOv8 object detection, Tesseract OCR brand/text recognition, and Pillow EXIF authenticity checks to compute a composite verification score \(V\) and award GreenCoins.

---

## 1. System Architecture

```
Frontend (HTML5, CSS3, Vanilla JS)
      │
      │ REST API (JSON / Multipart, JWT Bearer Token)
      ▼
FastAPI Backend (Uvicorn)
      │
      ├── YOLOv8n (Object detection & category taxonomy)
      ├── Tesseract OCR (Packaging brand & material code detection)
      ├── Pillow EXIF (Camera hardware & software tampering flags)
      └── Composite Scoring Engine: V = 0.45D + 0.30B + 0.25A (Threshold: V >= 60)
      │
      ▼
MongoDB Atlas Cloud Database
      ├── users (Unique email, bcrypt password hash)
      ├── verifications (Pipeline outputs, scores, timestamps)
      └── greencoins_transactions (Unique reward per verification, ledger balance)
```

---

## 2. API Endpoints

### Authentication
- `POST /api/v1/auth/register` — Citizen registration with bcrypt hashing.
- `POST /api/v1/auth/login` — Citizen login, returns signed expiring JWT access token.
- `GET /api/v1/auth/me` — Current citizen profile (Protected).

### Waste Verification
- `POST /api/v1/verify` — Validates image format (JPG, PNG, WEBP), enforces 10 MB limit, runs YOLOv8 + OCR + EXIF, calculates score \(V\), stores in MongoDB, issues GreenCoins, and returns updated balance.

### Rewards & History
- `GET /api/v1/greencoins/balance` — Authoritative balance derived from MongoDB transactions.
- `GET /api/v1/greencoins/transactions` — Paginated reward transaction records.
- `GET /api/v1/history` — Paginated scan history for authenticated citizen.
- `GET /api/v1/history/{verification_id}` — Detailed report for a single scan.

### Health
- `GET /health` (or `/api/v1/health`) — Checks MongoDB Atlas ping, YOLO model, and OCR engine.

---

## 3. Environment Variables (`.env`)

| Variable | Description | Example |
| :--- | :--- | :--- |
| `MONGODB_URI` | MongoDB Atlas cluster connection string | `mongodb+srv://user:pass@cluster0.abc.mongodb.net/?retryWrites=true&w=majority` |
| `MONGODB_DATABASE` | Database name | `greenloopai` |
| `JWT_SECRET_KEY` | Secret key for JWT signature | `your-32-char-random-secret` |
| `JWT_EXPIRE_MINUTES` | Token expiry duration | `1440` (24 hours) |
| `YOLO_MODEL_PATH` | Path to YOLOv8n weights | `models/yolov8n.pt` |
| `YOLO_CONF` | Detection confidence threshold | `0.25` |
| `TESSERACT_CMD` | Path to Tesseract OCR executable | `C:\Program Files\Tesseract-OCR\tesseract.exe` (Windows) or `tesseract` (Linux) |
| `FRONTEND_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000,http://localhost:8000` |
| `MAX_UPLOAD_MB` | Upload file size limit | `10` |
| `GREENCOINS_PER_SCORE`| Reward coin multiplier | `0.5` |

---

## 4. Local Run (Windows PowerShell)

### Start Backend & Serve Frontend
```powershell
cd C:\Users\Shrawan\.gemini\antigravity\scratch\GreenLoopAI\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open **`http://localhost:8000`** in any browser.

### Run Automated Tests
```powershell
cd C:\Users\Shrawan\.gemini\antigravity\scratch\GreenLoopAI\backend
pytest tests -v
```

---

## 5. How to Get a 24/7 Public Link (Runs Even When Laptop is Shut Down)

When your laptop is turned off, local processes on `localhost` cannot run. To keep the website accessible 24/7 on all mobile phones and laptops worldwide, host it on a free cloud platform (e.g. **Render.com** or **Railway.app**).

### 3-Step Free Cloud Deployment (Render.com)

1. **Push the repository to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial GreenLoopAI release"
   git remote add origin https://github.com/<your-username>/GreenLoopAI.git
   git push -u origin main
   ```

2. **Deploy on Render (Free):**
   - Go to [render.com](https://render.com) and sign up with GitHub.
   - Click **New +** -> **Web Service**.
   - Select your `GreenLoopAI` repository.
   - Settings:
     - **Runtime:** `Python 3`
     - **Build Command:** `pip install -r backend/requirements.txt`
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend`
   - In **Environment Variables**, add:
     - `MONGODB_URI`: `<your MongoDB Atlas connection string>`
     - `JWT_SECRET_KEY`: `<generate a random secret>`
     - `TESSERACT_CMD`: `tesseract`

3. **Get Your Public HTTPS Link:**
   Render gives you an immediate live public link like:
   **`https://greenloopai.onrender.com`**
   This link works permanently on all devices, whether your laptop is on or completely shut down.
