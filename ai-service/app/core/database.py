import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger("greenloopai.database")

# Detect engine connection arguments
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine_kwargs = {
    "echo": settings.DB_ECHO,
    "connect_args": connect_args
}

if not is_sqlite:
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_pre_ping": True
    })

try:
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine initialized with URL: %s", settings.DATABASE_URL.split("@")[-1])
except Exception as e:
    logger.error("Failed to initialize database engine: %s", str(e))
    raise

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a transaction-managed SQLAlchemy session.
    Automatically commits on success or rolls back on unhandled exception.
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error("Database transaction rolled back due to error: %s", str(e))
        raise
    finally:
        db.close()


def init_db():
    """
    Initializes database schema tables if not created.
    """
    Base.metadata.create_all(bind=engine)
