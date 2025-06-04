#!/usr/bin/env python3
"""
Test script for Spartacus Backend
Tests basic functionality of the FastAPI backend
"""

import sys
import os
import asyncio
import httpx
import json
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from spartacus_services.logger import get_logger

logger = get_logger(__name__)

BASE_URL = "http://127.0.0.1:8000"


async def test_health_check():
    """Test health check endpoint"""
    logger.info("🔍 Testing health check...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                logger.info("✅ Health check passed")
                return True
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False


async def test_system_status():
    """Test system status endpoint"""
    logger.info("🔍 Testing system status...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/system/status")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ System status: {data['status']}")
                logger.info(f"   Active agents: {data['active_agents']}")
                logger.info(f"   Uptime: {data['uptime']:.2f}s")
                return True
            else:
                logger.error(f"❌ System status failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ System status error: {e}")
            return False


async def test_list_agents():
    """Test list agents endpoint"""
    logger.info("🔍 Testing list agents...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/agents/list")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Found {data['total_agents']} agents")
                for agent in data['agents'][:3]:  # Show first 3
                    logger.info(f"   - {agent['name']} ({agent['type']})")
                return True
            else:
                logger.error(f"❌ List agents failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ List agents error: {e}")
            return False


async def test_list_tools():
    """Test list tools endpoint"""
    logger.info("🔍 Testing list tools...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/tools/list")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Found {data['total_tools']} tools")
                for tool in data['tools']:
                    logger.info(f"   - {tool['name']}: {tool['description']}")
                return True
            else:
                logger.error(f"❌ List tools failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ List tools error: {e}")
            return False


async def test_run_agent():
    """Test running an agent"""
    logger.info("🔍 Testing agent execution...")
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "user_input": "Hello! Can you tell me what you can do?",
                "agent_type": "default",
                "max_iterations": 5
            }
            
            response = await client.post(
                f"{BASE_URL}/api/agents/run",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Agent execution successful")
                logger.info(f"   Agent response: {data['response'][:100]}...")
                logger.info(f"   Execution time: {data['execution_time']:.2f}s")
                logger.info(f"   Iterations: {data['iterations']}")
                return True
            else:
                logger.error(f"❌ Agent execution failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Agent execution error: {e}")
            return False


async def test_chat_message():
    """Test chat message endpoint"""
    logger.info("🔍 Testing chat message...")
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "message": "What's the weather like?",
                "agent_type": "default"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/chat/message",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Chat message successful")
                logger.info(f"   Session ID: {data['session_id']}")
                logger.info(f"   Response: {data['message']['content'][:100]}...")
                return True
            else:
                logger.error(f"❌ Chat message failed: {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Chat message error: {e}")
            return False


async def run_all_tests():
    """Run all backend tests"""
    logger.info("🧪 Starting Spartacus Backend Tests")
    logger.info(f"📍 Testing against: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health_check),
        ("System Status", test_system_status),
        ("List Agents", test_list_agents),
        ("List Tools", test_list_tools),
        ("Run Agent", test_run_agent),
        ("Chat Message", test_chat_message),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("🧪 TEST SUMMARY")
    logger.info("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\n📊 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Backend is working correctly.")
        return True
    else:
        logger.warning("⚠️  Some tests failed. Check the backend logs.")
        return False


async def main():
    """Main test function"""
    try:
        success = await run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("🧪 Spartacus Backend Test Suite")
    print("Make sure the backend is running on http://127.0.0.1:8000")
    print("You can start it with: python spartacus_backend/start_backend.py")
    print()
    
    asyncio.run(main()) 