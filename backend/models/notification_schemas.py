"""Pydantic schemas for notifications."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class EmailDeliverySchema(BaseModel):
    """Email delivery status schema."""
    id: int
    notification_record_id: int
    recipient_email: str
    status: str  # pending, simulated, sent, failed
    subject: str
    body_preview: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class SMSDeliverySchema(BaseModel):
    """SMS delivery status schema."""
    id: int
    notification_record_id: int
    recipient_phone: str
    status: str  # pending, simulated, sent, failed
    message_preview: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class NotificationRecordSchema(BaseModel):
    """Notification record schema."""
    id: int
    security_event_id: int
    incident_id: str
    agent_name: str
    attempted_tool: str
    threat_category: str
    severity: str  # low, medium, high, critical
    decision: str  # BLOCK, REQUIRE_APPROVAL
    timestamp: datetime
    created_at: datetime
    last_notification_at: Optional[datetime] = None
    notification_count: int
    email_deliveries: Optional[list[EmailDeliverySchema]] = []
    sms_deliveries: Optional[list[SMSDeliverySchema]] = []

    class Config:
        from_attributes = True


class NotificationSummarySchema(BaseModel):
    """Summary of notifications."""
    total_critical: int = Field(description="Total critical severity notifications")
    total_high: int = Field(description="Total high severity notifications")
    unread_count: int = Field(description="Count of unread notifications")
    recent_incidents: list[dict] = Field(description="Last 5 incidents")


class NotificationHistorySchema(BaseModel):
    """Pagination schema for notification history."""
    items: list[NotificationRecordSchema]
    total: int
    limit: int
    offset: int
