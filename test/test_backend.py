"""
Formal pytest tests for Spartacus Backend
"""
import pytest
import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestBackendImports:
    """Test that all backend modules can be imported"""
    
    def test_can_import_agentic_lib(self):
        """Test that agentic_lib can be imported"""
        import agentic_lib
        assert agentic_lib is not None
    
    def test_can_import_context_module(self):
        """Test that context module exists and has required classes"""
        try:
            from agentic_lib.context import Context, Message, Role
            assert Context is not None
            assert Message is not None
            assert Role is not None
        except ImportError:
            pytest.fail("agentic_lib.context module is missing")
    
    def test_can_import_gmail_tools(self):
        """Test that Gmail tools can be imported"""
        try:
            from agentic_lib.gmail_tools import gmail_send_tool, gmail_search_tool, gmail_read_tool
            assert gmail_send_tool is not None
            assert gmail_search_tool is not None
            assert gmail_read_tool is not None
        except ImportError:
            pytest.skip("Gmail tools not available - expected if Gmail not configured")
    
    def test_can_import_backend_main(self):
        """Test that backend main module can be imported"""
        try:
            from spartacus_backend.main import app
            assert app is not None
        except ImportError as e:
            pytest.fail(f"Cannot import backend main: {e}")

class TestGmailIntegration:
    """Test Gmail integration components"""
    
    def test_gmail_mcp_directory_exists(self):
        """Test that Gmail MCP server directory exists"""
        gmail_mcp_path = project_root / "mcp_servers" / "gmail"
        assert gmail_mcp_path.exists(), "Gmail MCP server directory not found"
    
    def test_gmail_mcp_package_json(self):
        """Test that Gmail MCP has valid package.json"""
        package_json = project_root / "mcp_servers" / "gmail" / "package.json"
        assert package_json.exists(), "Gmail MCP package.json not found"
        
        with open(package_json) as f:
            pkg_data = json.load(f)
        
        assert "name" in pkg_data, "Package name missing"
        assert "version" in pkg_data, "Package version missing"
    
    def test_gmail_mcp_built(self):
        """Test that Gmail MCP TypeScript is built"""
        dist_path = project_root / "mcp_servers" / "gmail" / "dist"
        assert dist_path.exists(), "Gmail MCP not built - run 'npm run build'"
    
    def test_gmail_credentials_setup(self):
        """Test Gmail credentials are configured"""
        gmail_config_dir = Path.home() / ".gmail-mcp"
        
        if not gmail_config_dir.exists():
            pytest.skip("Gmail not configured - ~/.gmail-mcp directory missing")
        
        credentials_file = gmail_config_dir / "gcp-oauth.keys.json"
        assert credentials_file.exists(), "Gmail credentials file missing"
        
        with open(credentials_file) as f:
            creds = json.load(f)
        
        assert "installed" in creds, "Invalid credentials format"
        assert "client_id" in creds["installed"], "Client ID missing"

class TestProjectStructure:
    """Test project structure and files"""
    
    def test_required_directories_exist(self):
        """Test that all required directories exist"""
        required_dirs = [
            "agentic_lib",
            "spartacus_backend", 
            "spartacus_frontend",
            "test",
            "scripts",
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Required directory missing: {dir_name}"
    
    def test_required_files_exist(self):
        """Test that key files exist"""
        required_files = [
            "agentic_lib/__init__.py",
            "agentic_lib/tools.py",
            "spartacus_backend/__init__.py",
            "spartacus_backend/main.py",
            "start_spartacus.py",
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Required file missing: {file_path}"

class TestAgenticLib:
    """Test agentic_lib functionality"""
    
    def test_context_classes_work(self):
        """Test that context classes can be instantiated and used"""
        from agentic_lib.context import Context, Message, Role
        
        # Test Role enum
        assert Role.SYSTEM.value == "system"
        assert Role.USER.value == "user"
        assert Role.ASSISTANT.value == "assistant"
        
        # Test Message creation
        message = Message(Role.USER, "Hello world")
        assert message.role == Role.USER
        assert message.content == "Hello world"
        assert message.metadata is None
        
        # Test Context creation and usage
        context = Context([])
        assert len(context.messages) == 0
        
        context.add_message(Role.USER, "Test message")
        assert len(context.messages) == 1
        
        last_msg = context.get_last_message()
        assert last_msg is not None
        assert last_msg.content == "Test message"
    
    def test_tools_module_exists(self):
        """Test that tools module exists and has basic structure"""
        import agentic_lib.tools
        assert agentic_lib.tools is not None

if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"]) 