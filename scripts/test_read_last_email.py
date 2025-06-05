#!/usr/bin/env python3
"""
Test reading the last email via Spartacus API to ensure it's not a mock response.
"""
import requests
import json
import time

def test_read_last_email():
    """Test reading the last email via the Spartacus API"""
    print("🧪 Testing Read Last Email functionality via Spartacus API")
    print("=" * 60)

    base_url = "http://127.0.0.1:8000"
    
    # Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend healthy: {response.json()}")
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach backend: {e}")
        return

    # Ask the agent to read the last email
    print("\n💬 Sending request: 'lee mi ultimo email'")
    payload = {
        "message": "lee mi ultimo email",
        "agent_id": "email"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/chat/message",
            json=payload,
            timeout=120  # Increased timeout for the agent to process
        )
        response.raise_for_status()
        
        response_data = response.json()
        print("\n📝 Agent Response:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))

        print("\n🕵️ Verifying response...")
        # Get the assistant's message content
        assistant_message = response_data.get("message", {}).get("content", "")
        
        # More robust check
        is_mock = "mock-email" in assistant_message.lower() or "mcp connection failed" in assistant_message.lower()
        has_real_content = "llms on the run" in assistant_message.lower() or "vikram sreekanti" in assistant_message.lower() or "zapier" in assistant_message.lower()

        if is_mock:
            print("❌ FAIL: The response contains mock data.")
        elif has_real_content:
            print("✅ PASS: The response contains real email data.")
        else:
            print("🤔 UNKNOWN: The response does not contain expected real or mock data. Please verify manually.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Test failed with connection error: {e}")
    except json.JSONDecodeError:
        print(f"❌ Test failed: Could not decode JSON response: {response.text}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensure backend is running before testing
    time.sleep(5)  # Give backend a moment to start if just launched
    test_read_last_email() 