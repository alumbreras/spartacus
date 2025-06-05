#!/usr/bin/env python3
"""
Simple OAuth callback server for Gmail authentication
"""
import json
import time
import requests
import subprocess
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class OAuthHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback and token exchange"""
    
    def do_GET(self):
        """Handle GET request for OAuth callback"""
        if '/oauth2callback' in self.path:
            try:
                # Parse the authorization code
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                
                if 'code' in params:
                    auth_code = params['code'][0]
                    print(f"✅ Authorization code received: {auth_code[:20]}...")
                    
                    # Exchange code for token
                    success = self.exchange_code_for_token(auth_code)
                    
                    if success:
                        response = """
                        <html><body style="font-family: Arial; text-align: center; margin-top: 100px;">
                        <h1 style="color: green;">🎉 Gmail Authentication Complete!</h1>
                        <p>Token saved successfully. You can close this window.</p>
                        <p><a href="http://localhost:3000">Return to Spartacus</a></p>
                        </body></html>
                        """
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(response.encode())
                        
                        # Signal to shut down server
                        threading.Thread(target=self.shutdown_server).start()
                    else:
                        self.send_error_response("Failed to exchange token")
                        
                elif 'error' in params:
                    error = params['error'][0]
                    print(f"❌ OAuth error: {error}")
                    self.send_error_response(f"OAuth error: {error}")
                else:
                    self.send_error_response("No authorization code received")
                    
            except Exception as e:
                print(f"❌ Error processing callback: {e}")
                self.send_error_response(str(e))
        else:
            self.send_error_response("Invalid callback path")
    
    def exchange_code_for_token(self, auth_code):
        """Exchange authorization code for access token"""
        try:
            # Load client credentials
            config_path = Path.home() / ".gmail-mcp" / "gcp-oauth.keys.json"
            with open(config_path) as f:
                creds = json.load(f)
            
            client_creds = creds['installed']
            
            # Token exchange request
            token_data = {
                'client_id': client_creds['client_id'],
                'client_secret': client_creds['client_secret'],
                'code': auth_code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://localhost:3000/oauth2callback'
            }
            
            print("🔄 Exchanging code for token...")
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data=token_data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_info = response.json()
                
                # Save complete token info
                creds.update(token_info)
                
                with open(config_path, 'w') as f:
                    json.dump(creds, f, indent=2)
                
                print("✅ Token saved successfully!")
                print(f"📄 Access token: {token_info.get('access_token', '')[:20]}...")
                print(f"🔄 Refresh token: {token_info.get('refresh_token', '')[:20]}...")
                
                return True
            else:
                print(f"❌ Token exchange failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Token exchange error: {e}")
            return False
    
    def send_error_response(self, error_msg):
        """Send error response"""
        response = f"""
        <html><body style="font-family: Arial; text-align: center; margin-top: 100px;">
        <h1 style="color: red;">❌ Authentication Failed</h1>
        <p>{error_msg}</p>
        <p><a href="javascript:history.back()">Go Back</a></p>
        </body></html>
        """
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def shutdown_server(self):
        """Shutdown server after successful authentication"""
        time.sleep(2)
        print("🛑 Shutting down OAuth server...")
        self.server.shutdown()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def start_oauth_server():
    """Start OAuth callback server"""
    print("🚀 Starting OAuth callback server on port 3000...")
    
    server = HTTPServer(('localhost', 3000), OAuthHandler)
    
    # Store server reference for shutdown
    OAuthHandler.server = server
    
    print("⏳ Waiting for OAuth callback...")
    print("🔗 Open this URL in your browser:")
    print("https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.modify&response_type=code&client_id=1060582880462-qliftp0qg34jl2apf56ime1u3g939gol.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Foauth2callback")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    finally:
        server.server_close()
        print("✅ OAuth server shutdown complete")

if __name__ == "__main__":
    start_oauth_server() 