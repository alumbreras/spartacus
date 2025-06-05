#!/usr/bin/env python3
"""
Debug Gmail MCP responses to understand the format
"""
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spartacus_backend.services.mcp_gmail_client import GmailMCPClient

async def debug_mcp_responses():
    """Debug MCP responses to understand the format"""
    print("🔍 Debugging Gmail MCP Response Format")
    print("=" * 50)
    
    client = GmailMCPClient()
    email_id = None
    
    try:
        print("🚀 Starting MCP server...")
        await client.start_server()
        print("✅ MCP server started successfully")
        
        print("\n📧 First, searching for an email to get an ID...")
        try:
            search_result = await client.call_tool("search_emails", {
                "query": "in:inbox",
                "maxResults": 1
            })
            
            if "content" in search_result and search_result["content"]:
                content_text = search_result["content"][0].get("text", "")
                # Use the existing parser to find the email ID
                emails = client._parse_email_search_text(content_text)
                if emails:
                    email_id = emails[0].get("id")
                    print(f"💌 Found email with ID: {email_id}")
                else:
                    print("Could not parse email ID from search result.")
            else:
                print("Search did not return any content.")

        except Exception as e:
            print(f"Error during email search: {e}")

        if email_id:
            print(f"\n📄 Now, reading email with ID: {email_id}")
            try:
                read_result = await client.call_tool("read_email", {"messageId": email_id})
                print("\n--- RAW MCP RESPONSE (read_email) ---")
                print(json.dumps(read_result, indent=2))
                print("------------------------------------")
                
                if "content" in read_result and read_result["content"]:
                    print("\n--- RAW TEXT FROM MCP ---")
                    text_content = read_result["content"][0].get("text", "N/A")
                    print(text_content)
                    print("-------------------------")

            except Exception as e:
                print(f"Error during email read: {e}")
        else:
            print("\nSkipping email read because no email ID was found.")
            
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🛑 Stopping MCP server...")
        await client.stop_server()
        print("✅ MCP server stopped")

if __name__ == "__main__":
    asyncio.run(debug_mcp_responses())