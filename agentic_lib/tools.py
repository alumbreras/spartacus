from typing import Dict, Any, Optional, Type, TypeVar, Callable, Generic, Awaitable
from pydantic import BaseModel
import inspect
import json
from .context_injection import needs_context_injection, get_context_fields

T = TypeVar('T', bound=BaseModel)
C = TypeVar('C', bound=BaseModel)
ToolResultType = TypeVar('ToolResultType')

class ToolCall(BaseModel):
    """Represents a call to a specific tool with its arguments."""
    name: str
    arguments: Dict[str, Any]

class Tool(Generic[ToolResultType]):
    """
    Base class for tools that can be called by the router.
    
    Supports both direct Context passing and automatic dependency injection
    via @context_inject decorator.
    """
    
    def __init__(
        self,
        name: str,
        function: Callable[..., ToolResultType],
        args_schema: Type[BaseModel],
        takes_ctx: bool = True,  # Most tools need context
        result_formatter_fn: Optional[Callable[[ToolResultType], str]] = None,
        context_update_fn: Optional[Callable[[C, ToolResultType], None]] = None,
        description: Optional[str] = None
    ):
        """
        Initialize a tool with its metadata and invocation function.
        
        Args:
            name: Name of the tool
            function: Function to call when the tool is invoked
            args_schema: Pydantic model defining the expected arguments  
            takes_ctx: Whether the tool function needs the agent's context
            result_formatter_fn: Optional function to format the tool result for message history
            context_update_fn: Optional callback to update context after tool execution
            description: Optional description of the tool
        """
        self.name = name
        self.function = function
        self.args_schema = args_schema
        self.takes_ctx = takes_ctx
        self.result_formatter_fn = result_formatter_fn
        self.context_update_fn = context_update_fn
        
        # ✅ Check for context injection setup
        if needs_context_injection(function):
            required_fields = get_context_fields(function)
            print(f"✅ Tool '{name}' will auto-inject context fields: {required_fields}")
            self._uses_context_injection = True
            self._required_context_fields = required_fields
        else:
            self._uses_context_injection = False
            self._required_context_fields = []
        
        # Extract description from docstring if not provided
        if description:
            self.description = description
        else:
            doc = inspect.getdoc(function)
            self.description = doc if doc else f"Tool {self.name}"

    async def invoke(self, ctx: Optional[C], arguments: Dict[str, Any]) -> str:
        """
        Invoke the tool with validated arguments and optional context.
        
        Args:
            ctx: Agent's context (contains message_history, index_name, products, etc.)
            arguments: Arguments to validate and pass to the function
            
        Returns:
            str: Formatted result for adding to message history
        """
        # Validate arguments against schema
        validated_args = self.args_schema.model_validate(arguments)
        
        # Call function with appropriate context handling
        if self.takes_ctx:
            if ctx is None:
                raise ValueError(f"Tool {self.name} requires context but none was provided")
            
            # ✅ Auto-injection based on decorator metadata
            if self._uses_context_injection:
                # Build kwargs with injected context fields
                function_kwargs = {"args": validated_args}
                
                for field_name in self._required_context_fields:
                    if hasattr(ctx, field_name):
                        function_kwargs[field_name] = getattr(ctx, field_name)
                    else:
                        raise RuntimeError(
                            f"Context missing required field '{field_name}' "
                            f"for function {self.function.__name__}"
                        )
                
                # Call with auto-injected parameters
                if inspect.iscoroutinefunction(self.function):
                    raw_result: ToolResultType = await self.function(**function_kwargs)
                else:
                    raw_result: ToolResultType = self.function(**function_kwargs)
            
            else:
                # ✅ Legacy: pass ctx directly (backward compatibility)
                if inspect.iscoroutinefunction(self.function):
                    raw_result: ToolResultType = await self.function(ctx, validated_args)
                else:
                    raw_result: ToolResultType = self.function(ctx, validated_args)
        
        else:
            # Function doesn't need context
            if inspect.iscoroutinefunction(self.function):
                raw_result: ToolResultType = await self.function(validated_args)
            else:
                raw_result: ToolResultType = self.function(validated_args)
        
        # ✅ GENERIC: Apply context update callback if provided
        if self.context_update_fn and ctx is not None:
            self.context_update_fn(ctx, raw_result)
        
        # Format result for message history
        if self.result_formatter_fn:
            formatted_result = self.result_formatter_fn(raw_result)
        else:
            formatted_result = self._default_format(raw_result)
        
        return formatted_result
    
    def _default_format(self, result: ToolResultType) -> str:
        """
        Default formatting for tool results.
        
        Args:
            result: The raw result from the tool function
            
        Returns:
            str: Formatted result for message history
        """
        if isinstance(result, str):
            return result
        elif isinstance(result, dict):
            # For dict results, create a clean JSON representation
            return json.dumps(result, indent=2)
        elif hasattr(result, 'model_dump_json'):
            # For Pydantic models
            return result.model_dump_json(indent=2)
        elif hasattr(result, 'model_dump'):
            # For Pydantic models that don't have model_dump_json
            return json.dumps(result.model_dump(), indent=2)
        else:
            # Fallback to string representation
            return str(result)
    
    def get_openai_tool(self) -> Dict[str, Any]:
        """
        Convert tool to OpenAI function format for LLM tool calling.
        
        Returns:
            Dict compatible with OpenAI's tool calling format
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_json_schema()
            }
        } 