#!/usr/bin/env python3
"""
Setup and test script for Gmail MCP integration in Spartacus Desktop
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any

def check_credentials() -> bool:
    """Check if Gmail OAuth credentials are properly configured"""
    
    print("📧 Gmail MCP Setup - Checking credentials...")
    print("=" * 60)
    
    # Check credentials file in project root
    root_creds = Path("credentials_gmail.json")
    if not root_creds.exists():
        print("❌ credentials_gmail.json not found in project root")
        return False
    
    # Check credentials in Gmail MCP expected location
    mcp_creds = Path.home() / ".gmail-mcp" / "gcp-oauth.keys.json"
    if not mcp_creds.exists():
        print("❌ gcp-oauth.keys.json not found in ~/.gmail-mcp/")
        print("   Run: mkdir -p ~/.gmail-mcp && cp credentials_gmail.json ~/.gmail-mcp/gcp-oauth.keys.json")
        return False
    
    # Validate credentials format
    try:
        with open(mcp_creds, 'r') as f:
            creds = json.load(f)
        
        if 'installed' not in creds:
            print("❌ Invalid credentials format - 'installed' key not found")
            return False
        
        required_fields = ['client_id', 'project_id', 'client_secret']
        for field in required_fields:
            if field not in creds['installed']:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ Gmail OAuth credentials found and valid")
        print(f"   Project ID: {creds['installed']['project_id']}")
        print(f"   Client ID: {creds['installed']['client_id'][:20]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False

def check_gmail_mcp_server() -> bool:
    """Check if Gmail MCP server is properly installed"""
    
    print("\n🔧 Checking Gmail MCP Server installation...")
    
    mcp_path = Path("mcp_servers/gmail")
    if not mcp_path.exists():
        print("❌ Gmail MCP server not found")
        print("   Run: git clone https://github.com/GongRzhe/Gmail-MCP-Server.git mcp_servers/gmail")
        return False
    
    # Check if npm dependencies are installed
    node_modules = mcp_path / "node_modules"
    if not node_modules.exists():
        print("❌ Node.js dependencies not installed")
        print("   Run: cd mcp_servers/gmail && npm install")
        return False
    
    # Check if TypeScript build exists
    index_js = mcp_path / "dist" / "index.js"
    if not index_js.exists():
        print("❌ TypeScript build not found")
        print("   Run: cd mcp_servers/gmail && npm run build")
        return False
    
    print("✅ Gmail MCP server properly installed")
    return True

async def test_gmail_mcp_connection() -> bool:
    """Test connection to Gmail MCP server"""
    
    print("\n🌐 Testing Gmail MCP server connection...")
    
    try:
        # Start the Gmail MCP server in test mode
        mcp_path = Path("mcp_servers/gmail")
        process = await asyncio.create_subprocess_exec(
            "node", "dist/index.js",
            cwd=mcp_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Give it a moment to start
        await asyncio.sleep(2)
        
        # Check if process is still running
        if process.returncode is not None:
            stdout, stderr = await process.communicate()
            print(f"❌ Gmail MCP server failed to start")
            print(f"   Error: {stderr.decode()}")
            return False
        
        # Terminate the test process
        process.terminate()
        await process.wait()
        
        print("✅ Gmail MCP server can be started successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Gmail MCP server: {e}")
        return False

def create_spartacus_gmail_integration() -> bool:
    """Create basic Gmail integration files for Spartacus"""
    
    print("\n⚙️  Creating Spartacus Gmail integration files...")
    
    # Create MCP client for Spartacus
    mcp_client_code = '''"""
