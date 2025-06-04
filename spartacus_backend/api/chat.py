"""
Chat API Router
Endpoints for chat functionality and messaging
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import uuid
import json
from datetime import datetime

from spartacus_backend.models.requests import ChatMessageRequest, AgentType
from spartacus_backend.models.responses import (
    ChatResponse, ChatMessage, ChatHistoryResponse, BaseResponse, ResponseStatus
)
from spartacus_backend.services.agent_manager import SpartacusAgentManager
from spartacus_backend.dependencies import get_agent_manager

router = APIRouter()

# Simple in-memory chat storage (would be replaced with database in production)
chat_sessions: Dict[str, List[Dict[str, Any]]] = {}

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatMessageRequest,
    agent_manager: SpartacusAgentManager = Depends(get_agent_manager)
):
    """
    Send a chat message and get agent response
    
    Process a user message through the specified agent and return the response.
    Maintains chat history and session context.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"chat-{uuid.uuid4().hex[:8]}"
        
        # Generate message ID
        message_id = f"msg-{uuid.uuid4().hex[:8]}"
        
        # Store user message
        user_message = ChatMessage(
            id=message_id,
            role="user",
            content=request.message,
            timestamp=datetime.now(),
            agent_type=None,
            tools_used=[]
        )
        chat_sessions[session_id] = chat_sessions.get(session_id, []) + [user_message]
        
        # Get chat context for agent
        chat_context = chat_sessions[session_id]
        
        # Run agent with user input
        result = await agent_manager.run_agent(
            user_input=request.message,
            agent_type=request.agent_type.value,
            context=request.context or {},
            session_id=session_id,
            max_iterations=10
        )
        
        # Create assistant message
        assistant_message_id = f"msg-{uuid.uuid4().hex[:8]}"
        assistant_message = ChatMessage(
            id=assistant_message_id,
            role="assistant",
            content=result["response"],
            timestamp=datetime.now(),
            agent_type=result["agent_type"],
            tools_used=result["tools_used"]
        )
        
        # Store assistant message
        chat_sessions[session_id] = chat_sessions[session_id] + [assistant_message]
        
        return ChatResponse(
            status=ResponseStatus.SUCCESS,
            session_id=session_id,
            message=assistant_message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """
    Get chat history for a session
    
    Retrieve all messages from the specified chat session.
    """
    try:
        messages = chat_sessions.get(session_id, [])
        
        return ChatHistoryResponse(
            status=ResponseStatus.SUCCESS,
            message="Chat history retrieved successfully",
            session_id=session_id,
            messages=messages,
            total_messages=len(messages)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat history: {str(e)}"
        )


@router.post("/clear/{session_id}", response_model=BaseResponse)
async def clear_chat_history(session_id: str):
    """
    Clear chat history for a session
    
    Remove all messages from the specified chat session.
    """
    try:
        chat_sessions[session_id] = []
        
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            message=f"Chat history cleared for session {session_id}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear chat history: {str(e)}"
        )


@router.get("/sessions", response_model=List[Dict[str, Any]])
async def list_chat_sessions():
    """
    List all active chat sessions
    
    Returns a list of all chat sessions with their metadata.
    """
    try:
        sessions = list(chat_sessions.keys())
        return sessions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list chat sessions: {str(e)}"
        )


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat streaming
    
    Enables real-time bidirectional communication for chat messages.
    """
    await websocket.accept()
    connection_id = f"ws-{uuid.uuid4().hex[:8]}"
    active_connections[connection_id] = websocket
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Extract message information
            user_message = message_data.get("message", "")
            session_id = message_data.get("session_id", f"ws-{uuid.uuid4().hex[:8]}")
            agent_type = message_data.get("agent_type", "default")
            
            # Send acknowledgment
            await websocket.send_text(json.dumps({
                "type": "message_received",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }))
            
            try:
                # Get agent manager
                agent_manager = get_agent_manager()
                
                # Process message through agent
                result = await agent_manager.run_agent(
                    user_input=user_message,
                    agent_type=agent_type,
                    session_id=session_id
                )
                
                # Send response back to client
                await websocket.send_text(json.dumps({
                    "type": "agent_response",
                    "session_id": session_id,
                    "message": result["response"],
                    "agent_type": result["agent_type"],
                    "tools_used": result["tools_used"],
                    "execution_time": result["execution_time"],
                    "timestamp": datetime.now().isoformat()
                }))
                
            except Exception as e:
                # Send error message
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "session_id": session_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }))
                
    except WebSocketDisconnect:
        if connection_id in active_connections:
            del active_connections[connection_id]
    except Exception as e:
        if connection_id in active_connections:
            del active_connections[connection_id]


async def broadcast_to_session(session_id: str, message: Dict[str, Any]):
    """
    Broadcast a message to all WebSocket connections for a session
    """
    message_json = json.dumps(message)
    connections_to_remove = []
    
    for connection_id, websocket in active_connections.items():
        try:
            await websocket.send_text(message_json)
        except Exception:
            connections_to_remove.append(connection_id)
    
    # Clean up disconnected connections
    for connection_id in connections_to_remove:
        del active_connections[connection_id] 