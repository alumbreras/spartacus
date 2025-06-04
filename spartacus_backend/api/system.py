"""
System API Router
Endpoints for system management and monitoring
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from spartacus_backend.models.requests import ConfigUpdateRequest
from spartacus_backend.models.responses import SystemStatusResponse, BaseResponse, ResponseStatus
from spartacus_backend.services.agent_manager import SpartacusAgentManager
from spartacus_backend.config.settings import settings
from spartacus_backend.dependencies import get_agent_manager

router = APIRouter()


@router.get("/health")
async def health_check(
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    System health check
    
    Basic health check endpoint that returns system status.
    """
    try:
        return {
            "status": "healthy",
            "message": "Spartacus Backend is running",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    Get detailed system status
    
    Returns comprehensive system status including resource usage and agent metrics.
    """
    try:
        status_data = agent_manager.get_system_status()
        
        return SystemStatusResponse(
            status=ResponseStatus.SUCCESS,
            message="System status retrieved successfully",
            **status_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system status: {str(e)}"
        )


@router.get("/config")
async def get_configuration():
    """
    Get current system configuration
    
    Returns the current system configuration settings.
    """
    try:
        config_dict = {
            "host": settings.host,
            "port": settings.port,
            "cors_origins": settings.cors_origins,
            "max_agents": settings.max_agents,
            "agent_timeout": settings.agent_timeout,
            "max_chat_history": settings.max_chat_history,
            "enable_streaming": settings.enable_streaming,
            "default_model": settings.default_model,
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "data_dir": settings.data_dir,
            "logs_dir": settings.logs_dir
        }
        
        return {
            "status": ResponseStatus.SUCCESS,
            "message": "Configuration retrieved successfully",
            "configuration": config_dict
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get configuration: {str(e)}"
        )


@router.post("/config", response_model=BaseResponse)
async def update_configuration(request: ConfigUpdateRequest):
    """
    Update system configuration
    
    Update system configuration settings. Changes may require restart.
    """
    try:
        # Update settings (in a real implementation, this would persist changes)
        updated_settings = []
        
        for key, value in request.settings.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
                updated_settings.append(key)
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Configuration updated: {', '.join(updated_settings)}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update configuration: {str(e)}"
        )


@router.post("/restart", response_model=BaseResponse)
async def restart_system(
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    Restart system components
    
    Gracefully restart system components while maintaining state.
    """
    try:
        # In a real implementation, this would trigger a graceful restart
        await agent_manager.cleanup()
        await agent_manager.initialize()
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message="System restarted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restart system: {str(e)}"
        )


@router.get("/logs")
async def get_logs(
    lines: int = 100,
    level: str = "INFO"
):
    """
    Get system logs
    
    Retrieve recent system logs for debugging and monitoring.
    """
    try:
        # In a real implementation, this would read from log files
        logs = [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "level": "INFO",
                "message": "System started successfully",
                "component": "main"
            },
            {
                "timestamp": "2024-01-15T10:30:01Z",
                "level": "INFO", 
                "message": "Agent Manager initialized",
                "component": "agent_manager"
            }
        ]
        
        return {
            "status": ResponseStatus.SUCCESS,
            "message": f"Retrieved {len(logs)} log entries",
            "logs": logs[-lines:],  # Return last N lines
            "total_logs": len(logs)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get logs: {str(e)}"
        ) 