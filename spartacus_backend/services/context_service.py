"""
ChatContextService - Manages chat sessions and message history
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os

from models.responses import ChatMessage
from spartacus_services.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class ChatContextService:
    """Service for managing chat sessions and message history"""
    
    def __init__(self):
        self.sessions: Dict[str, List[ChatMessage]] = {}
        self.session_metadata: Dict[str, Dict[str, Any]] = {}
        self.persistence_file = os.path.join(settings.data_dir, "chat_sessions.json")
        
        # Load existing sessions from disk
        self._load_sessions()
    
    def add_message(self, session_id: str, message: ChatMessage):
        """Add a message to a chat session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            self.session_metadata[session_id] = {
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "message_count": 0
            }
        
        self.sessions[session_id].append(message)
        self.session_metadata[session_id]["last_updated"] = datetime.now()
        self.session_metadata[session_id]["message_count"] += 1
        
        # Trim history if it exceeds maximum
        if len(self.sessions[session_id]) > settings.max_chat_history:
            self.sessions[session_id] = self.sessions[session_id][-settings.max_chat_history:]
            logger.info(f"Trimmed chat history for session {session_id}")
        
        # Save to disk
        self._save_sessions()
        
        logger.debug(f"Added message to session {session_id}")
    
    def get_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages from a chat session"""
        return self.sessions.get(session_id, [])
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get context for a chat session"""
        messages = self.get_messages(session_id)
        metadata = self.session_metadata.get(session_id, {})
        
        return {
            "session_id": session_id,
            "messages": [self._message_to_dict(msg) for msg in messages],
            "metadata": metadata,
            "message_count": len(messages)
        }
    
    def clear_session(self, session_id: str):
        """Clear all messages from a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        if session_id in self.session_metadata:
            del self.session_metadata[session_id]
        
        self._save_sessions()
        logger.info(f"Cleared session {session_id}")
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all chat sessions with metadata"""
        sessions = []
        for session_id, metadata in self.session_metadata.items():
            sessions.append({
                "session_id": session_id,
                "message_count": len(self.sessions.get(session_id, [])),
                "created_at": metadata.get("created_at"),
                "last_updated": metadata.get("last_updated")
            })
        return sessions
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about all chat sessions"""
        total_sessions = len(self.sessions)
        total_messages = sum(len(messages) for messages in self.sessions.values())
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "average_messages_per_session": total_messages / total_sessions if total_sessions > 0 else 0
        }
    
    def _message_to_dict(self, message: ChatMessage) -> Dict[str, Any]:
        """Convert ChatMessage to dictionary"""
        return {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.isoformat(),
            "agent_type": message.agent_type,
            "tools_used": message.tools_used
        }
    
    def _dict_to_message(self, data: Dict[str, Any]) -> ChatMessage:
        """Convert dictionary to ChatMessage"""
        return ChatMessage(
            id=data["id"],
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            agent_type=data.get("agent_type"),
            tools_used=data.get("tools_used", [])
        )
    
    def _save_sessions(self):
        """Save sessions to disk"""
        try:
            data = {
                "sessions": {},
                "metadata": {}
            }
            
            # Convert sessions to serializable format
            for session_id, messages in self.sessions.items():
                data["sessions"][session_id] = [
                    self._message_to_dict(msg) for msg in messages
                ]
            
            # Convert metadata to serializable format
            for session_id, metadata in self.session_metadata.items():
                data["metadata"][session_id] = {
                    "created_at": metadata["created_at"].isoformat(),
                    "last_updated": metadata["last_updated"].isoformat(),
                    "message_count": metadata["message_count"]
                }
            
            with open(self.persistence_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
    
    def _load_sessions(self):
        """Load sessions from disk"""
        try:
            if not os.path.exists(self.persistence_file):
                logger.info("No existing chat sessions found")
                return
            
            with open(self.persistence_file, 'r') as f:
                data = json.load(f)
            
            # Load sessions
            sessions_data = data.get("sessions", {})
            for session_id, messages_data in sessions_data.items():
                self.sessions[session_id] = [
                    self._dict_to_message(msg_data) for msg_data in messages_data
                ]
            
            # Load metadata
            metadata_data = data.get("metadata", {})
            for session_id, metadata in metadata_data.items():
                self.session_metadata[session_id] = {
                    "created_at": datetime.fromisoformat(metadata["created_at"]),
                    "last_updated": datetime.fromisoformat(metadata["last_updated"]),
                    "message_count": metadata["message_count"]
                }
            
            logger.info(f"Loaded {len(self.sessions)} chat sessions from disk")
            
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            # Initialize empty sessions on load failure
            self.sessions = {}
            self.session_metadata = {} 