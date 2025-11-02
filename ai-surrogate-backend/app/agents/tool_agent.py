"""
Tool-enabled agent that uses tools to perform actions
Multi-agent communication system
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.tools.base import BaseTool, ToolExecutionContext, ToolResult
from app.tools.registry import tool_registry
from app.tools.gmail_tool import gmail_tool
from app.tools.calendar_tool import calendar_tool
from app.services.ai_service import ai_service


class CommunicationAgent:
    """
    Communication Agent - Handles email, messaging, and notifications.
    Uses Gmail and other communication tools.
    
    This agent can:
    - Send emails
    - Read emails
    - Draft messages
    - Notify users
    """
    
    def __init__(self):
        self.agent_type = "communication"
        self.display_name = "Communication Agent"
        self.icon = "📧"
        
        # Register tools
        tool_registry.register(gmail_tool, category="communication")
    
    async def process(
        self, 
        message: str,
        context: Optional[str] = None,
        memory: Optional[str] = None,
        user_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process communication-related requests.
        Decides whether to use tools or just provide guidance.
        """
        try:
            start_time = datetime.utcnow()
            
            # Analyze if this requires tool usage
            tool_decision = await self._should_use_tool(message)
            
            if tool_decision["use_tool"]:
                # Extract parameters from message using AI
                tool_params = await self._extract_tool_parameters(
                    message, 
                    tool_decision["tool_name"]
                )
                
                # Execute tool
                tool_context = ToolExecutionContext(
                    user_id=user_id or "unknown",
                    thread_id=thread_id or "unknown",
                    message=message,
                    user_email=user_email
                )
                
                tool_result = await tool_registry.execute_tool(
                    tool_decision["tool_name"],
                    tool_params,
                    tool_context
                )
                
                # Generate response based on tool result
                if tool_result.requires_confirmation:
                    response_text = f"{tool_result.confirmation_prompt}\n\nPlease confirm to proceed."
                elif tool_result.success:
                    response_text = tool_result.message
                else:
                    response_text = f"I encountered an issue: {tool_result.message}\n\nLet me know if you'd like to try again."
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                return {
                    "content": response_text,
                    "confidence": 0.9 if tool_result.success else 0.6,
                    "processing_time": processing_time,
                    "tool_used": tool_decision["tool_name"],
                    "tool_result": tool_result.to_dict(),
                    "requires_confirmation": tool_result.requires_confirmation
                }
            else:
                # Provide guidance without using tools
                guidance_prompt = f"""You are a communication assistant. The user said: "{message}"

Provide helpful guidance about communication (email, messaging, etc.) without actually performing the action.

Be conversational and helpful. If they want to send an email or message, ask for details like:
- Who should I send it to?
- What should the subject be?
- What message would you like to send?

User message: {message}

Response:"""
                
                response = await ai_service.generate_chat_response(
                    message=guidance_prompt,
                    context=context,
                    memory=memory
                )
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                return {
                    "content": response,
                    "confidence": 0.8,
                    "processing_time": processing_time,
                    "tool_used": None
                }
            
        except Exception as e:
            print(f"Error in CommunicationAgent: {e}")
            return {
                "content": f"I'm here to help with communication! You mentioned: '{message}'. I can help you send emails, check messages, or communicate with others. What would you like to do?",
                "confidence": 0.5,
                "processing_time": 0.1,
                "error": str(e)
            }
    
    async def _should_use_tool(self, message: str) -> Dict[str, Any]:
        """Determine if message requires tool usage"""
        message_lower = message.lower()
        
        # Email-related keywords
        compose_email_keywords = ["send email", "email", "send message to", "write email", "compose email", "draft email"]
        read_email_keywords = ["check email", "read email", "inbox", "check messages", "any emails"]
        
        if any(keyword in message_lower for keyword in compose_email_keywords):
            # Check if we have enough information to create draft
            has_recipient = "@" in message or any(name in message_lower for name in ["talha", "ahmad", "saad"])
            
            if has_recipient or "send" in message_lower or "email" in message_lower:
                return {"use_tool": True, "tool_name": "gmail_tool", "reason": "User wants to compose email draft"}
        
        if any(keyword in message_lower for keyword in read_email_keywords):
            return {"use_tool": True, "tool_name": "gmail_tool", "reason": "User wants to read emails"}
        
        return {"use_tool": False, "tool_name": None, "reason": "No tool needed"}
    
    async def _extract_tool_parameters(self, message: str, tool_name: str) -> Dict[str, Any]:
        """Extract tool parameters from user message using AI"""
        message_lower = message.lower()
        
        if tool_name == "gmail_tool":
            # Extract email parameters
            params = {
                "operation": "create_draft"  # Default to creating drafts for safety
            }
            
            # Extract recipient - look for common patterns
            if "@" in message:
                # Extract email address
                words = message.split()
                for word in words:
                    if "@" in word:
                        params["to"] = word.strip(".,!? ")
                        break
            else:
                # Try to extract name and construct email
                # For demo, use placeholder
                for name in ["talha", "ahmad", "saad"]:
                    if name in message_lower:
                        params["to"] = f"{name}@example.com"
                        break
            
            # Extract subject and body
            if "about" in message_lower:
                # Try to extract subject
                about_idx = message_lower.find("about")
                remaining = message[about_idx+5:].strip()
                params["subject"] = remaining[:50] if len(remaining) > 0 else "Message from AI Surrogate"
                params["body"] = remaining if len(remaining) > 0 else message
            else:
                params["subject"] = "Message from AI Surrogate"
                params["body"] = message
            
            return params
        
        elif tool_name == "read_email":
            return {
                "operation": "read",
                "limit": 10
            }
        
        return {}
    
    def get_available_tools(self) -> List[BaseTool]:
        """Get list of tools this agent can use"""
        return tool_registry.get_tools_for_agent(self.agent_type)


