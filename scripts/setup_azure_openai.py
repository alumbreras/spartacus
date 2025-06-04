#!/usr/bin/env python3
"""
Setup script for Azure OpenAI configuration in Spartacus Desktop
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with Azure OpenAI configuration"""
    
    print("🔧 Azure OpenAI Configuration Setup")
    print("=" * 50)
    
    # Check if .env already exists
    env_path = Path(".env")
    if env_path.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("   Overwrite? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("   Setup cancelled.")
            return
    
    print("\n📋 Please provide your Azure OpenAI credentials:")
    print("   (You can find these in Azure Portal > OpenAI Service > Keys and Endpoint)")
    
    # Get Azure OpenAI credentials
    api_key = input("\n🔑 Azure OpenAI API Key: ").strip()
    endpoint = input("🌐 Azure OpenAI Endpoint (e.g., https://your-resource.openai.azure.com/): ").strip()
    model = input("🤖 Deployment/Model Name (default: gpt-4): ").strip() or "gpt-4"
    api_version = input("📅 API Version (default: 2024-10-21): ").strip() or "2024-10-21"
    
    # Validate inputs
    if not api_key:
        print("❌ API Key is required!")
        sys.exit(1)
    
    if not endpoint:
        print("❌ Endpoint is required!")
        sys.exit(1)
    
    if not endpoint.startswith("https://"):
        endpoint = f"https://{endpoint}"
    
    if not endpoint.endswith("/"):
        endpoint = f"{endpoint}/"
    
    # Create .env content
    env_content = f"""# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY={api_key}
AZURE_OPENAI_ENDPOINT={endpoint}
AZURE_OPENAI_MODEL={model}
AZURE_OPENAI_API_VERSION={api_version}

# Backend Settings
SPARTACUS_HOST=127.0.0.1
SPARTACUS_PORT=8000
SPARTACUS_LOG_LEVEL=INFO

# Development
SPARTACUS_RELOAD=true

# Environment
NODE_ENV=development
"""
    
    # Write .env file
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully!")
        print(f"   Location: {env_path.absolute()}")
        print("\n🔒 Security Note:")
        print("   - .env file is ignored by git (contains sensitive data)")
        print("   - Never commit API keys to version control")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_azure_openai():
    """Test Azure OpenAI connection"""
    print("\n🧪 Testing Azure OpenAI connection...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from agentic_lib.llm_clients.azure_openai_client import AzureOpenAIClient
        import asyncio
        
        async def test_connection():
            try:
                client = AzureOpenAIClient()
                
                # Simple test message
                messages = [
                    {"role": "user", "content": "Hello! Say 'Azure OpenAI is working' if you can read this."}
                ]
                
                response = await client.invoke(messages)
                print(f"✅ Connection successful!")
                print(f"   Response: {response.content[:100]}...")
                return True
                
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                print("\n💡 Troubleshooting tips:")
                print("   - Check your API key and endpoint")
                print("   - Verify the deployment name exists")
                print("   - Ensure API version is supported")
                return False
        
        return asyncio.run(test_connection())
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the Spartacus project directory")
        return False

def main():
    """Main setup function"""
    print("🏛️  Spartacus Desktop - Azure OpenAI Setup")
    print("=" * 50)
    
    # Change to project root if running from scripts/
    current_dir = Path.cwd()
    if current_dir.name == "scripts":
        os.chdir("..")
        print(f"📁 Changed to project root: {Path.cwd()}")
    
    # Create .env file
    if create_env_file():
        print("\n" + "=" * 50)
        
        # Test connection
        test_choice = input("\n🔍 Test Azure OpenAI connection now? (Y/n): ").lower().strip()
        if test_choice != 'n':
            if test_azure_openai():
                print("\n🎉 Setup completed successfully!")
                print("   You can now start Spartacus Desktop with:")
                print("   python start_spartacus.py")
            else:
                print("\n⚠️  Setup completed but connection test failed.")
                print("   Please check your credentials and try again.")
        else:
            print("\n✅ Setup completed!")
            print("   Test the connection later with:")
            print("   python test_standalone.py")

if __name__ == "__main__":
    main() 