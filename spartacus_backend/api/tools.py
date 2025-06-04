"""
Tools API Router
Endpoints for tool management and execution
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from spartacus_backend.models.requests import ToolExecuteRequest
from spartacus_backend.models.responses import (
    ToolListResponse, ToolExecuteResponse, ResponseStatus, BaseResponse
)
from spartacus_backend.services.agent_manager import SpartacusAgentManager
from spartacus_backend.dependencies import get_agent_manager

router = APIRouter()


@router.get("/list", response_model=ToolListResponse)
async def list_tools(
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    List all available tools
    
    Returns a list of all registered tools with their descriptions and parameters.
    """
    try:
        tools = await agent_manager.get_available_tools()
        
        return ToolListResponse(
            status=ResponseStatus.SUCCESS,
            message="Tools retrieved successfully",
            tools=tools,
            total_tools=len(tools)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tools: {str(e)}"
        )


@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_tool(
    request: ToolExecuteRequest,
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    Execute a specific tool
    
    Execute the specified tool with the provided parameters and return the result.
    """
    try:
        result = await agent_manager.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters,
            context=request.context
        )
        
        return ToolExecuteResponse(
            status=ResponseStatus.SUCCESS if result["success"] else ResponseStatus.ERROR,
            message="Tool executed successfully" if result["success"] else "Tool execution failed",
            tool_name=result["tool_name"],
            result=result["result"],
            execution_time=result["execution_time"],
            success=result["success"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Tool execution failed: {str(e)}"
        )


@router.get("/{tool_name}/info")
async def get_tool_info(
    tool_name: str,
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    Get detailed information about a specific tool
    
    Returns detailed information including parameters schema and usage examples.
    """
    try:
        if tool_name not in agent_manager.tools:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        tool = agent_manager.tools[tool_name]
        
        return {
            "status": ResponseStatus.SUCCESS,
            "tool_name": tool_name,
            "description": getattr(tool, 'description', 'Tool description'),
            "parameters": {},  # Would extract from tool schema
            "category": "general",
            "enabled": True,
            "usage_examples": []  # Could be added based on tool documentation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tool info: {str(e)}"
        ) 