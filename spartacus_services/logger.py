"""
Structured logger for Spartacus agents.
Recreated from app.services.utils.structured_logger
"""

import logging
import json
from typing import Any, Dict, Optional
from datetime import datetime

class StructuredLogger:
    """
    Structured logger that outputs JSON-formatted logs.
    
    This replaces app.services.utils.structured_logger for standalone operation.
    """
    
    def __init__(self, name: str = "spartacus", level: int = logging.INFO):
        """
        Initialize the structured logger.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(level)
        
        # Create formatter for structured output
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with optional structured data."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with optional structured data."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with optional structured data."""
        self._log(logging.ERROR, message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with optional structured data."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal method to log structured messages."""
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": logging.getLevelName(level),
            "message": message,
            "component": "spartacus"
        }
        
        # Add any additional structured data
        if kwargs:
            log_entry["data"] = kwargs
        
        # Log the structured entry
        self.logger.log(level, json.dumps(log_entry, indent=None))

class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured logging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record. If the message is already JSON, return as-is.
        Otherwise, create a structured format.
        """
        try:
            # Try to parse as JSON (already structured)
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            # Not JSON, create structured format
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "component": "spartacus",
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_entry, indent=None)

# Create default logger instance
logger = StructuredLogger()

def get_logger(name: str = "spartacus") -> StructuredLogger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name) 