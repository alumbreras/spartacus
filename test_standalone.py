#!/usr/bin/env python3
"""
Test script for Spartacus standalone agentic_lib.
This verifies that all dependencies are working correctly.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test imports
try:
    from agentic_lib.llm_clients.azure_openai_client import AzureOpenAIClient
    from spartacus_services.context import Context
    from agentic_lib.tools import Tool
    from spartacus_services.logger import logger
    from agentic_lib.base_agent import BaseAgent, AgentResponse
    from agentic_lib.final_answer import final_answer_tool
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

async def test_basic_functionality():
    """Test basic agent functionality."""
    
    print("\n🧪 Testing Spartacus Standalone Functionality...")
    
    # 1. Test Context creation
    print("1. Testing Context...")
    context = Context(
        session_id="test-session",
        user_id="test-user"
    )
    context.add_simple_user_message("Hello, this is a test!")
    print(f"   ✅ Context created with {len(context.message_history)} messages")
    
    # 2. Test LLM Client (if configured)
    print("2. Testing LLM Client...")
    try:
        llm_client = AzureOpenAIClient()
        print("   ✅ LLM client initialized")
        
        # Only test if we have credentials
        if os.getenv("AZURE_OPENAI_API_KEY"):
            print("   🔑 Azure OpenAI credentials found")
        else:
            print("   ⚠️  No Azure OpenAI credentials (set AZURE_OPENAI_API_KEY for full test)")
            
    except Exception as e:
        print(f"   ❌ LLM client error: {e}")
        return False
    
    # 3. Test Tool system
    print("3. Testing Tool System...")
    tools = {"final_answer": final_answer_tool}
    print(f"   ✅ Tools loaded: {list(tools.keys())}")
    
    # 4. Test Agent creation
    print("4. Testing Agent Creation...")
    try:
        agent = BaseAgent(
            llm_client=llm_client,
            tools=tools,
            system_prompt="You are a helpful assistant. When ready to respond, use the final_answer tool.",
            max_iterations=3
        )
        print("   ✅ Agent created successfully")
    except Exception as e:
        print(f"   ❌ Agent creation error: {e}")
        return False
    
    # 5. Test agent execution (if we have API key)
    if os.getenv("AZURE_OPENAI_API_KEY"):
        print("5. Testing Agent Execution...")
        try:
            response = await agent.run_until_final_answer(
                user_input="Say hello and test the final_answer tool",
                context=context
            )
            print(f"   ✅ Agent executed: {response.iterations} iterations")
            print(f"   ✅ Final answer: {response.final_answer}")
            print(f"   ✅ Tools used: {response.tools_executed}")
        except Exception as e:
            print(f"   ❌ Agent execution error: {e}")
            return False
    else:
        print("5. Skipping Agent Execution (no API key)")
    
    print("\n🎉 All tests passed! Your agentic_lib is ready for Spartacus!")
    return True

async def main():
    """Main test function."""
    print("🚀 Spartacus Standalone Test Suite")
    print("=" * 50)
    
    success = await test_basic_functionality()
    
    if success:
        print("\n✅ READY FOR PHASE 2: FastAPI Backend")
        print("Next steps:")
        print("  1. Create FastAPI backend")
        print("  2. Build agent endpoints")
        print("  3. Start Electron frontend")
    else:
        print("\n❌ Some tests failed. Please fix issues before proceeding.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main()) 