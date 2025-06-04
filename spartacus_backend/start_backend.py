#!/usr/bin/env python3
"""
Spartacus Backend Startup Script
"""

import sys
import os
import uvicorn
import argparse
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from spartacus_backend.config.settings import settings
from spartacus_services.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description="Start Spartacus Backend")
    parser.add_argument("--host", default=settings.host, help="Host to bind to")
    parser.add_argument("--port", type=int, default=settings.port, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", default=settings.reload, help="Enable auto-reload")
    parser.add_argument("--log-level", default=settings.log_level, help="Log level")
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting Spartacus Backend...")
    logger.info(f"📍 Host: {args.host}")
    logger.info(f"🔌 Port: {args.port}")
    logger.info(f"🔄 Reload: {args.reload}")
    logger.info(f"📊 Log Level: {args.log_level}")
    
    try:
        # Start the FastAPI server
        uvicorn.run(
            "spartacus_backend.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("👋 Shutting down Spartacus Backend...")
    except Exception as e:
        logger.error(f"❌ Failed to start backend: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 