"""
FastAPI Backend - IQ Analyzer Trading Platform
Real-time trading analysis with IQ Option API integration
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging
from datetime import datetime

from backend.models import User, Trade, TradeCreate, UserCreate, LoginRequest
from backend.database import get_db, engine
from backend.services.iqoption_service import IQOptionService
from backend.routes import auth, trades, analytics

# Initialize FastAPI app
app = FastAPI(
    title="IQ Analyzer API",
    description="AI Trading Analysis Platform with IQ Option Integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and services"""
    logger.info("Starting IQ Analyzer API...")
    # Create database tables
    from backend.models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down IQ Analyzer API...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IQ Analyzer API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected",
            "iq_option_api": "available"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
