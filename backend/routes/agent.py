"""AI agent integration routes."""
import json
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from database.models import Threat
from security.gateway import GatewayEngine
from agent.agent_service import AgentService
from agent.tool_registry import ToolRegistry
from models import ToolCallRequest

router = APIRouter()

# Initialize services
agent_service = AgentService()
tool_registry = ToolRegistry()


@router.post("/api/agent/message")
async def agent_message(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Process a user message through the AI agent and security gateway.
    
    Args:
        request: JSON body with:
            - user_message: str (required)
            - agent_role: str (default: 'employee')
            - conversation_history: list (default: [])
        db: Database session
        
    Returns:
        Dictionary with:
            - response_text: Agent's response
            - proposed_tools: Tools proposed by agent
            - gateway_decisions: Security decisions for each tool
            - executed_tools: List of tool names that were executed
            - blocked_tools: List of tool names that were blocked
    """
    try:
        # Extract request parameters
        user_message = request.get("user_message")
        if not user_message:
            raise HTTPException(status_code=400, detail="Missing required field: user_message")
        
        agent_role = request.get("agent_role", "employee")
        conversation_history = request.get("conversation_history", [])
        
        # Call the AI agent
        agent_response = agent_service.call_agent(
            user_message=user_message,
            agent_role=agent_role,
            conversation_history=conversation_history
        )
        
        # Process each proposed tool through the security gateway
        gateway_decisions = []
        executed_tools = []
        blocked_tools = []
        
        gateway = GatewayEngine(db)
        
        for tool_call in agent_response.get("proposed_tools", []):
            tool_name = tool_call.get("tool_name")
            arguments = tool_call.get("arguments", {})
            user_request = tool_call.get("user_request", user_message)
            
            # Pre-validate tool arguments for injection indicators
            arg_injection_check = _check_arguments_for_injection(arguments)
            
            # Evaluate tool call through gateway
            decision = gateway.evaluate(
                tool_name=tool_name,
                arguments=arguments,
                user_request=user_request,
                agent_name="ai_agent",
                agent_role=agent_role
            )
            
            # If injection was found in arguments, force BLOCK decision
            if arg_injection_check["contains_injection"]:
                decision.decision = "BLOCK"
                decision.explanation = arg_injection_check["reason"]
                decision.risk_score = max(decision.risk_score, 90)
                decision.risk_tier = "CRITICAL"
            
            # Record gateway decision
            gateway_decisions.append(decision.to_dict())
            
            # Execute tool if allowed
            if decision.decision == "ALLOW":
                try:
                    result = tool_registry.execute_tool(tool_name, arguments, db)
                    executed_tools.append(tool_name)
                except Exception as e:
                    blocked_tools.append(tool_name)
                    print(f"Error executing {tool_name}: {e}")
            
            # Create threat record if blocked
            elif decision.decision == "BLOCK":
                blocked_tools.append(tool_name)
                
                # Determine threat category from failed checks
                threat_category = _determine_threat_category(decision)
                severity = _map_risk_tier_to_severity(decision.risk_tier)
                
                threat = Threat(
                    timestamp=None,
                    threat_category=threat_category,
                    severity=severity,
                    agent_identifier="ai_agent",
                    requested_action=tool_name,
                    reason_for_detection=decision.explanation,
                    gateway_response="blocked",
                    is_demo=False
                )
                db.add(threat)
                db.commit()
        
        return {
            "response_text": agent_response.get("response_text", ""),
            "proposed_tools": agent_response.get("proposed_tools", []),
            "gateway_decisions": gateway_decisions,
            "executed_tools": executed_tools,
            "blocked_tools": blocked_tools
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing agent message: {str(e)}")


@router.post("/api/agent/mock")
async def agent_mock(
    scenario: str = Query("normal"),
    request: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Process a mock agent scenario through the security gateway.
    
    Args:
        scenario: One of 'normal', 'prompt_injection', 'exfiltration', 'unauthorized_tool'
        request: Optional JSON body with user_message (default: "test request")
        db: Database session
        
    Returns:
        Dictionary with same format as /api/agent/message
    """
    try:
        # Extract or default user message
        user_message = "test request"
        agent_role = "employee"
        
        if request:
            user_message = request.get("user_message", user_message)
            agent_role = request.get("agent_role", agent_role)
        
        # Call mock agent with scenario
        agent_response = agent_service._call_mock_agent(user_message, agent_role)
        
        # Process through gateway (same as /api/agent/message)
        gateway_decisions = []
        executed_tools = []
        blocked_tools = []
        
        gateway = GatewayEngine(db)
        
        for tool_call in agent_response.get("proposed_tools", []):
            tool_name = tool_call.get("tool_name")
            arguments = tool_call.get("arguments", {})
            user_request = tool_call.get("user_request", user_message)
            
            # Pre-validate tool arguments for injection indicators
            arg_injection_check = _check_arguments_for_injection(arguments)
            
            # Evaluate tool call through gateway
            decision = gateway.evaluate(
                tool_name=tool_name,
                arguments=arguments,
                user_request=user_request,
                agent_name="ai_agent",
                agent_role=agent_role
            )
            
            # If injection was found in arguments, force BLOCK decision
            if arg_injection_check["contains_injection"]:
                decision.decision = "BLOCK"
                decision.explanation = arg_injection_check["reason"]
                decision.risk_score = max(decision.risk_score, 90)
                decision.risk_tier = "CRITICAL"
            
            # Record gateway decision
            gateway_decisions.append(decision.to_dict())
            
            # Execute tool if allowed
            if decision.decision == "ALLOW":
                try:
                    result = tool_registry.execute_tool(tool_name, arguments, db)
                    executed_tools.append(tool_name)
                except Exception as e:
                    blocked_tools.append(tool_name)
                    print(f"Error executing {tool_name}: {e}")
            
            # Create threat record if blocked
            elif decision.decision == "BLOCK":
                blocked_tools.append(tool_name)
                
                threat_category = _determine_threat_category(decision)
                severity = _map_risk_tier_to_severity(decision.risk_tier)
                
                threat = Threat(
                    timestamp=None,
                    threat_category=threat_category,
                    severity=severity,
                    agent_identifier="ai_agent",
                    requested_action=tool_name,
                    reason_for_detection=decision.explanation,
                    gateway_response="blocked",
                    is_demo=False
                )
                db.add(threat)
                db.commit()
        
        return {
            "response_text": agent_response.get("response_text", ""),
            "proposed_tools": agent_response.get("proposed_tools", []),
            "gateway_decisions": gateway_decisions,
            "executed_tools": executed_tools,
            "blocked_tools": blocked_tools
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing mock scenario: {str(e)}")


@router.get("/api/agent/status")
async def agent_status():
    """
    Get agent service status.
    
    Returns:
        Dictionary with:
            - mode: "mock" or "live"
            - model: Model name if live, "mock" if mock mode
    """
    if agent_service.mock_mode:
        return {
            "mode": "mock",
            "model": "mock"
        }
    else:
        return {
            "mode": "live",
            "model": "gemini-1.5-flash"
        }


def _determine_threat_category(decision) -> str:
    """
    Determine threat category from failed security checks.
    
    Args:
        decision: GatewayDecision object
        
    Returns:
        Threat category string
    """
    # Check failed checks to categorize threat
    for check in decision.checks:
        if not check.passed:
            if check.name == "prompt_injection":
                return "prompt_injection"
            elif check.name == "data_leakage_prevention":
                return "data_exfiltration"
            elif check.name == "tool_permission":
                return "unauthorized_tool"
            elif check.name == "resource_authorization":
                return "unauthorized_access"
    
    # Default to policy violation if no specific category matches
    return "policy_violation"


def _map_risk_tier_to_severity(risk_tier: str) -> str:
    """
    Map risk tier to threat severity.
    
    Args:
        risk_tier: Risk tier from gateway decision
        
    Returns:
        Severity string (lowercase)
    """
    tier_map = {
        "CRITICAL": "critical",
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low"
    }
    return tier_map.get(risk_tier, "medium")


def _check_arguments_for_injection(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check tool arguments for injection indicators like override fields or suspicious parameter names.
    
    Args:
        arguments: Tool arguments dictionary
        
    Returns:
        Dictionary with:
            - contains_injection: bool
            - reason: str (explanation if injection found)
    """
    if not isinstance(arguments, dict):
        return {"contains_injection": False, "reason": ""}
    
    # List of suspicious argument names that suggest prompt injection attempts
    suspicious_keys = [
        "content_override",
        "instruction_override",
        "system_override",
        "prompt_override",
        "ignore_",
        "_ignore",
        "bypass",
        "override",
    ]
    
    # Check for suspicious keys
    for key in arguments.keys():
        key_lower = key.lower()
        for suspicious_pattern in suspicious_keys:
            if suspicious_pattern.lower() in key_lower:
                # Check if the value contains injection patterns
                value = str(arguments[key]).lower()
                if any(phrase in value for phrase in ["ignore", "bypass", "override", "reveal", "disregard"]):
                    return {
                        "contains_injection": True,
                        "reason": f"✗ Prompt injection detected: suspicious argument '{key}' with malicious content"
                    }
    
    return {"contains_injection": False, "reason": ""}
