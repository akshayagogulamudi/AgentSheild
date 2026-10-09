"""Notification service for email and SMS threat alerts."""
import os
import json
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models import (
    NotificationRecord, EmailDelivery, SMSDelivery,
    NotificationStatus
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Orchestrate email and SMS threat notifications."""

    def __init__(self, db: Session):
        """Initialize notification service."""
        self.db = db
        self.mode = os.getenv("NOTIFICATION_MODE", "mock").lower()
        self.min_severity = os.getenv("NOTIFICATION_MIN_SEVERITY", "high").lower()
        self.dedup_window_minutes = int(os.getenv("NOTIFICATION_DEDUP_WINDOW_MINUTES", "30"))

        # Email config
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.alert_email_to = os.getenv("ALERT_EMAIL_TO", "security@company.com").split(",")

        # SMS config (Twilio)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER", "")
        self.alert_phone_to = os.getenv("ALERT_PHONE_TO", "").split(",") if os.getenv("ALERT_PHONE_TO") else []

        # Lazy load Twilio client
        self._twilio_client = None

    @property
    def twilio_client(self):
        """Lazy load Twilio client."""
        if self._twilio_client is None and self.twilio_account_sid:
            try:
                from twilio.rest import Client
                self._twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
        return self._twilio_client

    def should_notify(self, severity: str) -> bool:
        """Check if notification should be sent based on severity threshold."""
        severity_levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        return severity_levels.get(severity.lower(), 0) >= severity_levels.get(self.min_severity, 2)

    def should_deduplicate(self, incident_id: str) -> bool:
        """Check if this incident was recently notified (deduplication)."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.dedup_window_minutes)

        existing = self.db.query(NotificationRecord).filter(
            NotificationRecord.incident_id == incident_id,
            NotificationRecord.last_notification_at >= cutoff_time
        ).first()

        return existing is not None

    def create_notification_record(
        self,
        security_event_id: int,
        incident_id: str,
        agent_name: str,
        attempted_tool: str,
        threat_category: str,
        severity: str,
        decision: str
    ) -> NotificationRecord:
        """Create a notification record for tracking."""
        record = NotificationRecord(
            security_event_id=security_event_id,
            incident_id=incident_id,
            agent_name=agent_name,
            attempted_tool=attempted_tool,
            threat_category=threat_category,
            severity=severity,
            decision=decision,
            is_demo=False
        )
        self.db.add(record)
        self.db.commit()
        return record

    def send_email_notification(
        self,
        notification_record_id: int,
        recipient_email: str,
        subject: str,
        body: str,
        incident_id: str
    ) -> EmailDelivery:
        """Send (or simulate) email notification."""
        
        # Sanitize body - never include raw secrets
        sanitized_body = self._sanitize_content(body)
        body_preview = sanitized_body[:500]

        email_delivery = EmailDelivery(
            notification_record_id=notification_record_id,
            recipient_email=recipient_email,
            subject=subject,
            body_preview=body_preview,
            is_demo=False
        )

        if self.mode == "mock":
            # Mock mode: simulate without sending
            email_delivery.status = NotificationStatus.SIMULATED
            logger.info(f"[MOCK] Email notification would be sent to {recipient_email}")
            logger.info(f"[MOCK] Subject: {subject}")
            logger.info(f"[MOCK] Body preview: {body_preview[:200]}...")
        else:
            # Live mode: attempt actual delivery
            try:
                self._send_smtp(recipient_email, subject, sanitized_body)
                email_delivery.status = NotificationStatus.SENT
                email_delivery.sent_at = datetime.utcnow()
                logger.info(f"Email notification sent to {recipient_email} (incident: {incident_id})")
            except Exception as e:
                email_delivery.status = NotificationStatus.FAILED
                email_delivery.error_message = str(e)
                logger.error(f"Failed to send email to {recipient_email}: {e}")

        self.db.add(email_delivery)
        self.db.commit()
        return email_delivery

    def send_sms_notification(
        self,
        notification_record_id: int,
        recipient_phone: str,
        message: str,
        incident_id: str
    ) -> SMSDelivery:
        """Send (or simulate) SMS notification."""
        
        # Sanitize message - SMS is 160 chars
        sanitized_message = self._sanitize_content(message)
        message_preview = sanitized_message[:160]

        sms_delivery = SMSDelivery(
            notification_record_id=notification_record_id,
            recipient_phone=recipient_phone,
            message_preview=message_preview,
            is_demo=False
        )

        if self.mode == "mock":
            # Mock mode: simulate without sending
            sms_delivery.status = NotificationStatus.SIMULATED
            logger.info(f"[MOCK] SMS notification would be sent to {recipient_phone}")
            logger.info(f"[MOCK] Message: {message_preview}")
        else:
            # Live mode: attempt actual delivery
            if not self.twilio_client:
                sms_delivery.status = NotificationStatus.FAILED
                sms_delivery.error_message = "Twilio client not configured"
                logger.error("Twilio not configured")
            else:
                try:
                    msg = self.twilio_client.messages.create(
                        body=sanitized_message,
                        from_=self.twilio_phone_number,
                        to=recipient_phone
                    )
                    sms_delivery.status = NotificationStatus.SENT
                    sms_delivery.sent_at = datetime.utcnow()
                    sms_delivery.provider_reference = msg.sid
                    logger.info(f"SMS notification sent to {recipient_phone} (incident: {incident_id})")
                except Exception as e:
                    sms_delivery.status = NotificationStatus.FAILED
                    sms_delivery.error_message = str(e)
                    logger.error(f"Failed to send SMS to {recipient_phone}: {e}")

        self.db.add(sms_delivery)
        self.db.commit()
        return sms_delivery

    def notify_on_threat(
        self,
        security_event_id: int,
        agent_name: str,
        attempted_tool: str,
        threat_category: str,
        severity: str,
        decision: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Optional[NotificationRecord]:
        """
        Main entry point for threat notifications.
        
        Called after security gateway makes a BLOCK or REQUIRE_APPROVAL decision.
        Uses mock mode by default.
        """
        
        # Check if we should notify based on severity
        if not self.should_notify(severity):
            logger.debug(f"Skipping notification for {severity} severity (below threshold)")
            return None

        # Generate incident ID
        incident_id = f"inc-{security_event_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Check deduplication
        if self.should_deduplicate(incident_id):
            logger.info(f"Skipping duplicate notification for {incident_id}")
            return None

        # Create notification record
        notification = self.create_notification_record(
            security_event_id=security_event_id,
            incident_id=incident_id,
            agent_name=agent_name,
            attempted_tool=attempted_tool,
            threat_category=threat_category,
            severity=severity,
            decision=decision
        )

        # Build notification messages
        email_subject = self._build_email_subject(severity, decision, agent_name)
        email_body = self._build_email_body(
            incident_id, agent_name, attempted_tool, threat_category, severity, decision, arguments
        )
        sms_message = self._build_sms_message(
            incident_id, agent_name, attempted_tool, severity, decision
        )

        # Send email notifications
        for email_address in self.alert_email_to:
            email_address = email_address.strip()
            if email_address:
                self.send_email_notification(
                    notification.id, email_address, email_subject, email_body, incident_id
                )

        # Send SMS notifications
        for phone_number in self.alert_phone_to:
            phone_number = phone_number.strip()
            if phone_number:
                self.send_sms_notification(
                    notification.id, phone_number, sms_message, incident_id
                )

        # Update last notification time
        notification.last_notification_at = datetime.utcnow()
        notification.notification_count += 1
        self.db.commit()

        return notification

    def _sanitize_content(self, content: str) -> str:
        """Remove sensitive data from notification content."""
        import re
        
        # Remove common secret patterns
        patterns = [
            r'(?i)(api[_-]?key|secret|password|token|bearer)\s*[:=]\s*["\']?([^\s"\']+)["\']?',
            r'(?i)(sk_[a-z0-9]{20,})',  # Stripe keys
            r'(?i)([A-Z0-9]{20,})',  # Generic long keys
        ]
        
        sanitized = content
        for pattern in patterns:
            sanitized = re.sub(pattern, r'\1=[REDACTED]', sanitized)
        
        return sanitized

    def _build_email_subject(self, severity: str, decision: str, agent_name: str) -> str:
        """Build email subject line."""
        severity_emoji = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "⚠️",
            "low": "ℹ️"
        }.get(severity.lower(), "ℹ️")
        
        decision_text = "BLOCKED" if decision == "BLOCK" else "APPROVAL REQUIRED"
        return f"{severity_emoji} Security Alert: {decision_text} - Agent: {agent_name}"

    def _build_email_body(
        self,
        incident_id: str,
        agent_name: str,
        attempted_tool: str,
        threat_category: str,
        severity: str,
        decision: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build email body with incident details."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        body = f"""
AgentShield AI Security Alert
==============================

Incident ID: {incident_id}
Timestamp: {timestamp}
Severity: {severity.upper()}
Decision: {decision}

THREAT DETAILS:
---------------
Agent: {agent_name}
Attempted Tool: {attempted_tool}
Threat Category: {threat_category}

ACTION TAKEN:
The security gateway has {decision.lower()} this operation to prevent potential harm.

INVESTIGATION:
Review this incident in the AgentShield dashboard: 
https://agentshield.example.com/dashboard?incident={incident_id}

---
This is an automated security notification from AgentShield AI.
Never reply with sensitive information to this email.
"""
        return body

    def _build_sms_message(
        self,
        incident_id: str,
        agent_name: str,
        attempted_tool: str,
        severity: str,
        decision: str
    ) -> str:
        """Build SMS message (limited to ~160 chars)."""
        severity_short = severity[0].upper()
        decision_short = "BLOCKED" if decision == "BLOCK" else "APPROVAL"
        
        message = f"[{severity_short}] AgentShield: Agent '{agent_name}' attempted '{attempted_tool}' - {decision_short}. Incident: {incident_id}"
        
        # Truncate to SMS limit
        if len(message) > 160:
            message = message[:157] + "..."
        
        return message

    def _send_smtp(self, recipient: str, subject: str, body: str) -> None:
        """Send email via SMTP."""
        if not self.smtp_username or not self.smtp_password:
            raise ValueError("SMTP credentials not configured (SMTP_USERNAME, SMTP_PASSWORD)")

        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)

    def get_notification_history(
        self,
        db: Session,
        limit: int = 50,
        offset: int = 0,
        severity: Optional[str] = None
    ) -> tuple[list[NotificationRecord], int]:
        """Fetch notification history."""
        query = db.query(NotificationRecord).order_by(NotificationRecord.created_at.desc())

        if severity:
            query = query.filter(NotificationRecord.severity == severity)

        total = query.count()
        records = query.limit(limit).offset(offset).all()

        return records, total

    def get_unread_count(self, db: Session) -> int:
        """Get count of unread notifications (created in last 24 hours)."""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        count = db.query(NotificationRecord).filter(
            NotificationRecord.created_at >= cutoff
        ).count()
        return count

    def get_summary(self, db: Session) -> Dict[str, Any]:
        """Get notification summary."""
        critical_count = db.query(NotificationRecord).filter(
            NotificationRecord.severity == "critical"
        ).count()

        high_count = db.query(NotificationRecord).filter(
            NotificationRecord.severity == "high"
        ).count()

        unread_count = self.get_unread_count(db)

        # Recent incidents
        recent = db.query(NotificationRecord).order_by(
            NotificationRecord.created_at.desc()
        ).limit(5).all()

        return {
            "total_critical": critical_count,
            "total_high": high_count,
            "unread_count": unread_count,
            "recent_incidents": [
                {
                    "incident_id": r.incident_id,
                    "severity": r.severity,
                    "agent_name": r.agent_name,
                    "threat_category": r.threat_category,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in recent
            ]
        }
