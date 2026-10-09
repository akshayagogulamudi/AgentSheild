"""Health check routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AgentShield AI Backend",
        "version": "0.1.0"
    }


@router.get("/api/status")
async def api_status(db: Session = Depends(get_db)):
    """API status endpoint with database check."""
    try:
        # Try to query the database
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "operational",
        "database": db_status,
        "service": "AgentShield AI Backend"
    }
