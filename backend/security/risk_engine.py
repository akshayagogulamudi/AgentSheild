"""Risk scoring engine that calculates risk scores 0-100."""
from typing import Dict, Tuple


class RiskScorer:
    """Calculates risk scores for security decisions based on policy violations and threats."""
    
    # Risk tiers
    TIER_LOW = "LOW"
    TIER_MEDIUM = "MEDIUM"
    TIER_HIGH = "HIGH"
    TIER_CRITICAL = "CRITICAL"
    
    def __init__(self):
        """Initialize risk scorer with scoring parameters."""
        # Base scores for violations
        self.base_scores = {
            "unknown_tool": 80,           # Unknown/unlisted tool
            "unauthorized_access": 70,   # Unauthorized resource access
            "tool_restriction": 50,      # Tool exists but with restrictions
            "policy_violation": 60,      # Generic policy violation
        }
        
        # Injection score contribution (0-30)
        self.injection_max = 30
        
        # DLP score contribution (0-40)
        self.dlp_max = 40
    
    def calculate_risk(
        self,
        tool_name: str,
        policy_violations: Dict,
        injection_score: float = 0.0,
        dlp_score: float = 0.0
    ) -> Tuple[int, str]:
        """
        Calculate overall risk score.
        
        Args:
            tool_name: Name of the tool being requested
            policy_violations: Dict with violation info:
                - type: (str) violation type (unknown_tool, unauthorized_access, etc.)
                - severity: (int) base score for this violation
            injection_score: Confidence score from prompt injection detector (0.0-1.0)
            dlp_score: DLP finding severity contribution (0.0-1.0)
            
        Returns:
            Tuple of (risk_score, risk_tier)
            - risk_score: Integer 0-100
            - risk_tier: String (LOW, MEDIUM, HIGH, CRITICAL)
        """
        base_score = 0.0
        
        # Get base score from policy violation
        violation_type = policy_violations.get("type", "policy_violation")
        base_score = self.base_scores.get(violation_type, 40)
        
        # Add injection detection contribution
        if injection_score > 0:
            base_score += injection_score * self.injection_max
        
        # Add DLP contribution
        if dlp_score > 0:
            base_score += dlp_score * self.dlp_max
        
        # Cap at 100
        risk_score = min(int(base_score), 100)
        
        # Determine tier
        risk_tier = self._get_tier(risk_score)
        
        return risk_score, risk_tier
    
    def _get_tier(self, score: int) -> str:
        """
        Map risk score to tier.
        
        Args:
            score: Risk score 0-100
            
        Returns:
            Risk tier: LOW (0-29), MEDIUM (30-59), HIGH (60-79), CRITICAL (80-100)
        """
        if score < 30:
            return self.TIER_LOW
        elif score < 60:
            return self.TIER_MEDIUM
        elif score < 80:
            return self.TIER_HIGH
        else:
            return self.TIER_CRITICAL
    
    def calculate_injection_contribution(self, injection_confidence: float) -> float:
        """
        Calculate contribution of injection detection to risk.
        
        Args:
            injection_confidence: Confidence from injection detector (0.0-1.0)
            
        Returns:
            Score contribution (0.0-30.0)
        """
        return injection_confidence * self.injection_max
    
    def calculate_dlp_contribution(self, dlp_severity: str) -> float:
        """
        Calculate contribution of DLP findings to risk.
        
        Args:
            dlp_severity: Severity level from DLP engine (LOW, MEDIUM, HIGH)
            
        Returns:
            Score contribution (0.0-40.0)
        """
        severity_scores = {
            "LOW": 10,
            "MEDIUM": 25,
            "HIGH": 40,
        }
        return severity_scores.get(dlp_severity, 0)
    
    def calculate_intent_mismatch_contribution(self, mismatch_confidence: float) -> float:
        """
        Calculate risk contribution from intent mismatch.
        
        Args:
            mismatch_confidence: Confidence that intent is mismatched (0.0-1.0)
            
        Returns:
            Score contribution (0.0-20.0)
        """
        return mismatch_confidence * 20
