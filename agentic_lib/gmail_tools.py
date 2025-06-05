"""
Gmail tools for Spartacus agents
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from agentic_lib.tools import Tool
from spartacus_backend.services.mcp_gmail_client import GmailMCPClient

class GmailSendInput(BaseModel):
    """Input parameters for sending emails"""
    to: List[str] = Field(description="List of recipient email addresses")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content (plain text)")
    html_body: str = Field(default="", description="Email body content (HTML format, optional)")
    cc: List[str] = Field(default=[], description="List of CC email addresses (optional)")

async def gmail_send_function(ctx, args: GmailSendInput) -> str:
    """Send an email via Gmail"""
    
    gmail_client = GmailMCPClient()
    
    try:
        result = await gmail_client.send_email(
            to=args.to,
            subject=args.subject,
            body=args.body,
            html_body=args.html_body if args.html_body else None,
            cc=args.cc if args.cc else None
        )
        
        return f"Email sent successfully to {', '.join(args.to)}"
        
    except Exception as e:
        return f"Error sending email: {str(e)}"
    
    finally:
        # await gmail_client.stop_server() # This was causing the server to stop after each call
        pass

class GmailSearchInput(BaseModel):
    """Input parameters for searching emails"""
    query: str = Field(description="Gmail search query (e.g., 'from:john@example.com after:2024/01/01')")
    max_results: int = Field(default=10, description="Maximum number of results to return")

async def gmail_search_function(ctx, args: GmailSearchInput) -> str:
    """Search emails in Gmail using Gmail search syntax"""
    
    gmail_client = GmailMCPClient()
    
    try:
        emails = await gmail_client.search_emails(args.query, args.max_results)
        
        if not emails:
            return f"No emails found for query: {args.query}"
        
        result = f"Found {len(emails)} emails for query: {args.query}\n\n"
        
        # Show first 3 emails
        for i, email in enumerate(emails[:3]):
            result += f"{i+1}. Subject: {email.get('subject', 'No subject')}\n"
            result += f"   From: {email.get('from', 'Unknown')}\n"
            result += f"   Date: {email.get('date', 'Unknown')}\n"
            result += f"   ID: {email.get('id', 'Unknown')}\n\n"
        
        if len(emails) > 3:
            result += f"... and {len(emails) - 3} more emails"
        
        return result
        
    except Exception as e:
        return f"Error searching emails: {str(e)}"
    
    finally:
        # await gmail_client.stop_server() # This was causing the server to stop after each call
        pass

class GmailReadInput(BaseModel):
    """Input parameters for reading emails"""
    message_id: str = Field(description="Gmail message ID to read")

async def gmail_read_function(ctx, args: GmailReadInput) -> str:
    """Read a specific email by its ID"""
    
    gmail_client = GmailMCPClient()
    
    try:
        email = await gmail_client.read_email(args.message_id)
        
        result = f"Email Details:\n"
        result += f"Subject: {email.get('subject', 'No subject')}\n"
        result += f"From: {email.get('from', 'Unknown')}\n"
        result += f"To: {email.get('to', 'Unknown')}\n"
        result += f"Date: {email.get('date', 'Unknown')}\n\n"
        result += f"Content:\n{email.get('body', 'No content')}"
        
        return result
        
    except Exception as e:
        return f"Error reading email: {str(e)}"
    
    finally:
        # await gmail_client.stop_server() # This was causing the server to stop after each call
        pass

# Create the tool instances
gmail_send_tool = Tool(
    name="gmail_send",
    function=gmail_send_function,
    args_schema=GmailSendInput,
    takes_ctx=True,
    description="Send an email via Gmail"
)

gmail_search_tool = Tool(
    name="gmail_search",
    function=gmail_search_function,
    args_schema=GmailSearchInput,
    takes_ctx=True,
    description="Search emails in Gmail using Gmail search syntax"
)

gmail_read_tool = Tool(
    name="gmail_read",
    function=gmail_read_function,
    args_schema=GmailReadInput,
    takes_ctx=True,
    description="Read a specific email by its ID"
)
