"""Security gateway evaluation routes."""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from models import ToolCallRequest
from security.gateway import GatewayEngine
from database.models import SecurityEvent
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)
router = APIRouter()


def send_threat_notification(
    db_session,
    security_event_id: int,
    agent_name: str,
    attempted_tool: str,
    threat_category: str,
    severity: str,
    decision: str,
    arguments: Optional[Dict[str, Any]] = None
):
    """Background task to send threat notifications."""
    try:
        service = NotificationService(db_session)
        if decision in ["BLOCK", "REQUIRE_APPROVAL"]:
            notification = service.notify_on_threat(
                security_event_id=security_event_id,
                agent_name=agent_name,
                attempted_tool=attempted_tool,
                threat_category=threat_category,
                severity=severity,
                decision=decision,
                arguments=arguments
            )
            if notification:
                logger.info(f"Threat notification sent for incident {notification.incident_id}")
    except Exception as e:
        logger.error(f"Failed to send threat notification: {e}")


@router.post("/api/gateway/evaluate")
async def evaluate_tool_call(
    request: ToolCallRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Evaluate a tool call through the security gateway.
    
    Args:
        request: ToolCallRequest with tool_name, arguments, user_request, agent_name, agent_role.
        db: Database session
        background_tasks: FastAPI background tasks for async notification
        
    Returns:
        GatewayDecision with decision, risk_score, checks, and explanation
    """
    try:
        gateway = GatewayEngine(db)
        
        # Use agent_role from request body, default to 'employee' if not provided
        agent_role = getattr(request, 'agent_role', 'employee') or 'employee'
        
        decision = gateway.evaluate(
            tool_name=request.tool_name,
            arguments=request.arguments,
            user_request=request.user_request,
            agent_name=request.agent_name,
            agent_role=agent_role
        )
        
        # Trigger notifications asynchronously for BLOCK and REQUIRE_APPROVAL
        if decision.decision in ["BLOCK", "REQUIRE_APPROVAL"]:
            # Determine threat category and severity
            threat_category = "unauthorized_access"
            severity = "medium"
            
            if decision.checks:
                for check in decision.checks:
                    if not check.passed:
                        if "injection" in check.name.lower():
                            threat_category = "prompt_injection"
                            severity = "high"
                        elif "leakage" in check.name.lower():
                            threat_category = "data_leakage"
                            severity = "high"
                        elif "permission" in check.name.lower():
                            threat_category = "unauthorized_access"
                            severity = "medium"
            
            # Map risk score to severity
            if decision.risk_score >= 70:
                severity = "critical"
            elif decision.risk_score >= 50:
                severity = "high"
            
            # Schedule notification in background
            background_tasks.add_task(
                send_threat_notification,
                db,
                security_event_id=db.query(SecurityEvent).order_by(SecurityEvent.id.desc()).first().id,
                agent_name=request.agent_name,
                attempted_tool=request.tool_name,
                threat_category=threat_category,
                severity=severity,
                decision=decision.decision,
                arguments=request.arguments
            )
        
        return decision.to_dict()
    
    except Exception as e:
        logger.error(f"Gateway evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Gateway evaluation failed: {str(e)}")


@router.get("/api/gateway/events")
async def get_gateway_events(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get the most recent security events with their check details.
    
    Args:
        db: Database session
        limit: Maximum number of events to return (default 10)
        
    Returns:
        List of security events sorted by timestamp descending
    """
    try:
        events = db.query(SecurityEvent).order_by(SecurityEvent.timestamp.desc()).limit(limit).all()
        
        result = []
        for event in events:
            result.append({
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
            })
        
        return result
    except Exception as e:
        logger.error(f"Failed to retrieve events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {str(e)}")


@router.get("/api/gateway/health")
async def gateway_health():
    """
    Check gateway health and status.
    
    Returns:
        Status information
    """
    return {
        "status": "operational",
        "version": "1.0.0",
        "engines": [
            "policy_engine",
            "prompt_injection_detector",
            "data_leakage_prevention",
            "risk_scorer",
            "intent_validator"
        ],
        "notifications": {
            "enabled": True,
            "mode": os.getenv("NOTIFICATION_MODE", "mock")
        }
    }
