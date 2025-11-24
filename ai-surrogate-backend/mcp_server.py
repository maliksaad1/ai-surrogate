from mcp.server.fastmcp import FastMCP
from typing import List, Optional
import os
import sys
from datetime import datetime

# Add app directory to path to import existing tools
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.tools.gmail_tool import gmail_tool
from app.tools.calendar_tool import calendar_tool
from app.tools.base import ToolExecutionContext

# Initialize FastMCP server
mcp = FastMCP("Google Tools")

@mcp.tool()
async def send_email(to: str, subject: str, body: str) -> str:
    """Send an email using Gmail.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
    """
    context = ToolExecutionContext(
        user_id="mcp_user",
        thread_id="mcp_thread",
        message="MCP Tool Call"
    )
    
    # Reuse existing tool logic
    result = await gmail_tool._send_email({
        "to": to,
        "subject": subject,
        "body": body
    }, context)
    
    if result.success:
        return result.message
    else:
        return f"Error: {result.error}"

@mcp.tool()
async def read_emails(limit: int = 10) -> str:
    """Read recent emails from Gmail inbox.
    
    Args:
        limit: Number of emails to retrieve (default: 10)
    """
    context = ToolExecutionContext(
        user_id="mcp_user",
        thread_id="mcp_thread",
        message="MCP Tool Call"
    )
    
    result = await gmail_tool._read_emails({
        "limit": limit
    }, context)
    
    if result.success:
        emails = result.data.get("emails", [])
        formatted = "\n\n".join([
            f"From: {e['from']}\nSubject: {e['subject']}\nDate: {e['date']}\nSnippet: {e.get('snippet', '')}"
            for e in emails
        ])
        return f"Found {len(emails)} emails:\n\n{formatted}"
    else:
        return f"Error: {result.error}"

@mcp.tool()
async def create_calendar_event(title: str, start_time: str, duration_minutes: int = 60, attendees: List[str] = []) -> str:
    """Create a Google Calendar event.
    
    Args:
        title: Event title
        start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SS)
        duration_minutes: Duration in minutes
        attendees: List of attendee email addresses
    """
    context = ToolExecutionContext(
        user_id="mcp_user",
        thread_id="mcp_thread",
        message="MCP Tool Call"
    )
    
    result = await calendar_tool._create_event({
        "title": title,
        "start_time": start_time,
        "duration_minutes": duration_minutes,
        "attendees": attendees
    }, context)
    
    if result.success:
        return result.message
    else:
        return f"Error: {result.error}"

@mcp.tool()
async def list_calendar_events(days_ahead: int = 7) -> str:
    """List upcoming calendar events.
    
    Args:
        days_ahead: Number of days to look ahead
    """
    context = ToolExecutionContext(
        user_id="mcp_user",
        thread_id="mcp_thread",
        message="MCP Tool Call"
    )
    
    result = await calendar_tool._list_events({
        "days_ahead": days_ahead
    }, context)
    
    if result.success:
        events = result.data.get("events", [])
        formatted = "\n".join([
            f"- {e['title']} ({e['start_time']})"
            for e in events
        ])
        return f"Upcoming events:\n{formatted}"
    else:
        return f"Error: {result.error}"

if __name__ == "__main__":
    mcp.run()
