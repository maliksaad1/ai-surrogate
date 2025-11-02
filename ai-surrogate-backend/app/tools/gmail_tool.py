"""
Gmail tool for sending, reading, and managing emails
"""

from typing import Dict, Any, Optional, List
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

from .base import BaseTool, ToolResult, ToolExecutionContext


class GmailTool(BaseTool):
    """
    Gmail integration tool for email operations.
    
    Capabilities:
    - Send emails
    - Read emails
    - Search emails
    - Check inbox
    """
    
    def __init__(self):
        super().__init__(
            name="send_email",
            description="Send an email to someone. Use this when the user wants to email someone, send a message via email, or communicate through email.",
            requires_confirmation=True,  # Always confirm before sending emails
            requires_auth=True
        )
        
        # Gmail SMTP configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.imap_server = "imap.gmail.com"
        
        # Get credentials from environment (will be set via config)
        self.gmail_address = os.getenv("GMAIL_ADDRESS")
        self.gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
    
    async def _execute_impl(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """Execute Gmail operation"""
        operation = parameters.get("operation", "send")
        
        if operation == "send":
            return await self._send_email(parameters, context)
        elif operation == "read":
            return await self._read_emails(parameters, context)
        elif operation == "search":
            return await self._search_emails(parameters, context)
        else:
            return ToolResult(
                success=False,
                error=f"Unknown operation: {operation}",
                message="Invalid operation specified"
            )
    
    async def _send_email(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """Send an email via Gmail SMTP"""
        try:
            # Extract parameters
            to_email = parameters.get("to")
            subject = parameters.get("subject", "Message from AI Surrogate")
            body = parameters.get("body", "")
            cc = parameters.get("cc", [])
            bcc = parameters.get("bcc", [])
            
            # Validate email configuration
            if not self.gmail_address or not self.gmail_app_password:
                return ToolResult(
                    success=False,
                    error="Gmail credentials not configured",
                    message="Gmail integration not set up. Please configure GMAIL_ADDRESS and GMAIL_APP_PASSWORD in environment variables."
                )
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.gmail_address
            msg['To'] = to_email if isinstance(to_email, str) else ", ".join(to_email)
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ", ".join(cc) if isinstance(cc, list) else cc
            if bcc:
                msg['Bcc'] = ", ".join(bcc) if isinstance(bcc, list) else bcc
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.gmail_address, self.gmail_app_password)
                
                recipients = [to_email] if isinstance(to_email, str) else to_email
                if cc:
                    recipients.extend(cc if isinstance(cc, list) else [cc])
                if bcc:
                    recipients.extend(bcc if isinstance(bcc, list) else [bcc])
                
                server.send_message(msg)
            
            return ToolResult(
                success=True,
                data={
                    "to": to_email,
                    "subject": subject,
                    "sent_at": datetime.utcnow().isoformat()
                },
                message=f"✅ Email sent successfully to {to_email}",
                metadata={
                    "operation": "send",
                    "recipients_count": len(recipients)
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to send email: {str(e)}"
            )
    
    async def _read_emails(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """Read recent emails from inbox"""
        try:
            # Validate credentials
            if not self.gmail_address or not self.gmail_app_password:
                return ToolResult(
                    success=False,
                    error="Gmail credentials not configured",
                    message="Gmail not configured"
                )
            
            limit = parameters.get("limit", 10)
            
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.gmail_address, self.gmail_app_password)
            mail.select('inbox')
            
            # Search for emails
            _, message_numbers = mail.search(None, 'ALL')
            email_ids = message_numbers[0].split()
            
            # Get recent emails
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            emails = []
            
            for email_id in reversed(recent_ids):
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                emails.append({
                    "from": email_message['From'],
                    "subject": email_message['Subject'],
                    "date": email_message['Date'],
                    "snippet": self._get_email_body(email_message)[:200]
                })
            
            mail.close()
            mail.logout()
            
            return ToolResult(
                success=True,
                data={"emails": emails, "count": len(emails)},
                message=f"Retrieved {len(emails)} emails",
                metadata={"operation": "read"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to read emails: {str(e)}"
            )
    
    async def _search_emails(
        self, 
        parameters: Dict[str, Any],
        context: ToolExecutionContext
    ) -> ToolResult:
        """Search emails by criteria"""
        try:
            if not self.gmail_address or not self.gmail_app_password:
                return ToolResult(
                    success=False,
                    error="Gmail credentials not configured",
                    message="Gmail not configured"
                )
            
            query = parameters.get("query", "")
            limit = parameters.get("limit", 10)
            
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.gmail_address, self.gmail_app_password)
            mail.select('inbox')
            
            # Search with query
            search_criteria = f'(SUBJECT "{query}")' if query else 'ALL'
            _, message_numbers = mail.search(None, search_criteria)
            
            email_ids = message_numbers[0].split()
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            for email_id in reversed(recent_ids):
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                emails.append({
                    "from": email_message['From'],
                    "subject": email_message['Subject'],
                    "date": email_message['Date']
                })
            
            mail.close()
            mail.logout()
            
            return ToolResult(
                success=True,
                data={"emails": emails, "count": len(emails), "query": query},
                message=f"Found {len(emails)} emails matching '{query}'",
                metadata={"operation": "search"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to search emails: {str(e)}"
            )
    
    def _get_email_body(self, email_message) -> str:
        """Extract email body text"""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return email_message.get_payload(decode=True).decode()
        return ""
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """Get parameter schema for Gmail tool"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["send", "read", "search"],
                    "description": "The operation to perform"
                },
                "to": {
                    "type": "string",
                    "description": "Recipient email address (for send operation)"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject (for send operation)"
                },
                "body": {
                    "type": "string",
                    "description": "Email body content (for send operation)"
                },
                "query": {
                    "type": "string",
                    "description": "Search query (for search operation)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of emails to retrieve (for read/search operations)",
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
        """Generate confirmation prompt for email sending"""
        operation = parameters.get("operation")
        
        if operation == "send":
            to = parameters.get("to")
            subject = parameters.get("subject", "No subject")
            body_preview = parameters.get("body", "")[:100]
            
            return f"""📧 Send Email Confirmation

To: {to}
Subject: {subject}
Message: {body_preview}{'...' if len(parameters.get('body', '')) > 100 else ''}

Do you want to send this email?"""
        
        return f"Do you want to {operation} emails?"


# Create global instance
gmail_tool = GmailTool()