class SchedulerAgentEnhanced:
    """
    Enhanced Scheduler Agent with Calendar tool integration.
    
    This agent can:
    - Create calendar events
    - Schedule meetings
    - Check availability
    - Set reminders
    - Communicate with Communication Agent to send invites
    """
    
    def __init__(self):
        self.agent_type = "scheduler"
        self.display_name = "Scheduler Agent"
        self.icon = "📅"
        
        # Register tools
        tool_registry.register(calendar_tool, category="scheduling")
    
    async def process(
        self, 
        message: str,
        context: Optional[str] = None,
        memory: Optional[str] = None,
        user_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process scheduling requests with tool support"""
        try:
            start_time = datetime.utcnow()
            
            # Check if we should use calendar tool
            tool_decision = await self._should_use_tool(message)
            
            if tool_decision["use_tool"]:
                # Extract parameters
                tool_params = await self._extract_calendar_parameters(message)
                
                # Execute calendar tool
                tool_context = ToolExecutionContext(
                    user_id=user_id or "unknown",
                    thread_id=thread_id or "unknown",
                    message=message,
                    user_email=user_email
                )
                
                tool_result = await tool_registry.execute_tool(
                    "create_calendar_event",
                    tool_params,
                    tool_context
                )
                
                # Generate response
                if tool_result.requires_confirmation:
                    response_text = f"{tool_result.confirmation_prompt}\n\nShall I proceed?"
                elif tool_result.success:
                    response_text = tool_result.message
                    
                    # If event was created with attendees, suggest sending email
                    if tool_params.get("attendees"):
                        response_text += "\n\nWould you like me to send email invitations to the attendees?"
                else:
                    response_text = f"I had trouble scheduling that: {tool_result.message}"
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                return {
                    "content": response_text,
                    "confidence": 0.9 if tool_result.success else 0.6,
                    "processing_time": processing_time,
                    "tool_used": "create_calendar_event",
                    "tool_result": tool_result.to_dict(),
                    "requires_confirmation": tool_result.requires_confirmation
                }
            else:
                # Provide scheduling guidance
                scheduling_prompt = f"""You are a scheduling assistant. The user said: "{message}"

Help them with scheduling, time management, or calendar-related tasks. Be specific and actionable.

If they want to schedule something, ask for:
- What event/meeting
- When (date and time)
- Who should attend
- Duration

User message: {message}

Response:"""
                
                response = await ai_service.generate_chat_response(
                    message=scheduling_prompt,
                    context=context,
                    memory=memory
                )
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                return {
                    "content": response,
                    "confidence": 0.8,
                    "processing_time": processing_time,
                    "tool_used": None
                }
            
        except Exception as e:
            print(f"Error in SchedulerAgentEnhanced: {e}")
            return {
                "content": f"I can help you with scheduling! You mentioned: '{message}'. What would you like to schedule?",
                "confidence": 0.5,
                "processing_time": 0.1,
                "error": str(e)
            }
    
    async def _should_use_tool(self, message: str) -> Dict[str, Any]:
        """Determine if scheduling requires calendar tool"""
        message_lower = message.lower()
        
        schedule_keywords = ["schedule", "book meeting", "create event", "add to calendar", "meeting with", "appointment"]
        
        if any(keyword in message_lower for keyword in schedule_keywords):
            # Check if we have time information
            has_time = any(word in message_lower for word in ["tomorrow", "today", "pm", "am", "7pm", "morning", "afternoon"])
            
            if has_time:
                return {"use_tool": True, "tool_name": "create_calendar_event", "reason": "User wants to schedule with specific time"}
        
        return {"use_tool": False, "tool_name": None, "reason": "Need more details"}
    
    async def _extract_calendar_parameters(self, message: str) -> Dict[str, Any]:
        """Extract calendar event parameters from message"""
        from datetime import datetime, timedelta
        
        params = {
            "operation": "create_event",
            "duration_minutes": 60
        }
        
        message_lower = message.lower()
        
        # Extract title/description
        if "meeting with" in message_lower:
            idx = message_lower.find("meeting with")
            remaining = message[idx+12:].strip()
            name = remaining.split()[0] if remaining else "someone"
            params["title"] = f"Meeting with {name.capitalize()}"
            params["attendees"] = [f"{name}@example.com"]
        elif "book" in message_lower:
            params["title"] = "Scheduled Event"
        
        # Extract time
        now = datetime.utcnow()
        if "tomorrow" in message_lower:
            # Extract time if specified
            if "7pm" in message_lower or "7 pm" in message_lower:
                event_time = (now + timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0)
            else:
                event_time = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
            params["start_time"] = event_time.isoformat()
        elif "today" in message_lower:
            if "7pm" in message_lower or "7 pm" in message_lower:
                event_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
            else:
                event_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            params["start_time"] = event_time.isoformat()
        
        return params


# Global instances
communication_agent = CommunicationAgent()
scheduler_agent_enhanced = SchedulerAgentEnhanced()
