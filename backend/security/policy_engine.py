"""Policy enforcement engine for role-based access control."""
import json
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from database.models import Policy


class PolicyEngine:
    """Enforces role-based policies for tool and resource access."""
    
    def __init__(self, db: Session):
        """
        Initialize policy engine.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self._policy_cache: Dict[str, Dict] = {}
    
    def get_role_permissions(self, role: str) -> Optional[Dict]:
        """
        Get permissions for a role.
        
        Args:
            role: Role identifier (e.g., 'employee', 'manager')
            
        Returns:
            Dictionary of allowed_tools with their restrictions, or None if role not found
        """
        if role in self._policy_cache:
            return self._policy_cache[role]
        
        policy = self.db.query(Policy).filter(Policy.role == role).first()
        if not policy:
            return None
        
        permissions = json.loads(policy.allowed_tools)
        self._policy_cache[role] = permissions
        return permissions
    
    def can_execute_tool(self, tool: str, role: str) -> Tuple[bool, str]:
        """
        Check if a role can execute a specific tool.
        
        Args:
            tool: Tool name
            role: Role identifier
            
        Returns:
            Tuple of (can_execute, reason)
        """
        permissions = self.get_role_permissions(role)
        
        if permissions is None:
            return False, f"Unknown role: {role}"
        
        if tool not in permissions:
            return False, f"Tool '{tool}' not found in role '{role}' permissions"
        
        # Tool exists in permissions (default allow if listed)
        return True, f"Tool '{tool}' is permitted for role '{role}'"
    
    def can_access_resource(self, resource: str, resource_type: str, role: str) -> Tuple[bool, str]:
        """
        Check if a role can access a specific resource (file or record).
        
        Args:
            resource: Resource identifier (filename, record_id, etc.)
            resource_type: Type of resource ('file', 'record', etc.)
            role: Role identifier
            
        Returns:
            Tuple of (can_access, reason)
        """
        permissions = self.get_role_permissions(role)
        
        if permissions is None:
            return False, f"Unknown role: {role}"
        
        if resource_type == "file":
            file_perms = permissions.get("read_file", {})
            restricted_files = file_perms.get("restricted_files", [])
            
            if resource in restricted_files:
                return False, f"File '{resource}' is restricted for role '{role}'"
            
            return True, f"Role '{role}' can access file '{resource}'"
        
        elif resource_type == "record":
            return True, f"Role '{role}' can access record '{resource}'"
        
        return False, f"Unknown resource type: {resource_type}"
    
    def get_tool_permission_level(self, tool: str, role: str) -> Dict:
        """
        Get detailed permission configuration for a tool/role combination.
        
        Args:
            tool: Tool name
            role: Role identifier
            
        Returns:
            Dictionary with permission details (restrictions, max operations, etc.)
        """
        permissions = self.get_role_permissions(role)
        
        if permissions is None or tool not in permissions:
            return {}
        
        return permissions.get(tool, {})
    
    def is_approval_required(self, tool: str, role: str) -> bool:
        """
        Check if a tool requires approval for a given role.
        
        Args:
            tool: Tool name
            role: Role identifier
            
        Returns:
            True if approval is required, False otherwise
        """
        tool_config = self.get_tool_permission_level(tool, role)
        return tool_config.get("requires_approval", False)
    
    def get_allowed_recipients(self, role: str) -> List[str]:
        """
        Get allowed email recipients for a role.
        
        Args:
            role: Role identifier
            
        Returns:
            List of allowed recipient patterns (e.g., ['@company.com', '@partners.com'])
        """
        tool_config = self.get_tool_permission_level("send_email", role)
        return tool_config.get("allowed_recipients", [])
    
    def is_recipient_allowed(self, recipient: str, role: str) -> bool:
        """
        Check if an email recipient is allowed for a role.
        
        Args:
            recipient: Email address or domain
            role: Role identifier
            
        Returns:
            True if recipient is allowed, False otherwise
        """
        allowed = self.get_allowed_recipients(role)
        
        if "*" in allowed:
            return True
        
        for pattern in allowed:
            if pattern == "*" or recipient.endswith(pattern):
                return True
        
        return False
    
    def get_allowed_classifications(self, role: str) -> List[str]:
        """
        Get allowed document classifications for a role.
        
        Args:
            role: Role identifier
            
        Returns:
            List of allowed classifications (e.g., ['PUBLIC', 'INTERNAL'])
        """
        tool_config = self.get_tool_permission_level("read_file", role)
        return tool_config.get("allowed_classifications", [])
    
    def is_classification_allowed(self, classification: str, role: str) -> bool:
        """
        Check if a document classification is accessible for a role.
        
        Args:
            classification: Document classification
            role: Role identifier
            
        Returns:
            True if classification is allowed, False otherwise
        """
        allowed = self.get_allowed_classifications(role)
        return classification in allowed
