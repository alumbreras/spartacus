#!/usr/bin/env python3
"""
Script to test Gmail integration and authentication
"""
import sys
import os
import json
from pathlib import Path

def test_gmail_integration():
    """Test Gmail MCP server and authentication"""
    print("📧 GMAIL INTEGRATION TEST")
    print("=" * 50)
    
    # Check Gmail MCP server
    print("🔍 GMAIL MCP SERVER CHECK:")
    mcp_gmail_path = Path.cwd() / "mcp_servers" / "gmail"
    
    if mcp_gmail_path.exists():
        print(f"  ✅ Gmail MCP directory exists: {mcp_gmail_path}")
        
        # Check package.json
        package_json = mcp_gmail_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    pkg_data = json.load(f)
                print(f"  ✅ Package: {pkg_data.get('name', 'unknown')} v{pkg_data.get('version', 'unknown')}")
            except Exception as e:
                print(f"  ⚠️  Could not read package.json: {e}")
        
        # Check if built
        dist_path = mcp_gmail_path / "dist"
        if dist_path.exists():
            print(f"  ✅ Built TypeScript files exist")
        else:
            print(f"  ❌ TypeScript not built - run 'npm run build'")
    else:
        print(f"  ❌ Gmail MCP directory not found")
    
    print()
    
    # Check Gmail credentials
    print("🔑 GMAIL CREDENTIALS CHECK:")
    gmail_config_dir = Path.home() / ".gmail-mcp"
    
    if gmail_config_dir.exists():
        print(f"  ✅ Gmail config directory exists: {gmail_config_dir}")
        
        credentials_file = gmail_config_dir / "gcp-oauth.keys.json"
        if credentials_file.exists():
            print(f"  ✅ Credentials file exists")
            
            try:
                with open(credentials_file) as f:
                    creds = json.load(f)
                
                if "installed" in creds:
                    print(f"  ✅ OAuth client configuration found")
                    client_id = creds["installed"].get("client_id", "")
                    if client_id:
                        print(f"  ✅ Client ID: {client_id[:20]}...")
                    else:
                        print(f"  ❌ No client ID found")
                else:
                    print(f"  ❌ Invalid credentials format")
                    
            except Exception as e:
                print(f"  ❌ Could not read credentials: {e}")
        else:
            print(f"  ❌ Credentials file not found")
            
        # Check for access token
        token_file = gmail_config_dir / "token.json"
        if token_file.exists():
            print(f"  ✅ Access token file exists")
            try:
                with open(token_file) as f:
                    token_data = json.load(f)
                if "access_token" in token_data:
                    print(f"  ✅ Access token available")
                else:
                    print(f"  ❌ No access token in file")
            except Exception as e:
                print(f"  ⚠️  Could not read token file: {e}")
        else:
            print(f"  ❌ No access token file found")
    else:
        print(f"  ❌ Gmail config directory not found")
    
    print()
    
    # Test Gmail tools import
    print("🛠️  GMAIL TOOLS CHECK:")
    try:
        current_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(current_dir))
        
        from agentic_lib.gmail_tools import gmail_send_tool, gmail_search_tool, gmail_read_tool
        print(f"  ✅ Gmail tools imported successfully")
        print(f"  ✅ Available tools: gmail_send, gmail_search, gmail_read")
        
        # Test tool creation
        tools = [gmail_send_tool, gmail_search_tool, gmail_read_tool]
        for tool in tools:
            print(f"  ✅ Tool {tool.name} created successfully")
            
    except ImportError as e:
        print(f"  ❌ Could not import Gmail tools: {e}")
    except Exception as e:
        print(f"  ❌ Error testing Gmail tools: {e}")
    
    print()
    print("🔧 GMAIL TEST COMPLETE")

def test_gmail_mcp_server():
    """Test Gmail MCP server directly"""
    print("\n🚀 TESTING GMAIL MCP SERVER DIRECTLY:")
    
    mcp_path = Path.cwd() / "mcp_servers" / "gmail"
    if not mcp_path.exists():
        print("  ❌ Gmail MCP server not found")
        return
    
    print(f"  📁 Testing in: {mcp_path}")
    
    # Test if we can run the auth command
    try:
        import subprocess
        result = subprocess.run(
            ["npm", "run", "auth", "--help"], 
            cwd=mcp_path, 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("  ✅ Gmail MCP auth command available")
        else:
            print(f"  ⚠️  Gmail MCP auth command issue: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("  ⚠️  Gmail MCP auth command timed out")
    except Exception as e:
        print(f"  ❌ Could not test Gmail MCP: {e}")

if __name__ == "__main__":
    test_gmail_integration()
    test_gmail_mcp_server() 