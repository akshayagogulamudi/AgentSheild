from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()


class SecurityClassification(str, enum.Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    RESTRICTED = "RESTRICTED"


class SecurityEventDecision(str, enum.Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True)
    role = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    allowed_tools = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Policy(role={self.role})>"


class SimulatedFile(Base):
    __tablename__ = "simulated_files"

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    classification = Column(Enum(SecurityClassification), default=SecurityClassification.PUBLIC)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<SimulatedFile(filename={self.filename}, classification={self.classification})>"


class SimulatedRecord(Base):
    __tablename__ = "simulated_records"

    id = Column(Integer, primary_key=True)
    record_type = Column(String(50))  # employee, customer, financial, etc.
    data = Column(Text, nullable=False)  # JSON string
    classification = Column(Enum(SecurityClassification), default=SecurityClassification.INTERNAL)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<SimulatedRecord(record_type={self.record_type})>"


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String(100), nullable=False)
    requested_tool = Column(String(100), nullable=False)
    arguments = Column(Text)  # JSON string
    decision = Column(Enum(SecurityEventDecision), nullable=False)
    risk_score = Column(Float, default=0.0)
    reason = Column(Text)
    checks_passed = Column(Text)  # JSON array
    checks_failed = Column(Text)  # JSON array
    is_demo = Column(Boolean, default=False)

    def __repr__(self):
        return f"<SecurityEvent(tool={self.requested_tool}, decision={self.decision})>"


class Threat(Base):
    __tablename__ = "threats"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("security_events.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    threat_category = Column(String(100), nullable=False)  # prompt_injection, unauthorized_access, etc.
    severity = Column(String(20))  # low, medium, high, critical
    agent_identifier = Column(String(100))
    requested_action = Column(Text)
    reason_for_detection = Column(Text)
    gateway_response = Column(String(50))  # allowed, blocked, pending
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Threat(category={self.threat_category}, severity={self.severity})>"


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    actor = Column(String(100))
    action = Column(String(200), nullable=False)
    details = Column(Text)  # JSON string
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<ActivityLog(action={self.action})>"


class PendingApproval(Base):
    __tablename__ = "pending_approvals"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("security_events.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String(100), nullable=False)
    tool_name = Column(String(100), nullable=False)
    arguments = Column(Text)  # JSON string
    reason = Column(Text)
    approver_email = Column(String(100))
    status = Column(String(20), default="pending")  # pending, approved, rejected
    approved_at = Column(DateTime, nullable=True)
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<PendingApproval(tool={self.tool_name}, status={self.status})>"


class EmailOutbox(Base):
    __tablename__ = "email_outbox"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    recipient = Column(String(100), nullable=False)
    subject = Column(String(255))
    body = Column(Text)
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<EmailOutbox(to={self.recipient})>"



# ===== NOTIFICATION MODELS =====

class NotificationStatus(str, enum.Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SIMULATED = "simulated"
    SENT = "sent"
    FAILED = "failed"


class NotificationChannel(str, enum.Enum):
    """Notification delivery channel."""
    EMAIL = "email"
    SMS = "sms"


class NotificationRecord(Base):
    """Track all threat notifications."""
    __tablename__ = "notification_records"

    id = Column(Integer, primary_key=True)
    security_event_id = Column(Integer, ForeignKey("security_events.id"), nullable=False)
    incident_id = Column(String(50), unique=True, nullable=False)
    agent_name = Column(String(100), nullable=False)
    attempted_tool = Column(String(100), nullable=False)
    threat_category = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False)
    decision = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_notification_at = Column(DateTime, nullable=True)
    notification_count = Column(Integer, default=0)
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<NotificationRecord(incident_id={self.incident_id}, severity={self.severity})>"


class EmailDelivery(Base):
    """Track email notification delivery."""
    __tablename__ = "email_deliveries"

    id = Column(Integer, primary_key=True)
    notification_record_id = Column(Integer, ForeignKey("notification_records.id"), nullable=False)
    recipient_email = Column(String(100), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    subject = Column(String(255))
    body_preview = Column(String(500))
    error_message = Column(Text, nullable=True)
    provider_reference = Column(String(255), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<EmailDelivery(to={self.recipient_email}, status={self.status})>"


class SMSDelivery(Base):
    """Track SMS notification delivery."""
    __tablename__ = "sms_deliveries"

    id = Column(Integer, primary_key=True)
    notification_record_id = Column(Integer, ForeignKey("notification_records.id"), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    message_preview = Column(String(160))
    error_message = Column(Text, nullable=True)
    provider_reference = Column(String(255), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_demo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<SMSDelivery(to={self.recipient_phone}, status={self.status})>"
