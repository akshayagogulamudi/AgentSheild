"""Notification history and status routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.notification_schemas import (
    NotificationRecordSchema, NotificationHistorySchema, NotificationSummarySchema
)
from services.notification_service import NotificationService

router = APIRouter()


@router.get("/api/notifications/summary", response_model=NotificationSummarySchema)
async def get_notification_summary(db: Session = Depends(get_db)):
    """
    Get notification summary (critical count, unread count, recent incidents).
    
    Returns:
        NotificationSummarySchema with aggregated notification data
    """
    try:
        service = NotificationService(db)
        summary = service.get_summary(db)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notification summary: {str(e)}")


@router.get("/api/notifications", response_model=NotificationHistorySchema)
async def get_notifications(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    severity: str = Query(None, description="Filter by severity: low, medium, high, critical")
):
    """
    Get notification history.
    
    Args:
        db: Database session
        limit: Number of records to return (default 50, max 100)
        offset: Offset for pagination (default 0)
        severity: Optional filter by severity
        
    Returns:
        NotificationHistorySchema with paginated results
    """
    try:
        service = NotificationService(db)
        records, total = service.get_notification_history(
            db, limit=limit, offset=offset, severity=severity
        )
        
        return NotificationHistorySchema(
            items=[NotificationRecordSchema.from_orm(r) for r in records],
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")


@router.get("/api/notifications/{incident_id}", response_model=NotificationRecordSchema)
async def get_notification_detail(incident_id: str, db: Session = Depends(get_db)):
    """
    Get details of a specific notification by incident ID.
    
    Args:
        incident_id: Unique incident identifier
        db: Database session
        
    Returns:
        NotificationRecordSchema with full details
    """
    try:
        from database.notification_models import NotificationRecord
        
        notification = db.query(NotificationRecord).filter(
            NotificationRecord.incident_id == incident_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return NotificationRecordSchema.from_orm(notification)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notification: {str(e)}")


@router.get("/api/notifications/critical/count")
async def get_critical_notification_count(db: Session = Depends(get_db)):
    """
    Get count of critical severity notifications.
    
    Returns:
        Count of critical notifications
    """
    try:
        from database.notification_models import NotificationRecord
        
        count = db.query(NotificationRecord).filter(
            NotificationRecord.severity == "critical"
        ).count()
        
        return {"count": count, "severity": "critical"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch critical count: {str(e)}")
