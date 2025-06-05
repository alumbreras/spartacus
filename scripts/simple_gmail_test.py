#!/usr/bin/env python3
"""
Simple Gmail test via direct API call
"""
import requests
import json

def simple_test():
    """Simple test of Gmail functionality"""
    print("🔍 Simple Gmail API Test")
    print("=" * 30)
    
    base_url = "http://127.0.0.1:8000"
    
    # Simple health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Simple agent test with shorter timeout
    print("\nTesting simple message...")
    payload = {
        "message": "Hello",
        "agent_id": "default"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/chat/message",
            json=payload,
            timeout=10
        )
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'No response')[:100]}...")
        else:
            print(f"Error: {response.text}")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_test() 