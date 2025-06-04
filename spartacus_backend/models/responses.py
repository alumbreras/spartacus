"""
Pydantic response models for Spartacus Backend API
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    """Response status types"""
    SUCCESS = "success"
    ERROR = "error"
    PROCESSING = "processing"
    PARTIAL = "partial"


class BaseResponse(BaseModel):
    """Base response model"""
    status: ResponseStatus = Field(..., description="Response status")
    message: Optional[str] = Field(default=None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class AgentRunResponse(BaseResponse):
    """Response from agent execution"""
    agent_id: str = Field(..., description="Agent execution ID")
    agent_type: str = Field(..., description="Type of agent that was run")
    response: str = Field(..., description="Agent's response")
    iterations: int = Field(..., description="Number of iterations performed")
    execution_time: float = Field(..., description="Execution time in seconds")
    tools_used: List[str] = Field(default=[], description="Tools used during execution")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Updated context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Agent execution completed",
                "timestamp": "2024-01-15T10:30:00Z",
                "agent_id": "agent-run-123",
                "agent_type": "analysis",
                "response": "Based on the data analysis...",
                "iterations": 3,
                "execution_time": 12.5,
                "tools_used": ["python_executor", "data_analyzer"],
                "context": {"analysis_result": "completed"}
            }
        }


class ChatMessage(BaseModel):
    """Chat message model"""
    id: str = Field(..., description="Message ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")
    agent_type: Optional[str] = Field(default=None, description="Agent type if from agent")
    tools_used: List[str] = Field(default=[], description="Tools used in this message")


class ChatResponse(BaseResponse):
    """Response for chat operations"""
    session_id: str = Field(..., description="Chat session ID")
    message: ChatMessage = Field(..., description="The response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-15T10:30:00Z",
                "session_id": "chat-123",
                "message": {
                    "id": "msg-456",
                    "role": "assistant",
                    "content": "Hello! How can I help you?",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "agent_type": "default",
                    "tools_used": []
                }
            }
        }


class ChatHistoryResponse(BaseResponse):
    """Response for chat history"""
    session_id: str = Field(..., description="Chat session ID")
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    total_messages: int = Field(..., description="Total number of messages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2024-01-15T10:30:00Z",
                "session_id": "chat-123",
                "messages": [],
                "total_messages": 0
            }
        }


class AgentInfo(BaseModel):
    """Agent information model"""
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    type: str = Field(..., description="Agent type")
    tools: List[str] = Field(..., description="Available tools")
    model: str = Field(..., description="LLM model")
    created_at: datetime = Field(..., description="Creation timestamp")
    active: bool = Field(..., description="Whether agent is active")


class AgentListResponse(BaseResponse):
    """Response for listing agents"""
    agents: List[AgentInfo] = Field(..., description="List of available agents")
    total_agents: int = Field(..., description="Total number of agents")


class ToolInfo(BaseModel):
    """Tool information model"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters schema")
    category: str = Field(..., description="Tool category")
    enabled: bool = Field(..., description="Whether tool is enabled")


class ToolListResponse(BaseResponse):
    """Response for listing tools"""
    tools: List[ToolInfo] = Field(..., description="List of available tools")
    total_tools: int = Field(..., description="Total number of tools")


class ToolExecuteResponse(BaseResponse):
    """Response from tool execution"""
    tool_name: str = Field(..., description="Executed tool name")
    result: Any = Field(..., description="Tool execution result")
    execution_time: float = Field(..., description="Execution time in seconds")
    success: bool = Field(..., description="Whether execution was successful")


class SystemStatusResponse(BaseResponse):
    """System status response"""
    version: str = Field(..., description="Application version")
    uptime: float = Field(..., description="System uptime in seconds")
    active_agents: int = Field(..., description="Number of active agents")
    active_sessions: int = Field(..., description="Number of active chat sessions")
    memory_usage: float = Field(..., description="Memory usage percentage")
    cpu_usage: float = Field(..., description="CPU usage percentage")


class ErrorResponse(BaseResponse):
    """Error response model"""
    error_code: str = Field(..., description="Error code")
    error_details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")
    
    def __init__(self, **data):
        if "status" not in data:
            data["status"] = ResponseStatus.ERROR
        super().__init__(**data) 