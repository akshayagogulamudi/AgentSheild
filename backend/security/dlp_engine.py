"""Data Leakage Prevention engine for detecting sensitive data."""
import re
from typing import Tuple, List, Dict


class DataLeakagePreventionEngine:
    """Detects and prevents transmission of sensitive data."""
    
    # Severity levels
    SEVERITY_LOW = "LOW"
    SEVERITY_MEDIUM = "MEDIUM"
    SEVERITY_HIGH = "HIGH"
    
    # Data types
    API_KEY = "API_KEY"
    PASSWORD = "PASSWORD"
    RESTRICTED_CONTENT = "RESTRICTED_CONTENT"
    CREDIT_CARD = "CREDIT_CARD"
    SSN = "SSN"
    
    def __init__(self):
        """Initialize DLP engine with detection patterns."""
        self.patterns = {
            self.API_KEY: [
                (r"api[_-]?key\s*[=:]\s*['\"]?([a-zA-Z0-9_\-\.]+)['\"]?", 0.9, self.SEVERITY_HIGH),
                (r"sk[-_]?[a-zA-Z0-9]{20,}", 0.85, self.SEVERITY_HIGH),  # OpenAI-like keys
                (r"RESTRICTED_[A-Z_]+\s*=\s*['\"]?[^\s'\"]+['\"]?", 0.95, self.SEVERITY_HIGH),
                (r"secret[_-]?key\s*[=:]\s*['\"]?[^\s'\"]+['\"]?", 0.90, self.SEVERITY_HIGH),
                (r"authorization[_-]?token\s*[=:]\s*['\"]?[^\s'\"]+['\"]?", 0.85, self.SEVERITY_HIGH),
            ],
            self.PASSWORD: [
                (r"password\s*[=:]\s*['\"]?([^\s'\"]+)['\"]?", 0.90, self.SEVERITY_HIGH),
                (r"pwd\s*[=:]\s*['\"]?([^\s'\"]+)['\"]?", 0.85, self.SEVERITY_HIGH),
                (r"pass\s*[=:]\s*['\"]?([^\s'\"]+)['\"]?", 0.85, self.SEVERITY_MEDIUM),
                (r"credential\s*[=:]\s*['\"]?([^\s'\"]+)['\"]?", 0.80, self.SEVERITY_HIGH),
                (r"secret\s*[=:]\s*['\"]?([^\s'\"]+)['\"]?", 0.80, self.SEVERITY_MEDIUM),
            ],
            self.RESTRICTED_CONTENT: [
                (r"RESTRICTED|CONFIDENTIAL|SECRET|CLASSIFIED", 0.95, self.SEVERITY_HIGH),
                (r"For.*eyes.*only|Internal.*Only", 0.90, self.SEVERITY_HIGH),
            ],
            self.CREDIT_CARD: [
                (r"\b(?:\d[ -]*?){13,19}\b", 0.85, self.SEVERITY_HIGH),  # Credit card patterns
                (r"\b4[0-9]{12}(?:[0-9]{3})?\b|\b5[1-5][0-9]{14}\b", 0.95, self.SEVERITY_HIGH),
            ],
            self.SSN: [
                (r"\b\d{3}-\d{2}-\d{4}\b", 0.95, self.SEVERITY_HIGH),  # XXX-XX-XXXX
            ],
        }
    
    def scan_for_sensitive_data(self, text: str, context: str = "") -> Tuple[bool, List[Dict], str]:
        """
        Scan text for sensitive data patterns.
        
        Args:
            text: Text to scan (e.g., tool arguments, content to send)
            context: Additional context (e.g., 'email_body', 'file_content')
            
        Returns:
            Tuple of (contains_sensitive, data_types_found, severity)
            - contains_sensitive: True if sensitive data detected
            - data_types_found: List of dicts with type, pattern, confidence, severity
            - severity: Overall severity (LOW/MEDIUM/HIGH)
        """
        if not text:
            return False, [], self.SEVERITY_LOW
        
        text_normalized = str(text).lower()
        found_data_types = []
        max_severity = self.SEVERITY_LOW
        
        for data_type, patterns in self.patterns.items():
            for pattern, confidence, severity in patterns:
                matches = re.finditer(pattern, text_normalized, re.IGNORECASE)
                for match in matches:
                    found_data_types.append({
                        "type": data_type,
                        "pattern": match.group(0)[:50],  # Truncate for safety
                        "confidence": confidence,
                        "severity": severity
                    })
                    
                    # Update max severity
                    if severity == self.SEVERITY_HIGH:
                        max_severity = self.SEVERITY_HIGH
                    elif severity == self.SEVERITY_MEDIUM and max_severity != self.SEVERITY_HIGH:
                        max_severity = self.SEVERITY_MEDIUM
        
        contains_sensitive = len(found_data_types) > 0
        
        return contains_sensitive, found_data_types, max_severity
    
    def has_api_key(self, text: str) -> bool:
        """
        Check if text contains API key patterns.
        
        Args:
            text: Text to check
            
        Returns:
            True if API key pattern detected
        """
        if not text:
            return False
        
        text_normalized = str(text).lower()
        for pattern, _, _ in self.patterns[self.API_KEY]:
            if re.search(pattern, text_normalized, re.IGNORECASE):
                return True
        
        return False
    
    def has_password(self, text: str) -> bool:
        """
        Check if text contains password patterns.
        
        Args:
            text: Text to check
            
        Returns:
            True if password pattern detected
        """
        if not text:
            return False
        
        text_normalized = str(text).lower()
        for pattern, _, _ in self.patterns[self.PASSWORD]:
            if re.search(pattern, text_normalized, re.IGNORECASE):
                return True
        
        return False
    
    def has_restricted_marker(self, text: str) -> bool:
        """
        Check if text contains restricted content markers.
        
        Args:
            text: Text to check
            
        Returns:
            True if restricted marker detected
        """
        if not text:
            return False
        
        text_upper = str(text).upper()
        markers = ["RESTRICTED", "CONFIDENTIAL", "SECRET", "CLASSIFIED", "FOR OFFICIAL USE ONLY"]
        
        for marker in markers:
            if marker in text_upper:
                return True
        
        return False
    
    def check_recipient(self, recipient: str) -> Dict:
        """
        Check if recipient looks suspicious (external, suspicious domains, etc.).
        
        Args:
            recipient: Email address or identifier
            
        Returns:
            Dict with is_suspicious, reason, confidence
        """
        recipient_lower = str(recipient).lower()
        
        suspicious_indicators = {
            "external": [".ru", ".cn", ".pk", "gmail", "yahoo", "hotmail"],
            "suspicious": ["attacker", "hacker", "malicious", "external", "outsider"],
        }
        
        for category, indicators in suspicious_indicators.items():
            for indicator in indicators:
                if indicator in recipient_lower:
                    return {
                        "is_suspicious": True,
                        "reason": f"Recipient matches suspicious pattern: {indicator}",
                        "category": category
                    }
        
        return {
            "is_suspicious": False,
            "reason": "Recipient looks legitimate",
            "category": None
        }
