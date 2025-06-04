"""
Agents API Router
Endpoints for agent management and execution
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid

from spartacus_backend.models.requests import AgentRunRequest, AgentCreateRequest
from spartacus_backend.models.responses import (
    AgentRunResponse, AgentListResponse, BaseResponse, 
    ResponseStatus, ErrorResponse
)
from spartacus_backend.services.agent_manager import SpartacusAgentManager
from spartacus_backend.dependencies import get_agent_manager

router = APIRouter()


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(
    request: AgentRunRequest,
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    Run an agent with user input
    
    Execute an agent of the specified type with the provided input and context.
    Returns the agent's response along with execution metadata.
    """
    try:
        # Generate execution ID if not provided
        execution_id = f"exec-{uuid.uuid4().hex[:8]}"
        
        # Run the agent
        result = await agent_manager.run_agent(
            user_input=request.user_input,
            agent_type=request.agent_type.value,
            context=request.context,
            session_id=request.session_id,
            max_iterations=request.max_iterations
        )
        
        return AgentRunResponse(
            status=ResponseStatus.SUCCESS,
            message="Agent execution completed successfully",
            agent_id=result["agent_id"],
            agent_type=result["agent_type"],
            response=result["response"],
            iterations=result["iterations"],
            execution_time=result["execution_time"],
            tools_used=result["tools_used"],
            context=result["context"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )


@router.post("/create", response_model=BaseResponse)
async def create_agent(
    request: AgentCreateRequest,
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    Create a custom agent
    
    Create a new agent instance with custom configuration, instructions, and tools.
    """
    try:
        agent_id = await agent_manager.create_agent(
            agent_type="custom",
            name=request.name,
            description=request.description,
            instructions=request.instructions,
            tools=request.tools,
            model=request.model,
            temperature=request.temperature
        )
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Agent created successfully with ID: {agent_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("/list", response_model=AgentListResponse)
async def list_agents(
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    List all available agents
    
    Returns a list of all registered agents with their configuration and status.
    """
    try:
        agents = await agent_manager.get_available_agents()
        
        return AgentListResponse(
            status=ResponseStatus.SUCCESS,
            message="Agents retrieved successfully",
            agents=agents,
            total_agents=len(agents)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve agents: {str(e)}"
        )


@router.get("/{agent_id}/status")
async def get_agent_status(
    agent_id: str,
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    Get status of a specific agent
    
    Returns detailed status information for the specified agent.
    """
    try:
        if agent_id not in agent_manager.agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent_instance = agent_manager.agents[agent_id]
        
        return {
            "status": ResponseStatus.SUCCESS,
            "agent_id": agent_id,
            "agent_type": agent_instance.type,
            "active": agent_instance.active,
            "created_at": agent_instance.created_at,
            "last_used": agent_instance.last_used,
            "context_size": len(agent_instance.context.messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent status: {str(e)}"
        )


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    Delete a specific agent
    
    Removes the specified agent instance and cleans up its resources.
    """
    try:
        if agent_id not in agent_manager.agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Mark agent as inactive and remove from manager
        agent_manager.agents[agent_id].active = False
        del agent_manager.agents[agent_id]
        
        # Remove from active sessions
        sessions_to_remove = [
            session_id for session_id, aid in agent_manager.active_sessions.items()
            if aid == agent_id
        ]
        for session_id in sessions_to_remove:
            del agent_manager.active_sessions[session_id]
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Agent {agent_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete agent: {str(e)}"
        ) 