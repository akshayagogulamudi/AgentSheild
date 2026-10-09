"""Security events routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from database.models import SecurityEvent, ActivityLog, Threat
from models import SecurityEventSchema, ActivityLogSchema, ThreatSchema
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter()


@router.get("/api/events", response_model=List[SecurityEventSchema])
async def get_events(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    decision: Optional[str] = Query(None)
):
    """Get security events with optional filtering."""
    try:
        query = db.query(SecurityEvent)
        
        if decision:
            query = query.filter(SecurityEvent.decision == decision)
        
        events = query.order_by(SecurityEvent.timestamp.desc()).offset(offset).limit(limit).all()
        
        # Transform events to ensure checks_passed and checks_failed are lists
        result = []
        for event in events:
            event_dict = {
                "id": event.id,
                "timestamp": event.timestamp,
                "agent_name": event.agent_name,
                "requested_tool": event.requested_tool,
                "arguments": event.arguments,
                "decision": event.decision,
                "risk_score": event.risk_score,
                "reason": event.reason,
                "checks_passed": json.loads(event.checks_passed) if event.checks_passed else [],
                "checks_failed": json.loads(event.checks_failed) if event.checks_failed else [],
                "is_demo": event.is_demo
            }
            result.append(event_dict)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/events", response_model=SecurityEventSchema)
async def create_event(event_data: SecurityEventSchema, db: Session = Depends(get_db)):
    """Record a new security event."""
    try:
        event = SecurityEvent(
            agent_name=event_data.agent_name,
            requested_tool=event_data.requested_tool,
            arguments=event_data.arguments,
            decision=event_data.decision,
            risk_score=event_data.risk_score or 0.0,
            reason=event_data.reason,
            checks_passed=json.dumps(event_data.checks_passed) if event_data.checks_passed else None,
            checks_failed=json.dumps(event_data.checks_failed) if event_data.checks_failed else None,
            is_demo=event_data.is_demo
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/threats", response_model=List[ThreatSchema])
async def get_threats(
    db: Session = Depends(get_db),
    threat_category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    gateway_response: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Get threats with optional filters.
    
    Args:
        db: Database session
        threat_category: Filter by threat category (optional)
        severity: Filter by severity (optional)
        gateway_response: Filter by gateway response (optional)
        limit: Maximum results
        offset: Pagination offset
        
    Returns:
        List of threats
    """
    try:
        query = db.query(Threat)
        
        if threat_category:
            query = query.filter(Threat.threat_category == threat_category)
        if severity:
            query = query.filter(Threat.severity == severity)
        if gateway_response:
            query = query.filter(Threat.gateway_response == gateway_response)
        
        threats = query.order_by(Threat.timestamp.desc()).offset(offset).limit(limit).all()
        return threats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/activity-logs", response_model=List[ActivityLogSchema])
async def get_activity_logs(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get activity logs."""
    try:
        logs = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).offset(offset).limit(limit).all()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/activity-logs", response_model=ActivityLogSchema)
async def create_activity_log(log_data: ActivityLogSchema, db: Session = Depends(get_db)):
    """Record a new activity log entry."""
    try:
        log = ActivityLog(
            actor=log_data.actor,
            action=log_data.action,
            details=log_data.details,
            is_demo=log_data.is_demo
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
