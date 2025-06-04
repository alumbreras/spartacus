#!/usr/bin/env python3
"""
Spartacus Desktop Startup Script
Starts both backend and frontend for development
"""

import sys
import os
import subprocess
import time
import signal
import threading
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from spartacus_services.logger import get_logger

logger = get_logger(__name__)

class SpartacusLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.shutdown = False
        
    def start_backend(self):
        """Start the FastAPI backend"""
        logger.info("🚀 Starting Spartacus Backend...")
        
        backend_script = parent_dir / "spartacus_backend" / "start_backend.py"
        
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, str(backend_script), "--reload"],
                cwd=str(parent_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor backend output in a separate thread
            threading.Thread(
                target=self._monitor_process,
                args=(self.backend_process, "Backend"),
                daemon=True
            ).start()
            
            logger.info("✅ Backend started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Electron frontend"""
        logger.info("🎨 Starting Spartacus Frontend...")
        
        frontend_dir = parent_dir / "spartacus_frontend"
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            logger.info("📦 Installing frontend dependencies...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=str(frontend_dir),
                    check=True,
                    capture_output=True
                )
                logger.info("✅ Dependencies installed")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install dependencies: {e}")
                return False
        
        try:
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor frontend output in a separate thread
            threading.Thread(
                target=self._monitor_process,
                args=(self.frontend_process, "Frontend"),
                daemon=True
            ).start()
            
            logger.info("✅ Frontend started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            return False
    
    def _monitor_process(self, process, name):
        """Monitor process output"""
        while not self.shutdown and process.poll() is None:
            try:
                # Read stdout
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        logger.info(f"[{name}] {line.strip()}")
                
                # Read stderr
                if process.stderr:
                    line = process.stderr.readline()
                    if line:
                        logger.warning(f"[{name}] {line.strip()}")
                        
            except Exception as e:
                logger.error(f"Error monitoring {name}: {e}")
                break
    
    def wait_for_backend(self, timeout=30):
        """Wait for backend to be ready"""
        import requests
        
        logger.info("⏳ Waiting for backend to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=2)
                if response.status_code == 200:
                    logger.info("✅ Backend is ready!")
                    return True
            except:
                pass
            
            time.sleep(1)
        
        logger.warning("⚠️ Backend not ready within timeout")
        return False
    
    def cleanup(self):
        """Cleanup processes"""
        logger.info("🛑 Shutting down Spartacus...")
        self.shutdown = True
        
        if self.frontend_process:
            logger.info("Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        if self.backend_process:
            logger.info("Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        logger.info("✅ Cleanup completed")
    
    def run(self):
        """Main run method"""
        try:
            # Start backend first
            if not self.start_backend():
                return False
            
            # Wait for backend to be ready
            if not self.wait_for_backend():
                logger.warning("Backend may not be fully ready, but continuing...")
            
            # Start frontend
            if not self.start_frontend():
                self.cleanup()
                return False
            
            # Keep running until interrupted
            logger.info("🎉 Spartacus Desktop is running!")
            logger.info("📍 Backend: http://127.0.0.1:8000")
            logger.info("📍 Frontend: Will open in Electron window")
            logger.info("💡 Press Ctrl+C to stop")
            
            # Wait for processes
            while not self.shutdown:
                if self.backend_process and self.backend_process.poll() is not None:
                    logger.error("❌ Backend process died!")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    logger.error("❌ Frontend process died!")
                    break
                
                time.sleep(1)
            
            return True
            
        except KeyboardInterrupt:
            logger.info("👋 Received interrupt signal")
            return True
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
        finally:
            self.cleanup()


def main():
    """Main function"""
    print("🏛️ Spartacus Desktop Launcher")
    print("="*50)
    
    launcher = SpartacusLauncher()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        launcher.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the launcher
    success = launcher.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 