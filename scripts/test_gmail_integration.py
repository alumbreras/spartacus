#!/usr/bin/env python3
"""
Test script for Gmail MCP integration in Spartacus Desktop
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from spartacus_backend.services.agent_manager import SpartacusAgentManager

async def test_gmail_integration():
    """Test Gmail integration with Spartacus"""
    
    print("🧪 Testing Gmail Integration with Spartacus")
    print("=" * 60)
    
    # Initialize agent manager
    agent_manager = SpartacusAgentManager()
    await agent_manager.initialize()
    
    print(f"\n📊 Agent Manager Status:")
    print(f"   Agents: {len(agent_manager.agents)}")
    print(f"   Tools: {len(agent_manager.tools)}")
    
    # List all agents
    print(f"\n🤖 Available Agents:")
    for agent_id, agent_instance in agent_manager.agents.items():
        print(f"   - {agent_instance.type}: {agent_id}")
    
    # List all tools
    print(f"\n🛠️  Available Tools:")
    for tool_name, tool in agent_manager.tools.items():
        print(f"   - {tool_name}: {getattr(tool, 'description', 'No description')}")
    
    # Test email agent if available
    email_agents = [a for a in agent_manager.agents.values() if a.type == "email"]
    if email_agents:
        print(f"\n✅ Email agent found! Testing...")
        
        try:
            result = await agent_manager.run_agent(
                user_input="¿Qué herramientas Gmail tienes disponibles?",
                agent_type="email"
            )
            
            print(f"📧 Email Agent Response:")
            print(f"   {result.get('response', 'No response')}")
            
        except Exception as e:
            print(f"❌ Error testing email agent: {e}")
    
    else:
        print(f"\n❌ No email agent found")
    
    # Cleanup
    await agent_manager.cleanup()
    print(f"\n✅ Test completed")

if __name__ == "__main__":
    asyncio.run(test_gmail_integration()) 