"""
FastAPI Dependencies
Provides shared dependencies for the API endpoints
"""

from fastapi import HTTPException
from spartacus_backend.services.agent_manager import SpartacusAgentManager

# Global agent manager instance will be set by main.py
agent_manager: SpartacusAgentManager = None


def set_agent_manager(manager: SpartacusAgentManager):
    """Set the global agent manager instance"""
    global agent_manager
    agent_manager = manager


def get_agent_manager() -> SpartacusAgentManager:
    """Get the global agent manager instance"""
    if agent_manager is None:
        raise HTTPException(status_code=500, detail="Agent manager not initialized")
    return agent_manager 