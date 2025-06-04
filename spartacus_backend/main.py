"""
Spartacus Desktop Backend - FastAPI Application
Main entry point that exposes the agentic_lib as REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from spartacus_backend.api.chat import router as chat_router
from spartacus_backend.api.agents import router as agents_router
from spartacus_backend.api.tools import router as tools_router
from spartacus_backend.api.system import router as system_router
from spartacus_backend.services.agent_manager import SpartacusAgentManager
from spartacus_backend.config.settings import settings
import spartacus_backend.dependencies as dependencies


# Global agent manager instance
agent_manager: SpartacusAgentManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    global agent_manager
    
    # Startup
    print("🚀 Starting Spartacus Backend...")
    agent_manager = SpartacusAgentManager()
    await agent_manager.initialize()
    
    # Set the agent manager in dependencies
    dependencies.set_agent_manager(agent_manager)
    
    print("✅ Agent Manager initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Spartacus Backend...")
    if agent_manager:
        await agent_manager.cleanup()
    print("✅ Cleanup completed")


# Create FastAPI app
app = FastAPI(
    title="Spartacus Desktop Backend",
    description="FastAPI backend for Spartacus Desktop - Claude Desktop alternative",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(tools_router, prefix="/api/tools", tags=["tools"])
app.include_router(system_router, prefix="/api/system", tags=["system"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Spartacus Desktop Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_manager": agent_manager is not None
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    ) 