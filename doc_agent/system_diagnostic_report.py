#!/usr/bin/env python3
"""
Comprehensive System Diagnostic for Spartacus Desktop
Generates a detailed report of system status
"""
import sys
import os
import json
import subprocess
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

class SpartacusDiagnostic:
    """Comprehensive diagnostic for Spartacus Desktop system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.timestamp = datetime.now()
        
    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run complete system diagnostic"""
        print("🏛️  SPARTACUS DESKTOP COMPREHENSIVE DIAGNOSTIC")
        print("=" * 70)
        print(f"📅 Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Project Root: {self.project_root}")
        print()
        
        # Add project to Python path
        sys.path.insert(0, str(self.project_root))
        
        # Run all diagnostic tests
        self.results = {
            "timestamp": self.timestamp.isoformat(),
            "project_root": str(self.project_root),
            "python_version": sys.version,
            "platform": sys.platform,
            "tests": {}
        }
        
        tests = [
            ("Project Structure", self.test_project_structure),
            ("Python Modules", self.test_python_modules),
            ("Gmail Integration", self.test_gmail_integration),
            ("Backend Imports", self.test_backend_imports),
            ("API Availability", self.test_api_availability),
            ("Frontend Setup", self.test_frontend_setup),
            ("Dependencies", self.test_dependencies),
        ]
        
        for test_name, test_func in tests:
            print(f"🔍 Running {test_name} Test...")
            try:
                result = test_func()
                self.results["tests"][test_name] = result
                status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
                print(f"   {status}")
                if not result.get("success", False):
                    print(f"   Issues: {len(result.get('issues', []))}")
            except Exception as e:
                self.results["tests"][test_name] = {
                    "success": False,
                    "error": str(e),
                    "issues": [f"Test crashed: {e}"]
                }
                print(f"   ❌ CRASH: {e}")
            print()
        
        # Generate summary
        self.generate_summary()
        
        return self.results
    
    def test_project_structure(self) -> Dict[str, Any]:
        """Test project directory structure"""
        required_dirs = [
            "agentic_lib",
            "spartacus_backend", 
            "spartacus_frontend",
            "mcp_servers",
            "test",
            "scripts",
            "doc_agent"
        ]
        
        required_files = [
            "start_spartacus.py",
            "agentic_lib/__init__.py",
            "agentic_lib/tools.py",
            "spartacus_backend/__init__.py",
            "spartacus_backend/main.py",
            "spartacus_frontend/package.json",
        ]
        
        issues = []
        
        # Check directories
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                issues.append(f"Missing directory: {dir_name}")
        
        # Check files
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                issues.append(f"Missing file: {file_path}")
        
        return {
            "success": len(issues) == 0,
            "checked_dirs": len(required_dirs),
            "checked_files": len(required_files),
            "issues": issues
        }
    
    def test_python_modules(self) -> Dict[str, Any]:
        """Test Python module imports"""
        modules_to_test = [
            ("fastapi", "FastAPI framework"),
            ("uvicorn", "ASGI server"),
            ("openai", "OpenAI client"),
            ("requests", "HTTP requests"),
            ("pathlib", "Path utilities"),
        ]
        
        spartacus_modules = [
            "agentic_lib",
            "agentic_lib.tools",
            "spartacus_backend",
            "spartacus_backend.main",
        ]
        
        issues = []
        import_results = {}
        
        # Test external modules
        for module_name, description in modules_to_test:
            try:
                __import__(module_name)
                import_results[module_name] = "✅"
            except ImportError as e:
                import_results[module_name] = "❌"
                issues.append(f"Cannot import {module_name}: {e}")
        
        # Test Spartacus modules
        for module_name in spartacus_modules:
            try:
                __import__(module_name)
                import_results[module_name] = "✅"
            except ImportError as e:
                import_results[module_name] = "❌"
                issues.append(f"Cannot import {module_name}: {e}")
        
        return {
            "success": len(issues) == 0,
            "import_results": import_results,
            "issues": issues
        }
    
    def test_gmail_integration(self) -> Dict[str, Any]:
        """Test Gmail integration setup"""
        issues = []
        gmail_status = {}
        
        # Check Gmail MCP server
        mcp_path = self.project_root / "mcp_servers" / "gmail"
        gmail_status["mcp_directory"] = mcp_path.exists()
        
        if not mcp_path.exists():
            issues.append("Gmail MCP server directory missing")
        else:
            # Check package.json
            package_json = mcp_path / "package.json"
            gmail_status["package_json"] = package_json.exists()
            
            # Check if built
            dist_path = mcp_path / "dist"
            gmail_status["typescript_built"] = dist_path.exists()
            
            if not dist_path.exists():
                issues.append("Gmail MCP TypeScript not built")
        
        # Check Gmail credentials
        gmail_config_dir = Path.home() / ".gmail-mcp"
        gmail_status["config_directory"] = gmail_config_dir.exists()
        
        if gmail_config_dir.exists():
            credentials_file = gmail_config_dir / "gcp-oauth.keys.json"
            gmail_status["credentials_file"] = credentials_file.exists()
            
            token_file = gmail_config_dir / "token.json"
            gmail_status["token_file"] = token_file.exists()
            
            if not credentials_file.exists():
                issues.append("Gmail credentials file missing")
            
            if not token_file.exists():
                issues.append("Gmail access token missing - need OAuth authentication")
        else:
            issues.append("Gmail configuration directory missing")
        
        # Test Gmail tools import
        try:
            from agentic_lib.gmail_tools import gmail_send_tool, gmail_search_tool, gmail_read_tool
            gmail_status["tools_importable"] = True
        except ImportError as e:
            gmail_status["tools_importable"] = False
            issues.append(f"Cannot import Gmail tools: {e}")
        
        return {
            "success": len(issues) == 0,
            "gmail_status": gmail_status,
            "issues": issues
        }
    
    def test_backend_imports(self) -> Dict[str, Any]:
        """Test backend module imports specifically"""
        issues = []
        
        # Test critical imports
        try:
            from spartacus_backend.main import app
            backend_app_ok = True
        except ImportError as e:
            backend_app_ok = False
            issues.append(f"Cannot import backend app: {e}")
        
        # Test context module
        try:
            from agentic_lib.context import Context, Message, Role
            context_ok = True
        except ImportError as e:
            context_ok = False
            issues.append(f"Missing context module: {e}")
            # Try to create it
            self.create_missing_context_module()
            issues.append("Created minimal context module")
        
        # Test agent manager
        try:
            from spartacus_backend.services.agent_manager import SpartacusAgentManager
            agent_manager_ok = True
        except ImportError as e:
            agent_manager_ok = False
            issues.append(f"Cannot import agent manager: {e}")
        
        return {
            "success": len(issues) == 0,
            "backend_app": backend_app_ok,
            "context_module": context_ok,
            "agent_manager": agent_manager_ok,
            "issues": issues
        }
    
    def test_api_availability(self) -> Dict[str, Any]:
        """Test if API endpoints are available"""
        base_url = "http://127.0.0.1:8000"
        endpoints = ["/health", "/", "/docs"]
        
        issues = []
        endpoint_status = {}
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=2)
                endpoint_status[endpoint] = {
                    "status_code": response.status_code,
                    "available": response.status_code == 200
                }
                if response.status_code != 200:
                    issues.append(f"Endpoint {endpoint} returned {response.status_code}")
            except requests.exceptions.RequestException:
                endpoint_status[endpoint] = {
                    "status_code": None,
                    "available": False
                }
                issues.append(f"Endpoint {endpoint} not accessible (backend not running)")
        
        return {
            "success": len(issues) == 0,
            "base_url": base_url,
            "endpoint_status": endpoint_status,
            "issues": issues
        }
    
    def test_frontend_setup(self) -> Dict[str, Any]:
        """Test frontend setup"""
        frontend_path = self.project_root / "spartacus_frontend"
        issues = []
        
        frontend_status = {
            "directory_exists": frontend_path.exists()
        }
        
        if not frontend_path.exists():
            issues.append("Frontend directory missing")
            return {
                "success": False,
                "frontend_status": frontend_status,
                "issues": issues
            }
        
        # Check package.json
        package_json = frontend_path / "package.json"
        frontend_status["package_json"] = package_json.exists()
        
        # Check node_modules
        node_modules = frontend_path / "node_modules"
        frontend_status["dependencies_installed"] = node_modules.exists()
        
        if not node_modules.exists():
            issues.append("Frontend dependencies not installed - run 'npm install'")
        
        return {
            "success": len(issues) == 0,
            "frontend_status": frontend_status,
            "issues": issues
        }
    
    def test_dependencies(self) -> Dict[str, Any]:
        """Test system dependencies"""
        dependencies = ["node", "npm", "python3"]
        issues = []
        dependency_status = {}
        
        for dep in dependencies:
            try:
                result = subprocess.run([dep, "--version"], capture_output=True, text=True, timeout=5)
                dependency_status[dep] = {
                    "available": result.returncode == 0,
                    "version": result.stdout.strip() if result.returncode == 0 else None
                }
                if result.returncode != 0:
                    issues.append(f"Dependency {dep} not available")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                dependency_status[dep] = {
                    "available": False,
                    "version": None
                }
                issues.append(f"Dependency {dep} not found")
        
        return {
            "success": len(issues) == 0,
            "dependency_status": dependency_status,
            "issues": issues
        }
    
    def create_missing_context_module(self):
        """Create minimal context module if missing"""
        context_file = self.project_root / "agentic_lib" / "context.py"
        
        if not context_file.exists():
            context_content = '''"""
Basic context module for Spartacus
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class Message:
    role: Role
    content: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass 
class Context:
    messages: List[Message]
    metadata: Optional[Dict[str, Any]] = None
    
    def add_message(self, role: Role, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the context"""
        self.messages.append(Message(role, content, metadata))
    
    def get_last_message(self) -> Optional[Message]:
        """Get the last message"""
        return self.messages[-1] if self.messages else None
'''
            
            with open(context_file, 'w') as f:
                f.write(context_content)
    
    def generate_summary(self):
        """Generate diagnostic summary"""
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for test in self.results["tests"].values() if test.get("success", False))
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Show critical issues
        critical_issues = []
        for test_name, result in self.results["tests"].items():
            if not result.get("success", False):
                issues = result.get("issues", [])
                for issue in issues:
                    critical_issues.append(f"{test_name}: {issue}")
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES:")
            for issue in critical_issues[:10]:  # Show first 10
                print(f"  • {issue}")
            if len(critical_issues) > 10:
                print(f"  ... and {len(critical_issues) - 10} more issues")
        else:
            print("✅ No critical issues found!")
        
        print()
    
    def save_report(self, filename: str = None):
        """Save diagnostic report to file"""
        if filename is None:
            filename = f"diagnostic_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        report_path = self.project_root / "doc_agent" / filename
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"📄 Report saved to: {report_path}")

def main():
    """Main diagnostic function"""
    diagnostic = SpartacusDiagnostic()
    results = diagnostic.run_full_diagnostic()
    diagnostic.save_report()
    
    # Return exit code based on success
    total_tests = len(results["tests"])
    passed_tests = sum(1 for test in results["tests"].values() if test.get("success", False))
    
    if passed_tests == total_tests:
        print("🎉 All systems operational!")
        return 0
    else:
        print("⚠️  System has issues that need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 