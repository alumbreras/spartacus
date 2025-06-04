"""
Agentic Library - Autonomous AI Agents with Tool Calling

A sophisticated library for building ReAct (Reasoning + Acting) agents
that can use tools and maintain conversation context.

Key Components:
- BaseAgent: Multi-loop agent with tool calling
- Tools: Extensible tool framework with context injection  
- Context: Conversation and session management
- LLM Clients: Integration with various LLM providers
"""

from .base_agent import BaseAgent, AgentResponse
from .tools import Tool, ToolCall
from .context_injection import context_inject, needs_context_injection, get_context_fields
from .final_answer import final_answer_tool, FinalAnswerInput, FinalAnswerResult
from .llm_clients import AzureOpenAIClient

__version__ = "1.0.0"

__all__ = [
    # Core agent functionality
    "BaseAgent",
    "AgentResponse",
    
    # Tool system
    "Tool", 
    "ToolCall",
    "final_answer_tool",
    "FinalAnswerInput",
    "FinalAnswerResult",
    
    # Context injection
    "context_inject",
    "needs_context_injection", 
    "get_context_fields",
    
    # LLM clients
    "AzureOpenAIClient",
] 