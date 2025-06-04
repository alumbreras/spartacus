"""
Base Agent for multi-loop conversational AI.
"""

import json
import logging
from typing import List, Dict, Optional, Any, Callable, Awaitable
from pydantic import BaseModel

# ✅ Updated imports for standalone operation
from llm_clients.azure_openai_client import AzureOpenAIClient
from spartacus_services.context import Context
from agentic_lib.tools import Tool  # ✅ Use original Tool implementation
from spartacus_services.logger import logger as structured_logger

logger = logging.getLogger(__name__)

class AgentResponse(BaseModel):
    """Response from the agent after processing user input."""
    text_response: Optional[str] = None
    tools_executed: List[str] = []
    iterations: int = 0
    finished: bool = False
    final_answer: Optional[str] = None

class BaseAgent:
    """
    Generic base agent that runs in a loop until a 'final_answer' tool is called.
    
    This is the most generic agent pattern possible:
    1. User provides input
    2. Agent reasons with LLM
    3. Agent executes tools  
    4. Agent continues looping until final_answer tool
    5. Agent returns final response
    
    This pattern enables:
    - Multi-step reasoning (chain-of-thought)
    - Complex workflows with multiple tool calls
    - Self-correction and iteration
    - Research and analysis tasks
    
    Subclasses can override behavior for specific use cases:
    - Single-shot agents (stop after first tool execution)
    - Domain-specific agents (custom loop conditions)
    - Specialized reasoning patterns
    """
    
    def __init__(
        self, 
        llm_client: AzureOpenAIClient, 
        tools: Dict[str, Tool], 
        system_prompt: str,
        max_iterations: int = 10
    ):
        """
        Initialize the base agent.
        
        Args:
            llm_client: LLM client for reasoning and tool selection
            tools: Dictionary of available tools {name: tool_instance}
            system_prompt: System prompt for the agent's behavior
            max_iterations: Maximum iterations to prevent infinite loops
        """
        self.llm_client = llm_client
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        
    def _prepare_messages(self, user_input: str, context: Context) -> List[Dict[str, Any]]:
        """Prepare messages for LLM including system prompt and conversation history."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        messages.extend(context.message_history)
        
        # Add current user input (only on first iteration)
        if not context.message_history or not any(msg.get("role") == "user" for msg in context.message_history[-5:]):
            messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def _get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Convert tools to OpenAI function format."""
        return [tool.get_openai_tool() for tool in self.tools.values()]
    
    async def _call_llm_with_tools(self, messages: List[Dict[str, Any]]) -> Any:
        """Call LLM with tools and get response."""
        tools = self._get_tools_for_llm()
        
        response = await self.llm_client.invoke(
            messages=messages,
            tools=tools,
            tool_choice="required"  # Force tool usage for consistency
        )
        
        return response
    
    def _add_assistant_message_to_history(self, context: Context, content: Optional[str], tool_calls: List[Any]):
        """Add assistant's message with tool calls to conversation history."""
        formatted_tool_calls = []
        for tool_call in tool_calls:
            formatted_tool_calls.append({
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            })
        
        context.message_history.append({
            "role": "assistant",
            "content": content,
            "tool_calls": formatted_tool_calls
        })
    
    def _add_tool_result_to_history(self, context: Context, tool_call_id: str, result: str):
        """Add tool execution result to conversation history."""
        context.message_history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result
        })
    
    async def _execute_tools_sequentially(self, context: Context, tool_calls: List[Any]) -> tuple[List[str], bool, Optional[str]]:
        """
        Execute tool calls sequentially and check for final_answer.
        
        Returns:
            (executed_tools, is_final, final_answer_content)
        """
        executed_tools = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_instance = self.tools.get(tool_name)
            
            # Check for final_answer tool
            if tool_name == "final_answer":
                arguments = json.loads(tool_call.function.arguments)
                final_answer = arguments.get("answer", "Task completed.")
                
                # Add final answer to history
                self._add_tool_result_to_history(context, tool_call.id, f"Final answer: {final_answer}")
                
                return executed_tools, True, final_answer
            
            if tool_instance:
                structured_logger.info(f"Base agent executing tool: {tool_name} (args: {tool_call.function.arguments})")
                
                # Execute tool with context injection and callbacks
                formatted_result = await tool_instance.invoke(
                    ctx=context,
                    arguments=json.loads(tool_call.function.arguments)
                )
                
                # Add tool result to conversation history
                self._add_tool_result_to_history(context, tool_call.id, formatted_result)
                
                executed_tools.append(tool_name)
                
                logger.info(f"Tool {tool_name} executed successfully")
                
            else:
                # Handle unknown tool
                logger.warning(f"Unknown tool requested: {tool_name}")
                error_content = json.dumps({"error": f"Unknown tool: {tool_name}"})
                self._add_tool_result_to_history(context, tool_call.id, error_content)
        
        return executed_tools, False, None
    
    async def run_until_final_answer(self, user_input: str, context: Context) -> AgentResponse:
        """
        Main agent execution loop - runs until final_answer tool is called.
        
        Args:
            user_input: User's input message
            context: Current conversation context
            
        Returns:
            AgentResponse with execution results
        """
        all_executed_tools = []
        iteration = 0
        
        try:
            while iteration < self.max_iterations:
                iteration += 1
                structured_logger.info(f"Base agent iteration {iteration}")
                
                # 1. Prepare messages with system prompt and history
                messages = self._prepare_messages(user_input, context)
                
                # 2. Call LLM to determine tool usage
                llm_response = await self._call_llm_with_tools(messages)
                
                # 3. Handle LLM response
                if llm_response.tool_calls:
                    # Add assistant's message with tool calls to history  
                    # ✅ FIXED: content=None when tool_calls are present (OpenAI requirement)
                    self._add_assistant_message_to_history(context, None, llm_response.tool_calls)
                    
                    # Execute tools sequentially and check for final_answer
                    executed_tools, is_final, final_answer = await self._execute_tools_sequentially(context, llm_response.tool_calls)
                    
                    all_executed_tools.extend(executed_tools)
                    
                    # Check if we should stop
                    if is_final:
                        return AgentResponse(
                            text_response=final_answer,
                            tools_executed=all_executed_tools,
                            iterations=iteration,
                            finished=True,
                            final_answer=final_answer
                        )
                
                else:
                    # LLM responded directly without tool calls - treat as final answer
                    context.message_history.append({"role": "assistant", "content": llm_response.content})
                    
                    return AgentResponse(
                        text_response=llm_response.content,
                        tools_executed=all_executed_tools,
                        iterations=iteration,
                        finished=True,
                        final_answer=llm_response.content
                    )
            
            # Max iterations reached
            logger.warning(f"Base agent reached max iterations ({self.max_iterations})")
            return AgentResponse(
                text_response="I've reached the maximum number of reasoning steps. Please try rephrasing your request.",
                tools_executed=all_executed_tools,
                iterations=iteration,
                finished=False,
                final_answer=None
            )
                
        except Exception as e:
            logger.error(f"Base agent execution error: {e}", exc_info=True)
            raise 