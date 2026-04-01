"""
CyberShield AI — FastAPI Application Entry Point
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

# Suppress noisy ML logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import engine, Base
from utils.exceptions import setup_exception_handlers
from dependencies import rate_limit_dependency

# Import routers (will be created in subsequent steps)
from routes import auth, analyze, awareness, reports, admin, demo, chatbot


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # ─── STARTUP ───
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Pre-load ML models (lazy loading available in model_loader)
    # We don't load here to keep startup fast; models load on first request
    print("✅ Application startup complete")
    
    yield
    
    # ─── SHUTDOWN ───
    print("👋 Application shutting down")


def create_application() -> FastAPI:
    """Application factory pattern."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="India-first multi-modal AI platform for cyber threat detection and awareness",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # ─── Middleware ───
    # NOTE: add_middleware() builds a stack in LIFO order (last-added = outermost).
    # @app.middleware decorators are appended AFTER that stack resolves, making them
    # innermost. To guarantee CORS runs on EVERY response (including error responses)
    # we register middlewares in this explicit order:
    #   1. Request-metadata (innermost — runs last)
    #   2. TrustedHost
    #   3. CORS (outermost — runs first; always injects Access-Control headers)

    # 1. Request ID + timing  (innermost)
    from starlette.middleware.base import BaseHTTPMiddleware

    async def _add_request_metadata(request: Request, call_next):
        request.state.request_id = os.urandom(8).hex()
        request.state.start_time = datetime.now(timezone.utc)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-API-Version"] = settings.APP_VERSION
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=_add_request_metadata)

    # 2. Trusted Host
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.DEBUG else ["localhost", "*.cybershield.ai", "testserver", "cybershield-api-t6z7.onrender.com"]
    )

    # 3. CORS  (outermost — added last so it wraps everything and always runs first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # ─── Exception Handlers ───
    setup_exception_handlers(app)
    
    # ─── Routes ───
    
    # Health check (public, no rate limit)
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint for load balancers and monitoring.
        Returns 200 OK if service is running.
        """
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": "development" if settings.DEBUG else "production"
        }
    
    # API Routers
    # Note: rate_limit_dependency applied individually to routes that need it
    app.include_router(
        auth.router,
        prefix="/api/v1/auth",
        tags=["Authentication"]
    )
    app.include_router(
        analyze.router,
        prefix="/api/v1/analyze",
        tags=["Analysis"]
    )
    app.include_router(
        awareness.router,
        prefix="/api/v1/awareness",
        tags=["Awareness"]
    )
    app.include_router(
        reports.router,
        prefix="/api/v1/reports",
        tags=["Reports"]
    )
    app.include_router(
        admin.router,
        prefix="/api/v1/admin",
        tags=["Admin"]
    )
    app.include_router(
        demo.router,
        prefix="/api/v1/demo",
        tags=["Demo"]
    )

    app.include_router(
        chatbot.router,
        prefix="/api/v1/assistant",
        tags=["Assistant"],
    )
    
    # Root redirect to docs
    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "CyberShield AI API", "docs": "/docs"}
    
    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )