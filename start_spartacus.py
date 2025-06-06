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
import threading
import queue
import socket
from pathlib import Path

class SpartacusLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.project_root = Path(__file__).parent
        self.running = True
        self.backend_logs_queue = queue.Queue()
        self.log_thread = None
        
    def check_port_available(self, port):
        """Check if a port is available"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('127.0.0.1', port))
            sock.close()
            return True
        except OSError:
            sock.close()
            return False
    
    def kill_processes_on_port(self, port):
        """Kill processes using a specific port"""
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                pids = []
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) > 1:
                            pids.append(parts[1])
                
                if pids:
                    print(f"🔄 Killing processes on port {port}: {', '.join(pids)}")
                    for pid in pids:
                        try:
                            subprocess.run(['kill', '-9', pid], check=False)
                        except:
                            pass
                    time.sleep(1)  # Wait a moment for processes to die
                    return True
            return False
        except Exception as e:
            print(f"⚠️  Could not check/kill processes on port {port}: {e}")
            return False
        
    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting Spartacus Backend (FastAPI)...")
        
        # Check if port 8000 is available
        if not self.check_port_available(8000):
            print("⚠️  Port 8000 is in use, attempting to free it...")
            if self.kill_processes_on_port(8000):
                print("✅ Port 8000 is now available")
            else:
                print("❌ Could not free port 8000")
                return False
        
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
            env=env,
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
        
        # Start log monitoring thread
        self.log_thread = threading.Thread(target=self._monitor_backend_logs, daemon=True)
        self.log_thread.start()
        return True
    
    def _monitor_backend_logs(self):
        """Monitor backend logs in a separate thread"""
        if not self.backend_process or not self.backend_process.stdout:
            return
            
        try:
            for line in iter(self.backend_process.stdout.readline, ''):
                if line and self.running:
                    self.backend_logs_queue.put(line.strip())
                if not self.running:
                    break
        except:
            pass
    
    def _process_backend_logs(self):
        """Process queued backend logs"""
        try:
            while not self.backend_logs_queue.empty():
                log_line = self.backend_logs_queue.get_nowait()
                if log_line:
                    # Only show important logs, filter out noise
                    if any(keyword in log_line.lower() for keyword in ['error', 'exception', 'traceback', 'failed', 'critical']):
                        print(f"🔴 Backend: {log_line}")
                    elif 'info' in log_line.lower() and ('started' in log_line.lower() or 'listening' in log_line.lower()):
                        print(f"🟢 Backend: {log_line}")
        except queue.Empty:
            pass
        
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
        
    def restart_frontend(self):
        """Restart the frontend process"""
        if self.frontend_process and self.frontend_process.poll() is None:
            print("🔄 Stopping current frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        self.start_frontend()
        
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
        self.running = False
        self.stop_processes()
        sys.exit(0)
        
    def show_status(self):
        """Show current status of processes"""
        backend_status = "🟢 Running" if self.backend_process and self.backend_process.poll() is None else "🔴 Stopped"
        frontend_status = "🟢 Running" if self.frontend_process and self.frontend_process.poll() is None else "🔴 Stopped"
        
        print(f"\n📊 Status:")
        print(f"   Backend:  {backend_status}")
        print(f"   Frontend: {frontend_status}")
        print(f"   API:      http://127.0.0.1:8000")
        print(f"   Docs:     http://127.0.0.1:8000/docs")
        
    def show_help(self):
        """Show available commands"""
        print("\n💡 Available commands:")
        print("   r  - Restart frontend")
        print("   s  - Show status")
        print("   h  - Show this help")
        print("   q  - Quit (Ctrl+C also works)")
        
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
            if not self.start_backend():
                print("❌ Failed to start backend")
                return
            
            # Start frontend
            self.start_frontend()
            
            print("\n🎉 Spartacus Desktop is running!")
            print("   Backend:  http://127.0.0.1:8000")
            print("   Frontend: Opening Electron app...")
            print("   Docs:     http://127.0.0.1:8000/docs")
            print("\n💡 Commands: 'r' (restart frontend), 's' (status), 'h' (help), 'q' (quit)")
            print("💡 Press Ctrl+C to stop everything")
            
            # Main monitoring loop
            while self.running:
                # Process backend logs
                self._process_backend_logs()
                
                # Check if backend died (this is actually an error)
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process died - this is a critical error")
                    
                    # Capture and show remaining backend logs
                    self._process_backend_logs()
                    
                    # Show return code
                    return_code = self.backend_process.returncode
                    print(f"🔍 Backend exit code: {return_code}")
                    break
                
                # Check if frontend died (normal when user closes app)
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("ℹ️  Frontend closed (backend still running)")
                    self.frontend_process = None
                
                # Non-blocking input check for commands
                try:
                    # Use select on Unix systems for non-blocking input
                    import select
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        command = sys.stdin.readline().strip().lower()
                        
                        if command == 'r':
                            self.restart_frontend()
                        elif command == 's':
                            self.show_status()
                        elif command == 'h':
                            self.show_help()
                        elif command == 'q':
                            break
                        elif command:
                            print(f"Unknown command: {command}. Type 'h' for help.")
                            
                except ImportError:
                    # Fallback for systems without select
                    pass
                except KeyboardInterrupt:
                    break
                    
                time.sleep(0.5)
                
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