"""
CyberShield AI — Database Connection & Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
import os


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cybershield:cybershield_pass@localhost:5432/cybershield_db"
)

# Handle test database
TESTING = os.getenv("TESTING", "false").lower() == "true"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

def _create_engine():
    """
    Create the SQLAlchemy engine.
    - TESTING=true  → lightweight SQLite (in-memory style)
    - Postgres URL   → try to connect; if DEBUG=true and it fails, fall back to
                       a local SQLite dev.db so the app starts without Postgres
    """
    if TESTING:
        return create_engine(
            "sqlite:///./test.db",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    pg_engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
    )

    # In development, gracefully fall back to SQLite when Postgres is down
    if DEBUG:
        try:
            with pg_engine.connect() as conn:
                conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            return pg_engine
        except Exception as exc:
            import warnings
            warnings.warn(
                f"⚠️  PostgreSQL unavailable ({exc}). "
                "Falling back to SQLite dev.db for local development. "
                "Set DEBUG=False in production.",
                stacklevel=2,
            )
            return create_engine(
                "sqlite:///./dev.db",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )

    return pg_engine


engine = _create_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass


def get_db():
    """
    FastAPI dependency — yields a database session per request.
    Automatically closes session after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """Create all tables (used in testing and initial setup)"""
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """Drop all tables (used in testing)"""
    Base.metadata.drop_all(bind=engine)