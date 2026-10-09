"""Security gateway evaluation routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import ToolCallRequest
from security.gateway import GatewayEngine
from database.models import SecurityEvent
from typing import Dict, Any, List, Optional
import json

router = APIRouter()


@router.post("/api/gateway/evaluate")
async def evaluate_tool_call(
    request: ToolCallRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluate a tool call through the security gateway.
    
    Args:
        request: ToolCallRequest with tool_name, arguments, user_request, agent_name, agent_role.
        db: Database session
        
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
        
        return decision.to_dict()
    
    except Exception as e:
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
        ]
    }
