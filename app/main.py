"""
FastAPI application entry point for Quiz Authentication Module.

This module initializes the FastAPI application with all routers,
middleware, exception handlers, and configuration.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth
from app.api import welcome
from app.core.exceptions import AuthException
from app.database import init_db
from app.i18n.language import detect_language
from app.i18n.translations import TranslationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize translation manager
translations = TranslationManager()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    # Startup
    await init_db()
    logger.info("Application started successfully")
    yield
    # Shutdown
    logger.info("Application shutting down")


# Application metadata
app = FastAPI(
    title="Quiz Auth Module",
    description="Multi-language authentication system with email verification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept-Language"],
)


# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# Exception handlers
@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException) -> JSONResponse:
    """Handle authentication module exceptions."""
    language = detect_language(request.headers.get("accept-language"))
    localized_message = translations.get(exc.message, language)
    
    # Log based on severity
    if exc.status_code >= 500:
        logger.error(f"{exc.__class__.__name__}: {exc.message}", exc_info=True)
    elif exc.status_code >= 400:
        logger.warning(f"{exc.__class__.__name__}: {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": localized_message}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    language = detect_language(request.headers.get("accept-language"))
    
    return JSONResponse(
        status_code=500,
        content={"detail": translations.get("internal_error", language)}
    )


# Include routers
app.include_router(auth.router)
app.include_router(welcome.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