Gmail MCP Client for Spartacus Desktop
"""

import asyncio
import json
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

class GmailMCPClient:
    """Client to communicate with Gmail MCP server"""
    
    def __init__(self, mcp_server_path: str = "mcp_servers/gmail"):
        self.mcp_server_path = Path(mcp_server_path)
        self.process = None
    
    async def start_server(self):
        """Start the Gmail MCP server"""
        if self.process is not None:
            return
        
        try:
            self.process = await asyncio.create_subprocess_exec(
                "node", "dist/index.js",
                cwd=self.mcp_server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Give server time to initialize
            await asyncio.sleep(1)
            
        except Exception as e:
            raise Exception(f"Failed to start Gmail MCP server: {e}")
    
    async def stop_server(self):
        """Stop the Gmail MCP server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
    
    async def send_email(self, to: List[str], subject: str, body: str, 
                        html_body: str = None, cc: List[str] = None) -> Dict[str, Any]:
        """Send an email via Gmail"""
        
        email_data = {
            "to": to,
            "subject": subject,
            "body": body
        }
        
        if html_body:
            email_data["htmlBody"] = html_body
            email_data["mimeType"] = "multipart/alternative"
        
        if cc:
            email_data["cc"] = cc
        
        return await self._call_mcp_tool("send_email", email_data)
    
    async def search_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search emails using Gmail syntax"""
        
        search_data = {
            "query": query,
            "maxResults": max_results
        }
        
        return await self._call_mcp_tool("search_emails", search_data)
    
    async def read_email(self, message_id: str) -> Dict[str, Any]:
        """Read a specific email by ID"""
        
        return await self._call_mcp_tool("read_email", {"messageId": message_id})
    
    async def list_labels(self) -> List[Dict[str, Any]]:
        """List all Gmail labels"""
        
        return await self._call_mcp_tool("list_email_labels", {})
    
    async def modify_email(self, message_id: str, add_labels: List[str] = None, 
                          remove_labels: List[str] = None) -> Dict[str, Any]:
        """Modify email labels"""
        
        modify_data = {"messageId": message_id}
        
        if add_labels:
            modify_data["addLabelIds"] = add_labels
        
        if remove_labels:
            modify_data["removeLabelIds"] = remove_labels
        
        return await self._call_mcp_tool("modify_email", modify_data)
    
    async def _call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call a tool on the Gmail MCP server"""
        
        if not self.process:
            await self.start_server()
        
        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        # Send request to MCP server
        request_json = json.dumps(request) + "\\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())
        
        if "error" in response:
            raise Exception(f"MCP Error: {response['error']}")
        
        return response.get("result", {})

# Example usage
async def test_gmail_client():
    """Test the Gmail MCP client"""
    
    client = GmailMCPClient()
    
    try:
        # Test listing labels
        labels = await client.list_labels()
        print(f"Found {len(labels)} Gmail labels")
        
        # Test search
        emails = await client.search_emails("is:unread", max_results=5)
        print(f"Found {len(emails)} unread emails")
        
        return True
        
    except Exception as e:
        print(f"Error testing Gmail client: {e}")
        return False
        
    finally:
        await client.stop_server()

if __name__ == "__main__":
    asyncio.run(test_gmail_client())
'''
    
    # Create the client file
    client_path = Path("spartacus_backend/services/mcp_gmail_client.py")
    client_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(client_path, 'w') as f:
        f.write(mcp_client_code)
    
    print("✅ Created spartacus_backend/services/mcp_gmail_client.py")
    
    # Create basic Gmail tools
    gmail_tools_code = '''"""
Gmail tools for Spartacus agents
"""

from typing import Dict, Any, List
from agentic_lib.tools import Tool
from spartacus_backend.services.mcp_gmail_client import GmailMCPClient

