"""
Final Answer tool for terminating agent loops.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field

# ✅ Updated imports for standalone operation
from agentic_lib.tools import Tool  # ✅ Use original Tool implementation
from spartacus_services.context import Context

class FinalAnswerInput(BaseModel):
    """Input parameters for the final_answer tool."""
    answer: str = Field(description="The final answer to provide to the user")

class FinalAnswerResult(BaseModel):
    """Result from the final_answer tool."""
    answer: str
    completed: bool = True

async def final_answer_function(ctx: Context, args: FinalAnswerInput) -> str:
    """
    Provide a final answer and terminate the agent loop.
    
    This tool signals that the agent has completed its task and is ready
    to provide a final response to the user. When this tool is called,
    the BaseAgent will stop looping and return the provided answer.
    
    Args:
        ctx: Current conversation context (not modified by this tool)
        args: Arguments containing the final answer
        
    Returns:
        Formatted result indicating completion
    """
    # This tool doesn't modify context - it just signals completion
    result = FinalAnswerResult(answer=args.answer, completed=True)
    
    return f"Final answer provided: {args.answer}"

# Create the tool instance
final_answer_tool = Tool(
    name="final_answer",
    function=final_answer_function,
    args_schema=FinalAnswerInput,
    takes_ctx=True,  # Takes context but doesn't modify it
    result_formatter_fn=None,  # Use default formatting
    context_update_fn=None,  # No context updates
    description="Provide a final answer to the user and complete the task"
) 