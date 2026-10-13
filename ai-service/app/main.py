import time
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import (
    health,
    assistant,
    verification,
    history,
    greencoins,
    epr,
    analytics,
    audit,
    auth,
    recycling
)

# Configure secure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("greenloopai.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize relational database tables on startup
    try:
        init_db()
        logger.info("Relational database schema verified and initialized.")
    except Exception as e:
        logger.error("Database initialization error: %s", str(e))
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GreenLoopAI — AI-Powered Platform for Smart Waste Verification & Automated EPR Compliance",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Security gateway handles strict origin verification
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_and_logging_middleware(request: Request, call_next):
    """
    Assigns correlation Request-ID and performs security logging.
    Strictly avoids logging authorization tokens, keys, passwords, or payload bodies.
    """
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-Id"] = request_id

        # Security audit log without sensitive body
        logger.info(
            "Request finished: id=%s method=%s path=%s status=%d duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms
        )
        return response

    except Exception as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error(
            "Unhandled server exception: id=%s method=%s path=%s error=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            str(e),
            duration_ms
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "request_id": request_id
            },
            headers={"X-Request-Id": request_id}
        )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    request_id = request.headers.get("X-Request-Id") or "unknown"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_EXCEPTION",
            "message": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id
        },
        headers={"X-Request-Id": request_id}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = request.headers.get("X-Request-Id") or "unknown"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed.",
            "details": jsonable_encoder(exc.errors()),
            "request_id": request_id
        },
        headers={"X-Request-Id": request_id}
    )


# Include Production API Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(verification.router)
app.include_router(recycling.router)
app.include_router(history.router)
app.include_router(greencoins.router)
app.include_router(epr.router)
app.include_router(analytics.router)
app.include_router(audit.router)
app.include_router(assistant.router)


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "status": "ONLINE",
        "version": settings.APP_VERSION,
        "workflow": "SCAN -> DETECT -> VERIFY -> RECYCLE -> REWARD -> EPR"
    }
