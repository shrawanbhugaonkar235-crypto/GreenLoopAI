FROM python:3.11-slim

# Install Tesseract OCR and OpenCV system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and frontend code
COPY backend/ backend/
COPY frontend/ frontend/

# Set environment
ENV PORT=8000
ENV TESSERACT_CMD=tesseract
ENV YOLO_MODEL_PATH=models/yolov8n.pt

EXPOSE 8000

# Start FastAPI server on Render's assigned port
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir backend"]
