"""
Google Calendar tool for scheduling and event management
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from .base import BaseTool, ToolResult, ToolExecutionContext


class CalendarTool(BaseTool):
    """
    Google Calendar integration for scheduling and event management.
    
    Capabilities:
    - Create calendar events/meetings
    - Check availability
    - List upcoming events
    - Update/cancel events
    - Set reminders
    """
    
    def __init__(self):
        super().__init__(
            name="create_calendar_event",
            description="Create a calendar event or meeting. Use when user wants to schedule a meeting, book an appointment, set a calendar event, or plan something at a specific time.",
            requires_confirmation=True,
            requires_auth=True
        )
        
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.calendar_service = None
    
    async def _execute_impl(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """Execute calendar operation"""
        operation = parameters.get("operation", "create_event")
        
        if operation == "create_event":
            return await self._create_event(parameters, context)
        elif operation == "list_events":
            return await self._list_events(parameters, context)
        elif operation == "check_availability":
            return await self._check_availability(parameters, context)
        elif operation == "cancel_event":
            return await self._cancel_event(parameters, context)
        else:
            return ToolResult(
                success=False,
                error=f"Unknown operation: {operation}",
                message="Invalid calendar operation"
            )
    
    async def _create_event(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """Create a calendar event"""
        try:
            # For now, return a simulated success response
            # In production, this would integrate with Google Calendar API
            
            title = parameters.get("title", "Meeting")
            description = parameters.get("description", "")
            start_time = parameters.get("start_time")  # ISO format datetime
            duration = parameters.get("duration_minutes", 60)
            attendees = parameters.get("attendees", [])
            location = parameters.get("location", "")
            
            # Validate required parameters
            if not start_time:
                return ToolResult(
                    success=False,
                    error="start_time is required",
                    message="Please specify when the event should start"
                )
            
            # Parse start time
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = start_dt + timedelta(minutes=duration)
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"Invalid start_time format: {str(e)}",
                    message="Please provide start_time in ISO format (YYYY-MM-DDTHH:MM:SS)"
                )
            
            # Simulate calendar event creation
            # TODO: Integrate with actual Google Calendar API
            event_data = {
                "id": f"event_{int(datetime.utcnow().timestamp())}",
                "title": title,
                "description": description,
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
                "duration_minutes": duration,
                "attendees": attendees,
                "location": location,
                "created_at": datetime.utcnow().isoformat(),
                "status": "confirmed"
            }
            
            # Format attendees message
            attendees_msg = f" with {', '.join(attendees)}" if attendees else ""
            location_msg = f" at {location}" if location else ""
            
            return ToolResult(
                success=True,
                data=event_data,
                message=f"✅ Calendar event created: '{title}' on {start_dt.strftime('%B %d at %I:%M %p')}{attendees_msg}{location_msg}",
                metadata={
                    "operation": "create_event",
                    "attendees_count": len(attendees) if attendees else 0
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to create calendar event: {str(e)}"
            )
    
    async def _list_events(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """List upcoming calendar events"""
        try:
            days_ahead = parameters.get("days_ahead", 7)
            max_results = parameters.get("max_results", 10)
            
            # Simulate event listing
            # TODO: Integrate with actual Google Calendar API
            now = datetime.utcnow()
            events = [
                {
                    "id": f"event_{i}",
                    "title": f"Sample Event {i}",
                    "start_time": (now + timedelta(days=i)).isoformat(),
                    "end_time": (now + timedelta(days=i, hours=1)).isoformat()
                }
                for i in range(1, min(days_ahead, max_results) + 1)
            ]
            
            return ToolResult(
                success=True,
                data={"events": events, "count": len(events)},
                message=f"Found {len(events)} upcoming events in the next {days_ahead} days",
                metadata={"operation": "list_events"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to list events: {str(e)}"
            )
    
    async def _check_availability(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """Check if a time slot is available"""
        try:
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            
            if not start_time or not end_time:
                return ToolResult(
                    success=False,
                    error="Both start_time and end_time are required",
                    message="Please specify the time range to check"
                )
            
            # Simulate availability check
            # TODO: Integrate with actual Google Calendar API
            is_available = True  # Simulate as available
            
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            return ToolResult(
                success=True,
                data={
                    "available": is_available,
                    "start_time": start_time,
                    "end_time": end_time
                },
                message=f"✅ Time slot is available from {start_dt.strftime('%I:%M %p')} to {end_dt.strftime('%I:%M %p')}",
                metadata={"operation": "check_availability"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to check availability: {str(e)}"
            )
    
    async def _cancel_event(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """Cancel a calendar event"""
        try:
            event_id = parameters.get("event_id")
            
            if not event_id:
                return ToolResult(
                    success=False,
                    error="event_id is required",
                    message="Please specify which event to cancel"
                )
            
            # Simulate event cancellation
            # TODO: Integrate with actual Google Calendar API
            
            return ToolResult(
                success=True,
                data={"event_id": event_id, "status": "cancelled"},
                message=f"✅ Event cancelled successfully",
                metadata={"operation": "cancel_event"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to cancel event: {str(e)}"
            )
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """Get parameter schema for Calendar tool"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["create_event", "list_events", "check_availability", "cancel_event"],
                    "description": "The calendar operation to perform"
                },
                "title": {
                    "type": "string",
                    "description": "Event title/name (for create_event)"
                },
                "description": {
                    "type": "string",
                    "description": "Event description (for create_event)"
                },
                "start_time": {
                    "type": "string",
                    "description": "Event start time in ISO format (YYYY-MM-DDTHH:MM:SS)"
                },
                "end_time": {
                    "type": "string",
                    "description": "Event end time in ISO format (for check_availability)"
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "Event duration in minutes (for create_event)",
                    "default": 60
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attendee email addresses (for create_event)"
                },
                "location": {
                    "type": "string",
                    "description": "Event location (for create_event)"
                },
                "event_id": {
                    "type": "string",
                    "description": "Event ID (for cancel_event)"
                },
                "days_ahead": {
                    "type": "integer",
                    "description": "Number of days to look ahead (for list_events)",
                    "default": 7
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of events to return (for list_events)",
                    "default": 10
                }
            },
            "required": ["operation"]
        }
    
    def get_confirmation_prompt(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> str:
        """Generate confirmation prompt for calendar operations"""
        operation = parameters.get("operation")
        
        if operation == "create_event":
            title = parameters.get("title", "Untitled Event")
            start_time = parameters.get("start_time", "")
            attendees = parameters.get("attendees", [])
            
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                time_str = start_dt.strftime('%B %d at %I:%M %p')
            except:
                time_str = start_time
            
            attendees_msg = f"\nAttendees: {', '.join(attendees)}" if attendees else ""
            
            return f"""📅 Create Calendar Event

Title: {title}
When: {time_str}
Duration: {parameters.get('duration_minutes', 60)} minutes{attendees_msg}

Do you want to create this event?"""
        
        elif operation == "cancel_event":
            return f"⚠️ Are you sure you want to cancel this event? This action cannot be undone."
        
        return f"Do you want to perform calendar operation: {operation}?"


# Create global instance
calendar_tool = CalendarTool()
