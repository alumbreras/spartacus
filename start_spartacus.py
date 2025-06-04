#!/usr/bin/env python3
"""
Spartacus Desktop Launcher
Launches both backend (FastAPI) and frontend (Electron + React) processes
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

class SpartacusLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.project_root = Path(__file__).parent
        
    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting Spartacus Backend (FastAPI)...")
        
        backend_dir = self.project_root / "spartacus_backend"
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ]
        
        # Set PYTHONPATH to include project root for proper imports
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)
        
        self.backend_process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            env=env,  # Add the environment with PYTHONPATH
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for backend to be ready
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        print("✅ Backend started at http://127.0.0.1:8000")
        
    def start_frontend(self):
        """Start the Electron + React frontend"""
        print("🎨 Starting Spartacus Frontend (Electron + React)...")
        
        frontend_dir = self.project_root / "spartacus_frontend"
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        self.frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("✅ Frontend starting...")
        
    def stop_processes(self):
        """Stop both backend and frontend processes"""
        print("\n🛑 Stopping Spartacus Desktop...")
        
        if self.frontend_process:
            print("   Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        if self.backend_process:
            print("   Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                
        print("✅ Spartacus Desktop stopped")
        
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        self.stop_processes()
        sys.exit(0)
        
    def run(self):
        """Run the complete Spartacus Desktop application"""
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("=" * 50)
        print("🏛️  SPARTACUS DESKTOP LAUNCHER")
        print("   Claude Desktop Alternative")
        print("=" * 50)
        
        try:
            # Start backend first
            self.start_backend()
            
            # Start frontend
            self.start_frontend()
            
            print("\n🎉 Spartacus Desktop is running!")
            print("   Backend:  http://127.0.0.1:8000")
            print("   Frontend: Opening Electron app...")
            print("   Docs:     http://127.0.0.1:8000/docs")
            print("\n💡 Press Ctrl+C to stop")
            
            # Keep the launcher running
            while True:
                # Check if processes are still alive
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process died")
                    break
                    
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend process died")
                    break
                    
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)
        except Exception as e:
            print(f"❌ Error: {e}")
            self.stop_processes()
            sys.exit(1)

if __name__ == "__main__":
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: No virtual environment detected")
        print("   Run: source .venv/bin/activate")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    launcher = SpartacusLauncher()
    launcher.run() 