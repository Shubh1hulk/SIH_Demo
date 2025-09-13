#!/usr/bin/env python3
"""
AI-Powered Multilingual Healthcare Chatbot
Main application entry point
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger
import sys
from typing import Dict, Any

# Import our modules - conditional imports for testing
try:
    from app.api.routes import chat, health, alerts
    routes_available = True
except ImportError as e:
    logger.warning(f"Route imports failed (expected in minimal test environment): {e}")
    routes_available = False
from app.core.config import settings
# Conditional imports for testing
try:
    from app.core.database import init_db
    from app.services.nlp_service import NLPService
    from app.services.health_service import HealthService
except ImportError as e:
    logger.warning(f"Some imports failed (expected in minimal test environment): {e}")
    init_db = None
    NLPService = None
    HealthService = None

# Global services
nlp_service = None
health_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    global nlp_service, health_service
    
    # Startup
    logger.info("Starting AI Healthcare Chatbot...")
    
    # Initialize database
    if init_db:
        await init_db()
    
    # Initialize services
    if NLPService and HealthService:
        nlp_service = NLPService()
        health_service = HealthService()
        
        # Load NLP models
        await nlp_service.initialize()
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Healthcare Chatbot...")
    if nlp_service:
        await nlp_service.cleanup()


# Create FastAPI app
app = FastAPI(
    title="AI Healthcare Chatbot",
    description="Multilingual AI-powered healthcare information chatbot for rural and semi-urban communities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
if routes_available:
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
    app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
    app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": "AI-Powered Multilingual Healthcare Chatbot",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/api/v1/status")
async def get_status() -> Dict[str, Any]:
    """Get system status"""
    return {
        "status": "healthy",
        "services": {
            "nlp": nlp_service.is_ready() if nlp_service else False,
            "health_db": health_service.is_ready() if health_service else False
        },
        "version": "1.0.0"
    }


def get_nlp_service():
    """Dependency injection for NLP service"""
    if not nlp_service:
        raise HTTPException(status_code=503, detail="NLP service not available")
    return nlp_service


def get_health_service():
    """Dependency injection for Health service"""
    if not health_service:
        raise HTTPException(status_code=503, detail="Health service not available")
    return health_service


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time}</green> | <level>{level}</level> | {message}")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )