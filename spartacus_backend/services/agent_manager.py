"""
SpartacusAgentManager - Wrapper service for agentic_lib integration
Manages agent lifecycle, execution, and state
"""

import asyncio
import uuid
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum

# Import agentic_lib components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from agentic_lib.base_agent import BaseAgent
from agentic_lib.tools import Tool
from spartacus_services.context import Context
from spartacus_services.logger import get_logger
from agentic_lib.llm_clients.azure_openai_client import AzureOpenAIClient
from agentic_lib.final_answer import final_answer_tool

# Import Gmail tools
try:
    from agentic_lib.gmail_tools import gmail_send_tool, gmail_search_tool, gmail_read_tool
    GMAIL_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Gmail tools not available: {e}")
    GMAIL_TOOLS_AVAILABLE = False

from spartacus_backend.models.requests import AgentType
from spartacus_backend.models.responses import AgentInfo, ToolInfo, AgentListResponse, ResponseStatus
from spartacus_backend.config.settings import settings

logger = get_logger(__name__)


class AgentInstance:
    """Individual agent instance with its state"""
    
    def __init__(self, agent_id: str, agent_type: str, agent):
        self.id = agent_id
        self.type = agent_type
        self.agent = agent
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        self.active = True
        # Create a simple mock context instead of using Context
        self.context = {
            "messages": [],
            "session_data": {}
        }
    
    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used = datetime.now()


class SpartacusAgentManager:
    """Manages agentic_lib agents and their execution"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInstance] = {}
        self.active_sessions: Dict[str, str] = {}  # session_id -> agent_id
        self.tools: Dict[str, Tool] = {}
        self.llm_client: Optional[AzureOpenAIClient] = None
        self.start_time = time.time()
        
    async def initialize(self):
        """Initialize the agent manager"""
        logger.info("Initializing SpartacusAgentManager...")
        
        # Initialize LLM client
        try:
            logger.info("Attempting to initialize Azure OpenAI client...")
            self.llm_client = AzureOpenAIClient()
            
            # Test the client to make sure it's working
            test_messages = [{"role": "user", "content": "test"}]
            await self.llm_client.invoke(test_messages)
            
            logger.info("✅ LLM client initialized and tested successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM client: {e}")
            logger.warning("⚠️  Continuing without LLM client - agents will use mock responses")
            self.llm_client = None
        
        # Initialize default tools
        await self._load_tools()
        
        # Create default agent types
        await self._create_default_agents()
        
        logger.info(f"✅ Agent Manager initialized with {len(self.agents)} agents and {len(self.tools)} tools")
        logger.info(f"🤖 LLM Client status: {'REAL Azure OpenAI' if self.llm_client else 'MOCK responses'}")
        
        # Debug: Check which agents are real vs mock
        for agent_id, agent_instance in self.agents.items():
            agent_type = "REAL Azure OpenAI" if hasattr(agent_instance.agent, 'llm_client') else "MOCK"
            logger.info(f"🔧 Agent {agent_id}: {agent_type}")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up SpartacusAgentManager...")
        
        # Stop all active agents
        for agent_instance in self.agents.values():
            agent_instance.active = False
        
        self.agents.clear()
        self.active_sessions.clear()
        
        logger.info("✅ Cleanup completed")
    
    async def _load_tools(self):
        """Load available tools from agentic_lib"""
        try:
            # Register actual tools
            self.tools["final_answer"] = final_answer_tool
            logger.info(f"Registered tool: final_answer")
            
            # Register Gmail tools if available
            if GMAIL_TOOLS_AVAILABLE:
                self.tools[gmail_send_tool.name] = gmail_send_tool
                self.tools[gmail_search_tool.name] = gmail_search_tool
                self.tools[gmail_read_tool.name] = gmail_read_tool
                
                logger.info(f"Registered Gmail tools: {gmail_send_tool.name}, {gmail_search_tool.name}, {gmail_read_tool.name}")
            
            # Create mock tools for missing functionality (future implementation)
            mock_tools = {
                "python_executor": self._create_mock_tool("python_executor", "Execute Python code"),
                "file_reader": self._create_mock_tool("file_reader", "Read files"),
                "web_search": self._create_mock_tool("web_search", "Search the web"),
            }
            
            self.tools.update(mock_tools)
            logger.info(f"Created {len(mock_tools)} mock tools for development")
                
        except Exception as e:
            logger.warning(f"Could not load some tools: {e}")
            # Create basic mock tools for testing
            self.tools = {
                "final_answer": self._create_mock_tool("final_answer", "Provide final answer"),
                "python_executor": self._create_mock_tool("python_executor", "Execute Python code"),
                "file_reader": self._create_mock_tool("file_reader", "Read files"),
                "web_search": self._create_mock_tool("web_search", "Search the web"),
            }
    
    def _create_mock_tool(self, name: str, description: str) -> Tool:
        """Create a mock tool for testing purposes"""
        class MockTool:
            def __init__(self, tool_name: str, tool_description: str):
                self.name = tool_name
                self.description = tool_description
                
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {
                    "status": "success",
                    "result": f"Mock execution of {self.name}",
                    "parameters": kwargs
                }
            
            def get_openai_tool(self) -> Dict[str, Any]:
                """Return OpenAI tool format for this mock tool"""
                return {
                    "type": "function",
                    "function": {
                        "name": self.name,
                        "description": self.description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": f"Input for {self.name}"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                }
        
        return MockTool(name, description)
    
    async def _create_default_agents(self):
        """Create default agent types"""
        default_configs = {
            AgentType.DEFAULT: {
                "name": "Default Agent",
                "description": "General purpose conversational agent",
                "instructions": "You are a helpful AI assistant.",
                "tools": list(self.tools.keys())
            },
            AgentType.RESEARCH: {
                "name": "Research Agent",
                "description": "Specialized in research and information gathering",
                "instructions": "You are a research specialist. Help users find and analyze information.",
                "tools": ["web_search", "file_reader", "final_answer"]
            },
            AgentType.CODING: {
                "name": "Coding Agent", 
                "description": "Specialized in programming and code analysis",
                "instructions": "You are a programming expert. Help with coding, debugging, and development.",
                "tools": ["python_executor", "file_reader", "final_answer"]
            },
            AgentType.ANALYSIS: {
                "name": "Analysis Agent",
                "description": "Specialized in data analysis and insights",
                "instructions": "You are a data analyst. Help analyze data and provide insights.",
                "tools": ["python_executor", "file_reader", "final_answer"]
            },
            AgentType.CREATIVE: {
                "name": "Creative Agent",
                "description": "Specialized in creative tasks and writing",
                "instructions": "You are a creative assistant. Help with writing, brainstorming, and creative tasks.",
                "tools": ["file_reader", "final_answer"]
            }
        }
        
        # Add Email Agent if Gmail tools are available
        if GMAIL_TOOLS_AVAILABLE:
            default_configs["email"] = {
                "name": "Email Assistant",
                "description": "Specialized in Gmail management and email operations",
                "instructions": "You are an email management specialist. You can send emails, search through Gmail, read specific emails, and help organize email communications. Use Gmail tools to manage emails efficiently.",
                "tools": ["gmail_send", "gmail_search", "gmail_read", "final_answer"]
            }
        
        for agent_type, config in default_configs.items():
            agent_id = await self.create_agent(
                agent_type=agent_type.value if hasattr(agent_type, 'value') else agent_type,
                **config
            )
            logger.info(f"Created default agent: {agent_type.value if hasattr(agent_type, 'value') else agent_type} ({agent_id})")
    
    async def create_agent(
        self,
        agent_type: str,
        name: str,
        description: str,
        instructions: str,
        tools: List[str],
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Create a new agent instance"""
        agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        
        try:
            # Create real BaseAgent with Azure OpenAI client
            if not self.llm_client:
                logger.warning(f"No LLM client available, creating mock agent for {name}")
                # Create a simple mock agent instead of BaseAgent for now
                class MockAgent:
                    def __init__(self, instructions: str):
                        self.instructions = instructions
                        self.iteration_count = 1
                        
                    async def run_until_final_answer(self, user_input: str, context):
                        return f"Mock response to '{user_input}': I'm a {agent_type} agent. {self.instructions[:100]}"
                
                agent = MockAgent(instructions)
            else:
                # Create real agent with Azure OpenAI
                logger.info(f"Creating REAL agent {name} with Azure OpenAI client")
                agent_tools = {name: tool for name, tool in self.tools.items() if name in tools}
                system_prompt = f"You are a {name}. {instructions}\n\nAvailable tools: {', '.join(agent_tools.keys())}"
                
                agent = BaseAgent(
                    llm_client=self.llm_client,
                    tools=agent_tools,
                    system_prompt=system_prompt,
                    max_iterations=20
                )
                logger.info(f"✅ Real BaseAgent created for {name} with {len(agent_tools)} tools")
            
            # Create agent instance wrapper
            agent_instance = AgentInstance(agent_id, agent_type, agent)
            self.agents[agent_id] = agent_instance
            
            logger.info(f"Created agent: {name} ({agent_id})")
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to create agent {name}: {e}")
            raise
    
    async def run_agent(
        self,
        user_input: str,
        agent_type: str = AgentType.DEFAULT.value,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        max_iterations: int = 20
    ) -> Dict[str, Any]:
        """Run an agent with user input"""
        start_time = time.time()
        
        try:
            # Find or create agent for this session
            agent_id = await self._get_agent_for_session(session_id, agent_type)
            agent_instance = self.agents[agent_id]
            agent_instance.update_last_used()
            
            # Update context if provided
            if context:
                agent_instance.context.update(context)
            
            # Check if this is a real BaseAgent or mock
            if hasattr(agent_instance.agent, 'llm_client'):
                # Real BaseAgent - create proper Context object
                from spartacus_services.context import Context
                agent_context = Context()
                agent_context.message_history = agent_instance.context.get("messages", [])
                
                # Run the real agent with Azure OpenAI
                logger.info(f"Running real agent {agent_id} with Azure OpenAI")
                agent_response = await agent_instance.agent.run_until_final_answer(
                    user_input, 
                    agent_context
                )
                
                response = agent_response.final_answer or agent_response.text_response or "Agent completed successfully"
                tools_used = agent_response.tools_executed
                iterations = agent_response.iterations
                
                # Update context with new messages
                agent_instance.context["messages"] = agent_context.message_history
                
            else:
                # Mock agent fallback
                logger.info(f"Running mock agent {agent_id}")
                response = await agent_instance.agent.run_until_final_answer(
                    user_input,
                    agent_instance.context
                )
                tools_used = []  # Mock tools used
                iterations = getattr(agent_instance.agent, 'iteration_count', 1)
            
            execution_time = time.time() - start_time
            
            return {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "response": response,
                "iterations": iterations,
                "execution_time": execution_time,
                "tools_used": tools_used,
                "context": agent_instance.context
            }
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise
    
    async def _get_agent_for_session(self, session_id: Optional[str], agent_type: str) -> str:
        """Get or create agent for a session"""
        if session_id and session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Find an available agent of the requested type
        for agent_id, agent_instance in self.agents.items():
            if agent_instance.type == agent_type and agent_instance.active:
                if session_id:
                    self.active_sessions[session_id] = agent_id
                return agent_id
        
        # No available agent found, create a new one
        raise Exception(f"No agent available for type: {agent_type}")
    
    def _extract_tools_used(self, agent: BaseAgent) -> List[str]:
        """Extract list of tools used during agent execution"""
        # This would be implemented based on how your BaseAgent tracks tool usage
        # For now, return empty list
        return []
    
    async def get_available_agents(self) -> List[AgentInfo]:
        """Get list of available agents"""
        agents = []
        for agent_id, agent_instance in self.agents.items():
            agents.append(AgentInfo(
                id=agent_id,
                name=agent_instance.type.title() + " Agent",
                description=f"Agent of type {agent_instance.type}",
                type=agent_instance.type,
                tools=list(self.tools.keys()),
                model=settings.default_model,
                created_at=agent_instance.created_at,
                active=agent_instance.active
            ))
        return agents
    
    async def get_available_tools(self) -> List[ToolInfo]:
        """Get list of available tools"""
        tools = []
        for tool_name, tool in self.tools.items():
            tools.append(ToolInfo(
                name=tool_name,
                description=getattr(tool, 'description', 'Tool description'),
                parameters={},  # Would extract from tool schema
                category="general",
                enabled=True
            ))
        return tools
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a specific tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        tool = self.tools[tool_name]
        start_time = time.time()
        
        try:
            result = await tool.execute(**parameters)
            execution_time = time.time() - start_time
            
            return {
                "tool_name": tool_name,
                "result": result,
                "execution_time": execution_time,
                "success": True
            }
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tool execution failed: {e}")
            return {
                "tool_name": tool_name,
                "result": str(e),
                "execution_time": execution_time,
                "success": False
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information"""
        import psutil
        
        return {
            "version": "1.0.0",
            "uptime": time.time() - self.start_time,
            "active_agents": len([a for a in self.agents.values() if a.active]),
            "active_sessions": len(self.active_sessions),
            "memory_usage": psutil.virtual_memory().percent,
            "cpu_usage": psutil.cpu_percent()
        } 