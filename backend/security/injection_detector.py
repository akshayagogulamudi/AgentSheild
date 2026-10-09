"""Prompt injection detection engine using heuristic patterns."""
import re
from typing import Tuple, List, Dict
from difflib import SequenceMatcher


class PromptInjectionDetector:
    """Detects malicious instructions embedded in untrusted content using heuristic patterns."""
    
    # Indicator types
    IGNORE_INSTRUCTIONS = "IGNORE_INSTRUCTIONS"
    REVEAL_SECRET = "REVEAL_SECRET"
    OVERRIDE_SYSTEM = "OVERRIDE_SYSTEM"
    EXECUTE_TOOL = "EXECUTE_TOOL"
    EXFILTRATE_DATA = "EXFILTRATE_DATA"
    
    def __init__(self):
        """Initialize detector with pattern rules."""
        # Patterns: (regex, indicator_type, confidence_boost)
        self.patterns = [
            # Ignore/override system instructions
            (r"ignore\s+(previous|earlier|all|existing|your)\s+(instructions|prompts|guidelines|rules|system|directives)", 
             self.IGNORE_INSTRUCTIONS, 0.30),
            (r"disregard\s+(previous|earlier|all|your)\s+(instructions|prompts|guidelines|rules|system)", 
             self.IGNORE_INSTRUCTIONS, 0.25),
            (r"forget\s+(what|all|your)\s+(instructions|prompts|guidelines|rules|system)", 
             self.IGNORE_INSTRUCTIONS, 0.20),
            (r"override\s+(previous|system|safety|security)\s+(instructions|constraints|rules|guidelines)", 
             self.OVERRIDE_SYSTEM, 0.30),
            (r"bypass\s+(security|safety|access|restrictions|permissions|controls)", 
             self.OVERRIDE_SYSTEM, 0.25),
            (r"disable\s+(safety|security|restrictions|controls|protections)", 
             self.OVERRIDE_SYSTEM, 0.25),
            
            # Reveal secrets/confidential info
            (r"reveal\s+(your\s+)?(secret|password|key|credential|token|api.?key|confidential|restricted|sensitive)\s+(information|data|content|value)", 
             self.REVEAL_SECRET, 0.35),
            (r"show\s+(me\s+)?(the|all)\s+(password|secret|key|credential|token|api.?key|confidential)\s+", 
             self.REVEAL_SECRET, 0.30),
            (r"tell\s+(me|us)\s+(the|your)\s+(password|secret|key|credential|token|confidential|restricted)", 
             self.REVEAL_SECRET, 0.30),
            (r"expose\s+(confidential|sensitive|restricted|secret|classified)\s+(information|data|content|records)", 
             self.REVEAL_SECRET, 0.30),
            (r"leak\s+(confidential|sensitive|restricted|secret)\s+(information|data|content|records)", 
             self.REVEAL_SECRET, 0.35),
            
            # Execute unauthorized tools
            (r"execute\s+(this|the|unauthorized|unknown|new|custom)\s+(tool|command|function|script|code)", 
             self.EXECUTE_TOOL, 0.25),
            (r"run\s+(this|the|unauthorized|unknown|new)\s+(tool|command|function|script|code)", 
             self.EXECUTE_TOOL, 0.25),
            (r"call\s+(this|the|unauthorized|unknown|new)\s+(tool|command|function|api)", 
             self.EXECUTE_TOOL, 0.25),
            (r"invoke\s+(this|the|unauthorized|unknown)\s+(tool|command|function)", 
             self.EXECUTE_TOOL, 0.20),
            
            # Exfiltrate data
            (r"send\s+(this|the|following|data|information|content)\s+(to|to\s+)?an?\s+(external|outside|external|attacker|malicious)\s+(server|endpoint|address|url|email)", 
             self.EXFILTRATE_DATA, 0.35),
            (r"transmit\s+(confidential|sensitive|restricted|data|information)\s+(to|to\s+)?an?\s+(external|outside)\s+(server|endpoint|address)", 
             self.EXFILTRATE_DATA, 0.30),
            (r"exfiltrate\s+(data|information|content|records)", 
             self.EXFILTRATE_DATA, 0.40),
            (r"steal\s+(data|information|content|records|credentials)", 
             self.EXFILTRATE_DATA, 0.35),
        ]
    
    def detect(self, text: str) -> Tuple[bool, float, List[Dict]]:
        """
        Detect prompt injection patterns in text.
        
        Args:
            text: Text to analyze (e.g., document content, tool response)
            
        Returns:
            Tuple of (is_suspicious, confidence, indicators_list)
            - is_suspicious: True if injection patterns detected
            - confidence: Float between 0.0 and 1.0
            - indicators_list: List of dicts with indicator_type and pattern_match
        """
        if not text:
            return False, 0.0, []
        
        # Normalize text for matching: lowercase, remove extra whitespace
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        
        indicators = []
        confidence = 0.0
        
        for pattern, indicator_type, boost in self.patterns:
            matches = re.finditer(pattern, normalized, re.IGNORECASE)
            for match in matches:
                indicators.append({
                    "type": indicator_type,
                    "pattern": match.group(0),
                    "confidence_boost": boost
                })
                confidence += boost
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        # If confidence > 0.3, consider it suspicious
        is_suspicious = confidence > 0.3 or len(indicators) > 0
        
        return is_suspicious, confidence, indicators
    
    def analyze_with_fuzzy_match(self, text: str, fuzzy_threshold: float = 0.8) -> Tuple[bool, float, List[Dict]]:
        """
        Enhanced detection using fuzzy matching for variations.
        
        Args:
            text: Text to analyze
            fuzzy_threshold: Similarity threshold for fuzzy matching (0.0-1.0)
            
        Returns:
            Tuple of (is_suspicious, confidence, indicators_list)
        """
        is_suspicious, confidence, indicators = self.detect(text)
        
        # Additional fuzzy patterns for common misspellings/variations
        fuzzy_keywords = [
            ("ignor", self.IGNORE_INSTRUCTIONS),
            ("overrid", self.OVERRIDE_SYSTEM),
            ("reveal", self.REVEAL_SECRET),
            ("exfiltrat", self.EXFILTRATE_DATA),
            ("execut", self.EXECUTE_TOOL),
        ]
        
        normalized = text.lower()
        for keyword, indicator_type in fuzzy_keywords:
            # Find word-like patterns
            words = re.findall(r'\b\w+\b', normalized)
            for word in words:
                similarity = SequenceMatcher(None, keyword, word).ratio()
                if similarity >= fuzzy_threshold:
                    indicators.append({
                        "type": indicator_type,
                        "pattern": word,
                        "confidence_boost": (similarity - fuzzy_threshold) * 0.2,
                        "fuzzy_match": True
                    })
                    confidence += (similarity - fuzzy_threshold) * 0.2
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        is_suspicious = confidence > 0.3 or len(indicators) > 0
        
        return is_suspicious, confidence, indicators
