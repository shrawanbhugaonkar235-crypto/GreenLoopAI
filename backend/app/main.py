import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import init_indexes
from app.routes import auth, verify, greencoins, history, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("greenloopai")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to ensure DB indexes are initialized at startup."""
    logger.info("Starting GreenLoopAI Backend...")
    try:
        init_indexes()
        logger.info("Database indexes successfully initialized.")
    except Exception as e:
        logger.warning(f"Database initialization notice: {e}")
    yield
    logger.info("Shutting down GreenLoopAI Backend...")

app = FastAPI(
    title="GreenLoopAI — Smart Waste Verification API",
    description=(
        "Production-grade backend for GreenLoopAI: YOLOv8 waste detection, "
        "Tesseract OCR, Pillow EXIF metadata authenticity, and MongoDB Atlas persistence."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = settings.allowed_origins
logger.info(f"Configuring CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(verify.router)
app.include_router(greencoins.router)
app.include_router(history.router)
app.include_router(health.router)

# Mount frontend files if available for convenient single-server hosting
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists() and (frontend_dir / "index.html").exists():
    logger.info(f"Mounting frontend directory from {frontend_dir}")
    # Mount css and js subdirectories
    css_dir = frontend_dir / "css"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    js_dir = frontend_dir / "js"
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(str(frontend_dir / "index.html"))

    @app.get("/favicon.svg", include_in_schema=False)
    async def serve_favicon():
        fav_path = frontend_dir / "favicon.svg"
        if fav_path.exists():
            return FileResponse(str(fav_path))
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
