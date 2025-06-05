#!/usr/bin/env python3
"""
Complete Gmail OAuth authentication process
"""
import subprocess
import time
import os
import json
from pathlib import Path
import webbrowser
import threading

def complete_gmail_authentication():
    """Complete Gmail OAuth authentication"""
    print("📧 GMAIL AUTHENTICATION COMPLETION")
    print("=" * 50)
    
    # Set up paths
    project_root = Path(__file__).parent.parent
    gmail_mcp_path = project_root / "mcp_servers" / "gmail"
    gmail_config_path = Path.home() / ".gmail-mcp"
    
    print(f"📁 Gmail MCP path: {gmail_mcp_path}")
    print(f"⚙️  Gmail config path: {gmail_config_path}")
    
    # Check if already authenticated
    token_file = gmail_config_path / "gcp-oauth.keys.json"
    if token_file.exists():
        try:
            with open(token_file) as f:
                token_data = json.load(f)
                if "access_token" in token_data:
                    print("✅ Gmail already authenticated!")
                    return True
        except:
            pass
    
    print("🔑 Starting OAuth authentication...")
    
    # Change to Gmail MCP directory
    os.chdir(gmail_mcp_path)
    
    def run_auth_process():
        """Run authentication in separate thread"""
        try:
            # Start authentication process
            process = subprocess.Popen(
                ["npm", "run", "auth"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Read output and look for URL
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output and "Please visit this URL" in output:
                    print(f"🌐 Auth URL found in output")
                    continue
                if output and "https://accounts.google.com" in output:
                    auth_url = output.strip()
                    print(f"🔗 Opening browser: {auth_url}")
                    webbrowser.open(auth_url)
                    break
            
            # Wait for process to complete
            stdout, stderr = process.communicate(timeout=60)
            
            if process.returncode == 0:
                print("✅ Authentication completed successfully!")
                return True
            else:
                print(f"❌ Authentication failed: {stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Authentication timed out")
            process.kill()
            return False
        except Exception as e:
            print(f"❌ Error during authentication: {e}")
            return False
    
    # Run authentication
    auth_thread = threading.Thread(target=run_auth_process)
    auth_thread.start()
    auth_thread.join(timeout=120)  # 2 minute timeout
    
    # Verify authentication
    print("🔍 Verifying authentication...")
    time.sleep(2)
    
    if token_file.exists():
        try:
            with open(token_file) as f:
                token_data = json.load(f)
                if "access_token" in token_data:
                    print("✅ Gmail authentication successful!")
                    print(f"📄 Token saved to: {token_file}")
                    return True
                else:
                    print("⚠️  Token file exists but no access_token found")
                    return False
        except Exception as e:
            print(f"❌ Error reading token: {e}")
            return False
    else:
        print("❌ Token file not created")
        return False

def manual_auth_instructions():
    """Provide manual authentication instructions"""
    print("\n📋 MANUAL AUTHENTICATION INSTRUCTIONS:")
    print("=" * 50)
    print("1. Open your browser")
    print("2. Visit: https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.modify&response_type=code&client_id=1060582880462-qliftp0qg34jl2apf56ime1u3g939gol.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Foauth2callback")
    print("3. Accept permissions")
    print("4. You should be redirected to Spartacus")
    print("5. Run this script again to verify")

if __name__ == "__main__":
    success = complete_gmail_authentication()
    
    if not success:
        manual_auth_instructions()
        print("\n💡 After completing manual auth, run this script again")
    else:
        print("\n🎉 Gmail integration is ready!")
        print("   You can now use Gmail tools in Spartacus") 