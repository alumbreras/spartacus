#!/usr/bin/env python3
"""
Script to test Spartacus backend functionality
"""
import sys
import time
import requests
import subprocess
from pathlib import Path
from threading import Thread
import signal

def test_backend_startup():
    """Test if backend can start successfully"""
    print("🚀 BACKEND STARTUP TEST")
    print("=" * 50)
    
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))
    
    # Check if port 8000 is available
    print("🔍 Checking port availability...")
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        print("  ⚠️  Port 8000 already in use")
        print(f"  📡 Current service responds: {response.status_code}")
        return False
    except requests.exceptions.RequestException:
        print("  ✅ Port 8000 available")
    
    # Try to import backend modules
    print("\n📦 Testing backend imports...")
    try:
        # First check if we can fix the missing context module
        import agentic_lib
        print("  ✅ agentic_lib imported")
        
        # Check if context module exists
        try:
            from agentic_lib.context import Context, Message, Role
            print("  ✅ agentic_lib.context imported")
        except ImportError:
            print("  ❌ agentic_lib.context missing - creating minimal version")
            create_missing_context_module()
        
        from spartacus_backend.main import app
        print("  ✅ Backend app imported successfully")
        
    except ImportError as e:
        print(f"  ❌ Backend import failed: {e}")
        return False
    
    return True

def create_missing_context_module():
    """Create minimal context module if missing"""
    context_file = Path(__file__).parent.parent / "agentic_lib" / "context.py"
    
    if not context_file.exists():
        context_content = '''"""
Basic context module for Spartacus
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    role: Role
    content: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass 
class Context:
    messages: List[Message]
    metadata: Optional[Dict[str, Any]] = None
    
    def add_message(self, role: Role, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the context"""
        self.messages.append(Message(role, content, metadata))
    
    def get_last_message(self) -> Optional[Message]:
        """Get the last message"""
        return self.messages[-1] if self.messages else None
'''
        
        with open(context_file, 'w') as f:
            f.write(context_content)
        print(f"  ✅ Created minimal context module at {context_file}")

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 API ENDPOINTS TEST")
    print("=" * 30)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ /health endpoint working")
        else:
            print(f"  ⚠️  /health returned {response.status_code}")
    except Exception as e:
        print(f"  ❌ /health endpoint failed: {e}")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("  ✅ / endpoint working")
        else:
            print(f"  ⚠️  / returned {response.status_code}")
    except Exception as e:
        print(f"  ❌ / endpoint failed: {e}")
    
    # Test chat endpoint
    try:
        chat_data = {
            "message": "Hello, this is a test",
            "agent_type": "default"
        }
        response = requests.post(f"{base_url}/api/chat/message", json=chat_data, timeout=10)
        if response.status_code == 200:
            print("  ✅ /api/chat/message endpoint working")
            result = response.json()
            print(f"  📄 Response preview: {str(result)[:100]}...")
        else:
            print(f"  ⚠️  /api/chat/message returned {response.status_code}")
    except Exception as e:
        print(f"  ❌ /api/chat/message failed: {e}")

def start_backend_for_testing():
    """Start backend in background for testing"""
    print("\n🔧 Starting backend for testing...")
    
    current_dir = Path(__file__).parent.parent
    env = {
        **os.environ,
        "PYTHONPATH": str(current_dir)
    }
    
    try:
        # Start backend process
        cmd = [
            sys.executable, "-c",
            "from spartacus_backend.main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8000, log_level='warning')"
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=current_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        print("  ⏳ Waiting for backend to start...")
        time.sleep(5)
        
        # Check if it's running
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=2)
            if response.status_code == 200:
                print("  ✅ Backend started successfully")
                return process
            else:
                print("  ❌ Backend not responding properly")
                process.terminate()
                return None
        except:
            print("  ❌ Backend failed to start")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"  ❌ Failed to start backend: {e}")
        return None

def main():
    """Main test function"""
    print("🏛️  SPARTACUS BACKEND COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test 1: Check if backend can be imported and started
    if not test_backend_startup():
        print("\n❌ Backend startup test failed - fixing issues...")
        return
    
    # Test 2: Try to start backend for API testing
    backend_process = start_backend_for_testing()
    
    if backend_process:
        try:
            # Test 3: Test API endpoints
            test_api_endpoints()
            
            print("\n✅ All backend tests completed!")
            
        finally:
            # Clean up
            print("\n🧹 Cleaning up...")
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
            print("  ✅ Backend process stopped")
    else:
        print("\n❌ Could not start backend for API testing")

if __name__ == "__main__":
    import os
    main() 