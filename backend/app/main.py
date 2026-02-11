"""Application entry point for GenAI Summarizer Web App."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import config
from backend.app.logger import app_logger
from backend.app.errors import (
    SummarizerException,
    summarizer_exception_handler,
    generic_exception_handler
)
from backend.app import api, ui


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    app_logger.info("Starting GenAI Summarizer Web App")
    app_logger.info(f"Host: {config.HOST}, Port: {config.PORT}")
    
    try:
        # Validate configuration
        config.validate()
        app_logger.info("Configuration validated successfully")
    except Exception as e:
        app_logger.error(f"Configuration validation failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down GenAI Summarizer Web App")


# Create FastAPI application
app = FastAPI(
    title="GenAI Summarizer Web App",
    description="AI-powered document summarization service with REST API and Web UI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(SummarizerException, summarizer_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(api.router)  # REST API routes
app.include_router(ui.router)   # Web UI routes

# Mount static files (if needed)
# app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": "GenAI Summarizer Web App",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    app_logger.info(f"Starting server on {config.HOST}:{config.PORT}")
    
    uvicorn.run(
        "backend.app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,  # Enable auto-reload for development
        log_level=config.LOG_LEVEL.lower()
    )
