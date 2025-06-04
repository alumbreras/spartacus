from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class BaseLLMClient(ABC):
    """
    Abstract base class for LLM clients.
    All LLM clients (OpenAI, Azure, etc.) should implement this interface.
    """
    
    @abstractmethod
    def invoke(
        self,
        tools: Optional[List[Dict[str, Any]]] = None,
        message_history: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronously invoke the LLM with a prompt and optional tools for function calling.
        
        Args:
            prompt: The prompt to send to the LLM
            tools: Optional list of tools available to the LLM
            message_history: Optional history of messages in the conversation
            tool_choice: Optional tool choice strategy ("auto", "none", or tool name)
            
        Returns:
            The response from the LLM including content and any tool calls
        """
        pass
    
    @abstractmethod
    async def ainvoke(
        self,
        prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        message_history: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Asynchronously invoke the LLM with a prompt and optional tools for function calling.
        
        Args:
            prompt: The prompt to send to the LLM
            tools: Optional list of tools available to the LLM
            message_history: Optional history of messages in the conversation
            tool_choice: Optional tool choice strategy ("auto", "none", or tool name)
            
        Returns:
            The response from the LLM including content and any tool calls
        """
        pass

    @abstractmethod
    def invoke_with_structured_output(
        self,
        prompt: str,
        output_schema: Type[T],
        message_history: Optional[List[Dict[str, Any]]] = None
    ) -> T:
        """
        Synchronously invoke the LLM with a prompt and get a structured response.
        
        Args:
            prompt: The prompt to send to the LLM
            output_schema: The Pydantic model class that defines the expected response structure
            message_history: Optional history of messages in the conversation
            
        Returns:
            An instance of the provided Pydantic model
        """
        pass

    @abstractmethod
    async def ainvoke_with_structured_output(
        self,
        prompt: str,
        output_schema: Type[T],
        message_history: Optional[List[Dict[str, Any]]] = None
    ) -> T:
        """
        Asynchronously invoke the LLM with a prompt and get a structured response.
        
        Args:
            prompt: The prompt to send to the LLM
            output_schema: The Pydantic model class that defines the expected response structure
            message_history: Optional history of messages in the conversation
            
        Returns:
            An instance of the provided Pydantic model
        """
        pass
