"""Intent validator that compares user request with agent action."""
from typing import Tuple


class IntentValidator:
    """Validates that agent actions align with user intent."""
    
    def __init__(self):
        """Initialize intent validator with keyword mappings."""
        # Map user intents to expected tools/resources
        self.intent_mappings = {
            # Summarize/read operations
            "summarize": ["read_file"],
            "read": ["read_file"],
            "view": ["read_file"],
            "retrieve": ["read_file", "search_records"],
            "get": ["read_file", "search_records"],
            
            # Search operations
            "search": ["search_records"],
            "find": ["search_records"],
            "look": ["search_records"],
            "query": ["search_records"],
            
            # Write/send operations
            "send": ["send_email"],
            "email": ["send_email"],
            "notify": ["send_email"],
            "alert": ["send_email"],
            
            # Delete operations (expect these to be blocked)
            "delete": ["delete_records"],
            "remove": ["delete_records"],
            "erase": ["delete_records"],
        }
    
    def compare_intent(
        self,
        user_request: str,
        agent_action: str,
        agent_tool: str
    ) -> Tuple[bool, float, str]:
        """
        Compare user intent with agent action.
        
        Args:
            user_request: Original user request (e.g., "Summarize the employee handbook")
            agent_action: Agent's proposed action (e.g., "Read financial_records_2024.txt")
            agent_tool: Tool name (e.g., "read_file")
            
        Returns:
            Tuple of (aligned, mismatch_confidence, explanation)
            - aligned: True if action aligns with intent
            - mismatch_confidence: Confidence that intent is mismatched (0.0-1.0)
            - explanation: Description of alignment or mismatch
        """
        if not user_request or not agent_tool:
            return True, 0.0, "Cannot validate without user request or agent tool"
        
        user_lower = user_request.lower()
        agent_lower = agent_action.lower() if agent_action else ""
        
        # Extract user intent keywords
        user_intent = self._extract_intent(user_lower)
        
        # Check if agent tool aligns with expected tools for that intent
        expected_tools = []
        for keyword, tools in self.intent_mappings.items():
            if keyword in user_lower:
                expected_tools.extend(tools)
        
        # If we found expected tools, check if agent tool matches
        if expected_tools:
            if agent_tool in expected_tools:
                # Tool matches - now check resource alignment
                resource_aligned = self._check_resource_alignment(user_lower, agent_lower)
                if resource_aligned:
                    return True, 0.0, f"Agent action aligns with user request intent"
                else:
                    # Tool is correct but resource seems wrong
                    return False, 0.6, f"Agent is using correct tool but accessing unexpected resource. User asked for '{user_intent}' but agent is targeting '{agent_lower}'"
            else:
                # Tool doesn't match expected
                return False, 0.8, f"Agent tool '{agent_tool}' does not match user intent. Expected one of {expected_tools}"
        
        # No specific intent keywords found - assume it could be aligned
        return True, 0.2, "User intent unclear, but tool seems reasonable"
    
    def _extract_intent(self, text: str) -> str:
        """
        Extract primary intent from text.
        
        Args:
            text: Lowercase user request
            
        Returns:
            Intent keyword or description
        """
        keywords = [
            "summarize", "read", "view", "retrieve", "search",
            "find", "send", "email", "delete", "remove"
        ]
        
        for keyword in keywords:
            if keyword in text:
                return keyword
        
        return "unknown"
    
    def _check_resource_alignment(self, user_request: str, agent_action: str) -> bool:
        """
        Check if the resource (file/record) aligns with user request.
        
        Args:
            user_request: User's request (lowercase)
            agent_action: Agent's proposed action (lowercase)
            
        Returns:
            True if resource seems aligned, False if misaligned
        """
        # Check for specific resource mentions in user request
        resource_keywords = {
            "handbook": ["handbook", "employee", "policy"],
            "financial": ["financial", "budget", "revenue", "earnings"],
            "employee": ["employee", "staff", "person", "user"],
            "customer": ["customer", "client", "user"],
        }
        
        # Find what resource user asked for
        user_resources = []
        for resource, keywords in resource_keywords.items():
            for keyword in keywords:
                if keyword in user_request:
                    user_resources.append(resource)
                    break
        
        # Check if agent is accessing matching resources
        for resource in user_resources:
            for keyword in resource_keywords[resource]:
                if keyword in agent_action:
                    return True
        
        # If no specific resources mentioned, assume alignment
        if not user_resources:
            return True
        
        # User mentioned specific resources but agent is accessing different ones
        return False