class GmailSendTool(Tool):
    """Tool for sending emails via Gmail"""
    
    def __init__(self):
        super().__init__(
            name="gmail_send",
            description="Send an email via Gmail",
            required_params=["to", "subject", "body"],
            optional_params=["html_body", "cc"]
        )
        self.gmail_client = GmailMCPClient()
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute email sending"""
        
        try:
            to_list = kwargs["to"]
            if isinstance(to_list, str):
                to_list = [to_list]
            
            result = await self.gmail_client.send_email(
                to=to_list,
                subject=kwargs["subject"],
                body=kwargs["body"],
                html_body=kwargs.get("html_body"),
                cc=kwargs.get("cc", [])
            )
            
            return {
                "status": "success",
                "result": "Email sent successfully",
                "details": result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
        
        finally:
            await self.gmail_client.stop_server()
    
    def get_openai_tool(self) -> Dict[str, Any]:
        """Get OpenAI tool format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of recipient email addresses"
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line"
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body content (plain text)"
                        },
                        "html_body": {
                            "type": "string",
                            "description": "Email body content (HTML format, optional)"
                        },
                        "cc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of CC email addresses (optional)"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        }

class GmailSearchTool(Tool):
    """Tool for searching emails in Gmail"""
    
    def __init__(self):
        super().__init__(
            name="gmail_search",
            description="Search emails in Gmail using Gmail search syntax",
            required_params=["query"],
            optional_params=["max_results"]
        )
        self.gmail_client = GmailMCPClient()
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute email search"""
        
        try:
            query = kwargs["query"]
            max_results = kwargs.get("max_results", 10)
            
            emails = await self.gmail_client.search_emails(query, max_results)
            
            return {
                "status": "success",
                "result": f"Found {len(emails)} emails",
                "emails": emails[:5],  # Limit to first 5 for display
                "total_count": len(emails)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
        
        finally:
            await self.gmail_client.stop_server()
    
    def get_openai_tool(self) -> Dict[str, Any]:
        """Get OpenAI tool format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Gmail search query (e.g., 'from:john@example.com after:2024/01/01')"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 10)"
                        }
                    },
                    "required": ["query"]
                }
            }
        }

class GmailReadTool(Tool):
    """Tool for reading specific emails"""
    
    def __init__(self):
        super().__init__(
            name="gmail_read",
            description="Read a specific email by its ID",
            required_params=["message_id"]
        )
        self.gmail_client = GmailMCPClient()
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute email reading"""
        
        try:
            message_id = kwargs["message_id"]
            
            email = await self.gmail_client.read_email(message_id)
            
            return {
                "status": "success",
                "result": "Email retrieved successfully",
                "email": email
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
        
        finally:
            await self.gmail_client.stop_server()
    
    def get_openai_tool(self) -> Dict[str, Any]:
        """Get OpenAI tool format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message_id": {
                            "type": "string",
                            "description": "Gmail message ID to read"
                        }
                    },
                    "required": ["message_id"]
                }
            }
        }
'''
    
    # Create the tools file
    tools_path = Path("agentic_lib/gmail_tools.py")
    tools_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(tools_path, 'w') as f:
        f.write(gmail_tools_code)
    
    print("✅ Created agentic_lib/gmail_tools.py")
    
    return True

async def main():
    """Main setup and test function"""
    
    print("🚀 Spartacus Gmail MCP Integration Setup")
    print("=" * 60)
    
    # Step 1: Check credentials
    if not check_credentials():
        print("\\n❌ Setup failed - credentials not configured properly")
        return False
    
    # Step 2: Check MCP server
    if not check_gmail_mcp_server():
        print("\\n❌ Setup failed - Gmail MCP server not installed properly")
        return False
    
    # Step 3: Test connection
    if not await test_gmail_mcp_connection():
        print("\\n❌ Setup failed - Gmail MCP server connection test failed")
        return False
    
    # Step 4: Create integration files
    if not create_spartacus_gmail_integration():
        print("\\n❌ Setup failed - could not create integration files")
        return False
    
    print("\\n🎉 Gmail MCP integration setup completed successfully!")
    print("\\n📝 Next steps:")
    print("   1. Add Gmail tools to your agent configurations")
    print("   2. Test sending an email: 'Send an email to test@example.com about testing Gmail integration'")
    print("   3. Test searching emails: 'Show me unread emails from today'")
    print("   4. Test reading emails: 'Read the latest email from John'")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 