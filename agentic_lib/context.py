"""
Context classes for agentic library
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

class Role(Enum):
    """Message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

@dataclass
class Message:
    """Represents a message in the conversation"""
    role: Role
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class Context:
    """Manages conversation context and history"""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.metadata: Dict[str, Any] = {}
        
    def add_message(self, role: Role, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the context"""
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        return message
    
    def get_messages(self, role: Optional[Role] = None) -> List[Message]:
        """Get messages, optionally filtered by role"""
        if role is None:
            return self.messages.copy()
        return [msg for msg in self.messages if msg.role == role]
    
    def clear(self):
        """Clear all messages"""
        self.messages.clear()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "metadata": msg.metadata
                }
                for msg in self.messages
            ],
            "metadata": self.metadata
        }
