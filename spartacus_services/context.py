"""
Context schema for Spartacus agents.
Recreated from app.services.schemas.context import Context
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Context(BaseModel):
    """
    Context object that holds conversation state and metadata.
    
    This replaces app.services.schemas.context.Context for standalone operation.
    """
    
    # Core conversation data
    message_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Chat history in OpenAI format with roles (system, user, assistant, tool)"
    )
    
    # Session management
    session_id: Optional[str] = Field(
        default=None,
        description="Unique session identifier"
    )
    
    # User/Agent identification
    user_id: Optional[str] = Field(
        default=None,
        description="User identifier"
    )
    
    agent_id: Optional[str] = Field(
        default=None,
        description="Agent identifier"
    )
    
    # Additional context fields that may be used by tools
    # (These can be added based on your specific needs)
    index_name: Optional[str] = Field(
        default=None,
        description="Search index name for tools that need it"
    )
    
    products: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Product data for commerce-related tools"
    )
    
    workspace_id: Optional[str] = Field(
        default=None,
        description="Workspace identifier"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for tools and agents"
    )
    
    # Configuration
    max_iterations: int = Field(
        default=10,
        description="Maximum iterations for agent loops"
    )
    
    temperature: float = Field(
        default=0.7,
        description="LLM temperature setting"
    )
    
    # ✅ Basic utility methods (no OpenAI-specific logic)
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.message_history = []
    
    def get_last_n_messages(self, n: int) -> List[Dict[str, Any]]:
        """Get the last n messages from history."""
        return self.message_history[-n:] if self.message_history else []
    
    def add_simple_user_message(self, content: str) -> None:
        """Add a simple user message (for testing/basic use)."""
        self.message_history.append({
            "role": "user",
            "content": content
        }) 