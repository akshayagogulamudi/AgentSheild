"""Email sending tool stub - simulated, non-functional."""
import json
from sqlalchemy.orm import Session
from database.models import EmailOutbox, ActivityLog


def send_email(recipient: str, subject: str, body: str, db: Session = None) -> dict:
    """
    Send a simulated email (never sends real emails).
    
    Args:
        recipient: Email recipient address
        subject: Email subject
        body: Email body
        db: Database session
        
    Returns:
        Dictionary with result
    """
    if db is None:
        return {"success": False, "error": "Database session required"}
    
    try:
        # Store in email outbox (never actually sends)
        email = EmailOutbox(
            recipient=recipient,
            subject=subject,
            body=body,
            is_demo=False
        )
        db.add(email)
        db.commit()
        
        # Record activity
        activity = ActivityLog(
            actor="tool_executor",
            action="send_email",
            details=json.dumps({
                "recipient": recipient,
                "subject": subject,
                "body_length": len(body),
                "success": True,
                "note": "Simulated - no real email sent"
            }),
            is_demo=False
        )
        db.add(activity)
        db.commit()
        
        return {
            "success": True,
            "recipient": recipient,
            "subject": subject,
            "message": "Email stored in outbox (simulated, not sent)",
            "tool": "send_email"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": "send_email"
        }
