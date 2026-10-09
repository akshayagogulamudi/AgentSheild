"""Tool registry for AI agent integration."""
import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from database.models import SimulatedFile, SimulatedRecord, EmailOutbox


# Tool definitions in a format compatible with Gemini function declarations
TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file from the secure document store",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the file to read"
                }
            },
            "required": ["filename"]
        }
    },
    {
        "name": "search_records",
        "description": "Search employee/customer records by keyword",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query keyword"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "send_email",
        "description": "Send an email to a recipient",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Email recipient address"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line"
                },
                "body": {
                    "type": "string",
                    "description": "Email body content"
                }
            },
            "required": ["to", "subject", "body"]
        }
    }
]


class ToolRegistry:
    """Registry of available tools for AI agents."""
    
    def __init__(self):
        """Initialize tool registry."""
        pass
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get list of all available tools with their specifications.
        
        Returns:
            List of tool dictionaries with name, description, and parameters schema
        """
        return TOOLS
    
    def get_tool_names(self) -> List[str]:
        """
        Get list of all available tool names.
        
        Returns:
            List of tool name strings
        """
        return [tool["name"] for tool in TOOLS]
    
    def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Execute a tool with the given arguments.
        
        This method assumes the tool has already been validated by the security gateway.
        Only call this for ALLOW decisions.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments/parameters
            db: Database session
            
        Returns:
            Dictionary with execution result or error
        """
        if tool_name == "read_file":
            return self._execute_read_file(arguments, db)
        elif tool_name == "search_records":
            return self._execute_search_records(arguments, db)
        elif tool_name == "send_email":
            return self._execute_send_email(arguments, db)
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    def _execute_read_file(
        self,
        arguments: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Execute read_file tool.
        
        Args:
            arguments: Must contain 'filename' key
            db: Database session
            
        Returns:
            Dictionary with file content or error
        """
        filename = arguments.get("filename")
        
        if not filename:
            return {
                "success": False,
                "error": "Missing required argument: filename"
            }
        
        try:
            file = db.query(SimulatedFile).filter(
                SimulatedFile.filename == filename
            ).first()
            
            if not file:
                return {
                    "success": False,
                    "error": f"File not found: {filename}"
                }
            
            return {
                "success": True,
                "filename": filename,
                "content": file.content,
                "classification": file.classification.value
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file: {str(e)}"
            }
    
    def _execute_search_records(
        self,
        arguments: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Execute search_records tool.
        
        Searches SimulatedRecord entries by querying the JSON data field.
        Returns up to 10 matching records.
        
        Args:
            arguments: Must contain 'query' key
            db: Database session
            
        Returns:
            Dictionary with matching records or error
        """
        query = arguments.get("query", "").lower()
        
        if not query:
            return {
                "success": False,
                "error": "Missing required argument: query"
            }
        
        try:
            records = db.query(SimulatedRecord).all()
            
            matches = []
            for record in records:
                # Parse JSON data and search within it
                try:
                    record_data = json.loads(record.data)
                    record_str = json.dumps(record_data).lower()
                    
                    if query in record_str:
                        matches.append({
                            "id": record.id,
                            "record_type": record.record_type,
                            "data": record_data,
                            "classification": record.classification.value
                        })
                except json.JSONDecodeError:
                    continue
            
            # Limit results to 10
            matches = matches[:10]
            
            return {
                "success": True,
                "query": query,
                "results": matches,
                "count": len(matches)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching records: {str(e)}"
            }
    
    def _execute_send_email(
        self,
        arguments: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Execute send_email tool.
        
        Creates an entry in the EmailOutbox table.
        
        Args:
            arguments: Must contain 'to', 'subject', 'body' keys
            db: Database session
            
        Returns:
            Dictionary with confirmation or error
        """
        recipient = arguments.get("to")
        subject = arguments.get("subject")
        body = arguments.get("body")
        
        if not recipient or not subject or not body:
            return {
                "success": False,
                "error": "Missing required arguments: to, subject, body"
            }
        
        try:
            email = EmailOutbox(
                recipient=recipient,
                subject=subject,
                body=body,
                is_demo=False
            )
            db.add(email)
            db.commit()
            
            return {
                "success": True,
                "message": f"Email sent to {recipient}",
                "email_id": email.id,
                "recipient": recipient,
                "subject": subject
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error sending email: {str(e)}"
            }
