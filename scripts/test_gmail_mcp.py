#!/usr/bin/env python3
"""
Test Gmail MCP connection with the correct protocol
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spartacus_backend.services.mcp_gmail_client import GmailMCPClient

async def test_mcp_connection():
    """Test MCP connection using the corrected client"""
    print("🧪 Testing Gmail MCP Connection")
    print("=" * 50)
    
    client = GmailMCPClient()
    
    try:
        print("🚀 Starting MCP server...")
        await client.start_server()
        print("✅ MCP server started successfully")
        
        print("\n📧 Testing email search...")
        emails = await client.search_emails("in:inbox", max_results=1)
        print(f"✅ Search completed: Found {len(emails)} emails")
        
        if emails:
            print("\n📖 Testing email read...")
            email = await client.read_email(emails[0]["id"])
            print(f"✅ Read completed: Email subject: {email.get('subject', 'N/A')}")
        
        print("\n🏷️  Testing label list...")
        labels = await client.list_labels()
        print(f"✅ Labels completed: Found {len(labels)} labels")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🛑 Stopping MCP server...")
        await client.stop_server()
        print("✅ MCP server stopped")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection()) 