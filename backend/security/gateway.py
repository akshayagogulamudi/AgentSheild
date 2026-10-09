"""Core security gateway that orchestrates all security checks."""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import SecurityEvent, PendingApproval, SecurityEventDecision

from .policy_engine import PolicyEngine
from .injection_detector import PromptInjectionDetector
from .dlp_engine import DataLeakagePreventionEngine
from .risk_engine import RiskScorer
from .intent_validator import IntentValidator


class CheckResult:
    """Result of a single security check."""
    
    def __init__(self, name: str, passed: bool, reason: str, details: Dict = None):
        """
        Initialize check result.
        
        Args:
            name: Check name (e.g., "tool_permission")
            passed: Whether check passed
            reason: Explanation of result
            details: Additional details (optional)
        """
        self.name = name
        self.passed = passed
        self.reason = reason
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "passed": self.passed,
            "reason": self.reason,
            "details": self.details
        }


class GatewayDecision:
    """Final security gateway decision."""
    
    def __init__(
        self,
        decision: str,
        risk_score: int,
        risk_tier: str,
        explanation: str,
        checks: List[CheckResult],
        requires_approval: bool = False,
        pending_approval_id: Optional[int] = None
    ):
        """
        Initialize gateway decision.
        
        Args:
            decision: ALLOW, BLOCK, or REQUIRE_APPROVAL
            risk_score: Risk score 0-100
            risk_tier: Risk tier (LOW, MEDIUM, HIGH, CRITICAL)
            explanation: Summary of decision
            checks: List of CheckResult objects
            requires_approval: Whether approval is needed
            pending_approval_id: ID of pending approval if one was created
        """
        self.decision = decision
        self.risk_score = risk_score
        self.risk_tier = risk_tier
        self.explanation = explanation
        self.checks = checks
        self.requires_approval = requires_approval
        self.pending_approval_id = pending_approval_id
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "decision": self.decision,
            "risk_score": self.risk_score,
            "risk_tier": self.risk_tier,
            "explanation": self.explanation,
            "checks": [c.to_dict() for c in self.checks],
            "requires_approval": self.requires_approval,
            "pending_approval_id": self.pending_approval_id
        }


