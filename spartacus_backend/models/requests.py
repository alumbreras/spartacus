"""
Pydantic request models for Spartacus Backend API
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class AgentType(str, Enum):
    """Available agent types"""
    DEFAULT = "default"
    RESEARCH = "research"
    CODING = "coding"
    ANALYSIS = "analysis"
    CREATIVE = "creative"


class AgentRunRequest(BaseModel):
    """Request to run an agent"""
    user_input: str = Field(..., description="User input message")
    agent_type: AgentType = Field(default=AgentType.DEFAULT, description="Type of agent to run")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    session_id: Optional[str] = Field(default=None, description="Chat session ID")
    max_iterations: Optional[int] = Field(default=10, description="Maximum agent iterations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "Help me analyze this data",
                "agent_type": "analysis",
                "context": {"data_source": "file.csv"},
                "session_id": "chat-123",
                "max_iterations": 5
            }
        }


class ChatMessageRequest(BaseModel):
    """Request to send a chat message"""
    message: str = Field(..., description="Chat message content")
    session_id: Optional[str] = Field(default=None, description="Chat session ID")
    agent_type: AgentType = Field(default=AgentType.DEFAULT, description="Agent type for this message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Message context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, can you help me?",
                "session_id": "chat-123",
                "agent_type": "default",
                "context": {}
            }
        }


class AgentCreateRequest(BaseModel):
    """Request to create a custom agent"""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    instructions: str = Field(..., description="Agent system instructions")
    tools: List[str] = Field(default=[], description="Available tools for the agent")
    model: Optional[str] = Field(default=None, description="LLM model to use")
    temperature: Optional[float] = Field(default=0.7, description="LLM temperature")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "my_custom_agent",
                "description": "A specialized agent for data analysis",
                "instructions": "You are an expert data analyst...",
                "tools": ["python_executor", "file_reader"],
                "model": "gpt-4",
                "temperature": 0.3
            }
        }


class ToolExecuteRequest(BaseModel):
    """Request to execute a specific tool"""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Execution context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "python_executor",
                "parameters": {"code": "print('Hello World')"},
                "context": {"session_id": "tool-session-123"}
            }
        }


class ConfigUpdateRequest(BaseModel):
    """Request to update system configuration"""
    settings: Dict[str, Any] = Field(..., description="Settings to update")
    
    class Config:
        json_schema_extra = {
            "example": {
                "settings": {
                    "default_model": "gpt-4-turbo",
                    "temperature": 0.5,
                    "max_tokens": 8000
                }
            }
        } 