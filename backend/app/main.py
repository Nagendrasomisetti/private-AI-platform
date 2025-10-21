"""
PrivAI FastAPI Backend - Main Application
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.logging import configure_logging, get_logger
from .api import upload, database, ingest, chat
from .models.schemas import HealthResponse, ErrorResponse

# Configure logging
configure_logging()
logger = get_logger("main")

# Application startup time
startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("PrivAI backend starting up", version=settings.app_version)
    yield
    # Shutdown
    logger.info("PrivAI backend shutting down")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Privacy-first AI application for college data processing",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(upload.router)
app.include_router(database.router)
app.include_router(ingest.router)
app.include_router(chat.router)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with basic information"""
    uptime = time.time() - startup_time
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        uptime=uptime
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - startup_time
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        uptime=uptime
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error("HTTP exception occurred", 
                status_code=exc.status_code,
                detail=exc.detail,
                path=request.url.path)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=f"Error occurred at {request.url.path}"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error("Unexpected error occurred", 
                error=str(exc),
                path=request.url.path)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