class GatewayEngine:
    """Orchestrates all security checks for tool execution."""
    
    def __init__(self, db: Session):
        """
        Initialize gateway engine.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.policy_engine = PolicyEngine(db)
        self.injection_detector = PromptInjectionDetector()
        self.dlp_engine = DataLeakagePreventionEngine()
        self.risk_scorer = RiskScorer()
        self.intent_validator = IntentValidator()
    
    def evaluate(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user_request: Optional[str] = None,
        agent_name: str = "default_agent",
        agent_role: str = "employee"
    ) -> GatewayDecision:
        """
        Evaluate a tool execution request through all security gates.
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments/parameters
            user_request: Original user request for intent validation
            agent_name: Name of requesting agent
            agent_role: Role/permission level of agent
            
        Returns:
            GatewayDecision with result and reasoning
        """
        checks = []
        violations = []
        
        # ===== CHECK 1: Tool Permission Validation =====
        tool_permitted, tool_reason = self.policy_engine.can_execute_tool(tool_name, agent_role)
        checks.append(CheckResult("tool_permission", tool_permitted, tool_reason))
        
        if not tool_permitted:
            violations.append({
                "type": "unknown_tool",
                "severity": 80
            })
        
        # ===== CHECK 2: Intent Validation =====
        aligned = True
        mismatch_confidence = 0.0
        intent_reason = "No user request provided for intent validation"
        
        if user_request:
            aligned, mismatch_confidence, intent_reason = self.intent_validator.compare_intent(
                user_request,
                str(arguments),
                tool_name
            )
        
        checks.append(CheckResult("intent_validation", aligned, intent_reason))
        
        if not aligned and mismatch_confidence > 0.7:
            violations.append({
                "type": "intent_mismatch",
                "severity": 60
            })
        
        # ===== CHECK 3: Prompt Injection Detection =====
        injection_suspicious = False
        injection_confidence = 0.0
        injection_indicators = []
        
        # Scan arguments for injection patterns
        args_str = json.dumps(arguments) if isinstance(arguments, dict) else str(arguments)
        injection_suspicious, injection_confidence, injection_indicators = self.injection_detector.analyze_with_fuzzy_match(args_str)
        
        injection_reason = f"{'✓ No injection patterns detected' if not injection_suspicious else f'⚠ Suspicious patterns found (confidence: {injection_confidence:.1%})'}"
        checks.append(CheckResult(
            "prompt_injection",
            not injection_suspicious,
            injection_reason,
            {"indicators": injection_indicators[:3]}  # Limit to first 3
        ))
        
        if injection_suspicious and injection_confidence > 0.5:
            violations.append({
                "type": "prompt_injection",
                "severity": 70
            })
        
        # ===== CHECK 4: Data Leakage Prevention =====
        dlp_violation = False
        dlp_findings = []
        dlp_severity = "LOW"
        
        # Scan arguments for sensitive data
        args_str = json.dumps(arguments) if isinstance(arguments, dict) else str(arguments)
        dlp_contains_sensitive, dlp_findings, dlp_severity = self.dlp_engine.scan_for_sensitive_data(args_str)
        
        dlp_reason = f"{'✓ No sensitive data detected' if not dlp_contains_sensitive else f'⚠ Sensitive data found: {dlp_severity} severity'}"
        checks.append(CheckResult(
            "data_leakage_prevention",
            not dlp_contains_sensitive,
            dlp_reason,
            {"findings": dlp_findings[:3]}  # Limit to first 3
        ))
        
        if dlp_contains_sensitive and dlp_severity in ["MEDIUM", "HIGH"]:
            dlp_violation = True
            violations.append({
                "type": "data_leakage",
                "severity": 75
            })
        
        # ===== CHECK 5: Resource Authorization =====
        resource_auth_passed = True
        resource_reason = "✓ Resource authorization OK"
        
        # For read_file, check document classification
        if tool_name == "read_file" and "filename" in arguments:
            filename = arguments["filename"]
            # Check if role can access this file
            can_access, access_reason = self.policy_engine.can_access_resource(
                filename,
                "file",
                agent_role
            )
            resource_auth_passed = can_access
            resource_reason = access_reason
            
            if not can_access:
                violations.append({
                    "type": "unauthorized_access",
                    "severity": 70
                })
        
        checks.append(CheckResult("resource_authorization", resource_auth_passed, resource_reason))
        
        # ===== CHECK 6: Argument Validation =====
        arg_validation_passed = True
        arg_reason = "✓ Arguments valid"
        
        if tool_name == "send_email":
            if "recipient" in arguments:
                recipient = arguments["recipient"]
                if not self.policy_engine.is_recipient_allowed(recipient, agent_role):
                    arg_validation_passed = False
                    arg_reason = f"Recipient '{recipient}' not allowed for role '{agent_role}'"
                    violations.append({
                        "type": "unauthorized_recipient",
                        "severity": 65
                    })
        
        checks.append(CheckResult("argument_validation", arg_validation_passed, arg_reason))
        
        # ===== CALCULATE RISK SCORE =====
        # Determine primary violation
        primary_violation = {
            "type": "none",
            "severity": 0
        }
        
        if violations:
            primary_violation = max(violations, key=lambda v: v["severity"])
        
        # Calculate risk score components
        injection_score = self.risk_scorer.calculate_injection_contribution(injection_confidence)
        dlp_score = self.risk_scorer.calculate_dlp_contribution(dlp_severity) if dlp_contains_sensitive else 0.0
        
        risk_score, risk_tier = self.risk_scorer.calculate_risk(
            tool_name,
            primary_violation,
            injection_score / 100.0,  # Normalize to 0-1
            dlp_score / 100.0  # Normalize to 0-1
        )
        
        # ===== DETERMINE FINAL DECISION =====
        decision = SecurityEventDecision.ALLOW
        explanation = "✓ All security checks passed"
        requires_approval = False
        pending_approval_id = None
        
        # Hard blocks: policy violations override risk score
        if not tool_permitted:
            decision = SecurityEventDecision.BLOCK
            explanation = f"✗ Tool '{tool_name}' is not permitted for role '{agent_role}'"
        
        elif not resource_auth_passed:
            decision = SecurityEventDecision.BLOCK
            explanation = f"✗ Access to resource denied: {resource_reason}"
        
        elif injection_suspicious and injection_confidence > 0.6:
            decision = SecurityEventDecision.BLOCK
            explanation = f"✗ Prompt injection detected with high confidence ({injection_confidence:.0%})"
        
        elif dlp_violation:
            decision = SecurityEventDecision.BLOCK
            explanation = f"✗ Sensitive data detected in arguments ({dlp_severity})"
        
        elif tool_name == "send_email" and self.policy_engine.is_approval_required(tool_name, agent_role):
            decision = SecurityEventDecision.REQUIRE_APPROVAL
            explanation = f"⚠ Email send requires approval for role '{agent_role}'"
            requires_approval = True
            
            # Create pending approval
            pending = PendingApproval(
                agent_name=agent_name,
                tool_name=tool_name,
                arguments=json.dumps(arguments),
                reason=f"External email send request by {agent_name}",
                approver_email="admin@company.com",
                status="pending",
                is_demo=False
            )
            self.db.add(pending)
            self.db.commit()
            pending_approval_id = pending.id
        
        elif risk_score >= 70 and not all(check.passed for check in checks):
            # High risk with failed checks might require approval
            if not all([tool_permitted, resource_auth_passed, arg_validation_passed]):
                decision = SecurityEventDecision.BLOCK
                explanation = f"✗ Multiple security checks failed (risk score: {risk_score})"
        
        # Record security event
        event = SecurityEvent(
            agent_name=agent_name,
            requested_tool=tool_name,
            arguments=json.dumps(arguments),
            decision=decision,
            risk_score=float(risk_score),
            reason=explanation,
            checks_passed=json.dumps([c.name for c in checks if c.passed]),
            checks_failed=json.dumps([c.name for c in checks if not c.passed]),
            is_demo=False
        )
        self.db.add(event)
        self.db.commit()
        
        return GatewayDecision(
            decision=decision.value,
            risk_score=risk_score,
            risk_tier=risk_tier,
            explanation=explanation,
            checks=checks,
            requires_approval=requires_approval,
            pending_approval_id=pending_approval_id
        )
