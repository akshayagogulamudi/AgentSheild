"""AI agent service for handling user requests and tool integration."""
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

from .mock_agent import MockAgent
from .tool_registry import TOOLS

# Load environment variables
load_dotenv()


class AgentService:
    """Service for calling AI agents and managing responses."""
    
    def __init__(self):
        """
        Initialize the agent service.
        
        Checks for GEMINI_API_KEY in environment. If missing or placeholder,
        initializes in mock mode. Otherwise initializes Gemini client.
        """
        self.mock_mode = True
        self.mock_agent = MockAgent()
        
        # Check for Gemini API key
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        
        if api_key and api_key != "your_key_here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel("gemini-1.5-flash")
                self.mock_mode = False
            except Exception as e:
                print(f"Warning: Could not initialize Gemini: {e}. Using mock mode.")
                self.mock_mode = True
        else:
            print("GEMINI_API_KEY not set or is placeholder. Using mock mode.")
            self.mock_mode = True
    
    def call_agent(
        self,
        user_message: str,
        agent_role: str = "employee",
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Call the AI agent to process a user message.
        
        Args:
            user_message: The user's request
            agent_role: Role/permission level of the agent (default: 'employee')
            conversation_history: Previous messages in conversation (optional)
            
        Returns:
            Dictionary with:
                - response_text: The agent's response
                - proposed_tools: List of proposed tool calls from agent
                  Each with: tool_name, arguments, user_request
        """
        if self.mock_mode:
            return self._call_mock_agent(user_message, agent_role)
        else:
            return self._call_gemini_agent(user_message, agent_role, conversation_history or [])
    
    def _call_mock_agent(
        self,
        user_message: str,
        agent_role: str
    ) -> Dict[str, Any]:
        """
        Call the mock agent and extract scenario from message.
        
        Args:
            user_message: The user's request
            agent_role: Role/permission level of the agent
            
        Returns:
            Dictionary with response_text and proposed_tools
        """
        # Detect scenario from user message keywords
        message_lower = user_message.lower()
        
        if "inject" in message_lower:
            scenario = "prompt_injection"
        elif "exfiltrat" in message_lower:
            scenario = "exfiltration"
        elif "delete" in message_lower:
            scenario = "unauthorized_tool"
        else:
            scenario = "normal"
        
        # Get mock response
        response = self.mock_agent.respond_with_scenario(scenario, user_message)
        
        return response
    
    def _call_gemini_agent(
        self,
        user_message: str,
        agent_role: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Call the real Gemini agent with function calling.
        
        Args:
            user_message: The user's request
            agent_role: Role/permission level of the agent
            conversation_history: Previous messages in conversation
            
        Returns:
            Dictionary with response_text and proposed_tools
        """
        try:
            # Prepare messages for Gemini
            messages = conversation_history.copy() if conversation_history else []
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Define tools for Gemini function calling
            tools = [
                {
                    "type": "function",
                    "function": {
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
                    }
                },
                {
                    "type": "function",
                    "function": {
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
                    }
                },
                {
                    "type": "function",
                    "function": {
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
                }
            ]
            
            # Call Gemini with function calling enabled
            response = self.client.generate_content(
                messages,
                tools=tools
            )
            
            # Extract response text
            response_text = response.text if response.text else "I processed your request."
            
            # Extract proposed tool calls
            proposed_tools = []
            if hasattr(response, "tool_calls"):
                for tool_call in response.tool_calls:
                    proposed_tools.append({
                        "tool_name": tool_call.name,
                        "arguments": tool_call.args,
                        "user_request": user_message
                    })
            
            return {
                "response_text": response_text,
                "proposed_tools": proposed_tools
            }
        
        except Exception as e:
            print(f"Error calling Gemini: {e}. Falling back to mock mode.")
            return self._call_mock_agent(user_message, agent_role)
