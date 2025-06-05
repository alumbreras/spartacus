#!/usr/bin/env python3
"""
Script to check module availability and diagnose import issues
"""
import sys
import os
from pathlib import Path

def check_module_imports():
    """Check if all required modules can be imported"""
    print("🔍 SPARTACUS MODULE DIAGNOSTIC")
    print("=" * 50)
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))
    
    print(f"📁 Current directory: {current_dir}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    print()
    
    # Test basic imports
    modules_to_test = [
        ("sys", "System module"),
        ("pathlib", "Path utilities"),
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("openai", "OpenAI client"),
    ]
    
    print("📦 BASIC MODULES:")
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name:15} - {description}")
        except ImportError as e:
            print(f"  ❌ {module_name:15} - FAILED: {e}")
    
    print()
    
    # Test Spartacus modules
    print("🏛️  SPARTACUS MODULES:")
    spartacus_modules = [
        "agentic_lib",
        "agentic_lib.tools",
        "agentic_lib.context",
        "agentic_lib.gmail_tools",
        "spartacus_backend",
        "spartacus_backend.main",
        "spartacus_backend.services.agent_manager",
    ]
    
    for module_name in spartacus_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name} - FAILED: {e}")
    
    print()
    
    # Check directory structure
    print("📂 DIRECTORY STRUCTURE:")
    dirs_to_check = [
        "agentic_lib",
        "spartacus_backend", 
        "spartacus_frontend",
        "mcp_servers",
        "test",
        "scripts",
    ]
    
    for dir_name in dirs_to_check:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            print(f"  ✅ {dir_name:20} - {dir_path}")
        else:
            print(f"  ❌ {dir_name:20} - NOT FOUND")
    
    print()
    
    # Check specific files
    print("📄 KEY FILES:")
    files_to_check = [
        "agentic_lib/__init__.py",
        "agentic_lib/context.py",
        "agentic_lib/tools.py",
        "agentic_lib/gmail_tools.py",
        "spartacus_backend/__init__.py",
        "spartacus_backend/main.py",
    ]
    
    for file_path in files_to_check:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - NOT FOUND")
    
    print()
    print("🔧 DIAGNOSTIC COMPLETE")

if __name__ == "__main__":
    check_module_imports() 