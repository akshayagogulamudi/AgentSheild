from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SecurityClassificationEnum(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    RESTRICTED = "RESTRICTED"


class SecurityEventDecisionEnum(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class ToolCallRequest(BaseModel):
    """Schema for tool call requests from AI agent."""
    tool_name: str = Field(..., description="Name of the tool to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    agent_name: str = Field(default="default_agent", description="Name of the requesting agent")
    user_request: Optional[str] = Field(None, description="Original user request for intent validation")


class PolicySchema(BaseModel):
    """Schema for security policy."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    role: str
    description: Optional[str] = None
    allowed_tools: str  # JSON string
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_demo: Optional[bool] = False


class SecurityEventSchema(BaseModel):
    """Schema for security events."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    agent_name: str
    requested_tool: str
    arguments: Optional[str] = None
    decision: SecurityEventDecisionEnum
    risk_score: Optional[float] = 0.0
    reason: Optional[str] = None
    checks_passed: Optional[List[str]] = None
    checks_failed: Optional[List[str]] = None
    is_demo: Optional[bool] = False


class ThreatSchema(BaseModel):
    """Schema for detected threats."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    event_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    threat_category: str
    severity: Optional[str] = None
    agent_identifier: Optional[str] = None
    requested_action: Optional[str] = None
    reason_for_detection: Optional[str] = None
    gateway_response: Optional[str] = None
    is_demo: Optional[bool] = True


class SimulatedFileSchema(BaseModel):
    """Schema for simulated files."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    filename: str
    content: Optional[str] = None
    classification: SecurityClassificationEnum
    created_at: Optional[datetime] = None
    is_demo: Optional[bool] = False


class SimulatedRecordSchema(BaseModel):
    """Schema for simulated records."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    record_type: str
    data: str  # JSON string
    classification: SecurityClassificationEnum
    created_at: Optional[datetime] = None
    is_demo: Optional[bool] = False


class ActivityLogSchema(BaseModel):
    """Schema for activity logs."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    actor: Optional[str] = None
    action: str
    details: Optional[str] = None
    is_demo: Optional[bool] = False


class PendingApprovalSchema(BaseModel):
    """Schema for pending approvals."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    event_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    agent_name: str
    tool_name: str
    arguments: Optional[str] = None
    reason: Optional[str] = None
    approver_email: Optional[str] = None
    status: Optional[str] = "pending"
    approved_at: Optional[datetime] = None
    is_demo: Optional[bool] = False


class EmailOutboxSchema(BaseModel):
    """Schema for email outbox."""
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    recipient: str
    subject: Optional[str] = None
    body: Optional[str] = None
    is_demo: Optional[bool] = False
