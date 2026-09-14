"""
Pytest Test Suite for Gmail & Google Drive MCP Server (Layered Architecture)
Supports both 'pytest' execution (with pytest fixtures & markers) and direct CLI execution.
"""

import json
import sys
import os
from pathlib import Path
import pytest  # Explicit Pytest framework import

# Ensure UTF-8 output encoding for Windows console compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ["DEBUG"] = "true"

# Add backend directory and workspace root to sys.path
backend_dir = Path(__file__).parent
root_dir = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from handlers.tool_handler import get_handler, ToolHandler
from services.gmail_service import get_gmail_service
from services.drive_service import get_drive_service
from config.settings import CREDENTIALS_PATH


# ============================================================================
# PYTEST FIXTURES (Equivalent to JUnit @BeforeEach)
# ============================================================================

@pytest.fixture
def tool_handler() -> ToolHandler:
    """Pytest fixture providing an initialized ToolHandler instance"""
    return get_handler("pytest-user")


# ============================================================================
# PYTEST TEST CASES (With explicit Pytest markers and assertions)
# ============================================================================

@pytest.mark.credentials
@pytest.mark.integration
def test_credentials():
    """Test if Google credentials file exists and loads successfully"""
    assert CREDENTIALS_PATH.exists(), f"credential.json not found at: {CREDENTIALS_PATH}"
    
    gmail_service = get_gmail_service()
    creds = gmail_service.get_credentials()
    assert creds is not None, "Failed to load Google credentials"


@pytest.mark.gmail
@pytest.mark.integration
def test_gmail_api(tool_handler: ToolHandler):
    """Test Gmail list_emails tool execution via ToolHandler fixture"""
    result_json = tool_handler.list_emails(query="is:unread", max_results=5)
    result = json.loads(result_json)
    
    assert result.get("success") is True, f"Gmail list_emails failed: {result.get('error')}"
    assert "data" in result, "Response payload missing 'data' field"
    assert "count" in result["data"], "Response data missing 'count' field"


@pytest.mark.drive
@pytest.mark.integration
def test_drive_api(tool_handler: ToolHandler):
    """Test Google Drive list_drive_files tool execution via ToolHandler fixture"""
    result_json = tool_handler.list_drive_files(max_results=5)
    result = json.loads(result_json)
    
    assert result.get("success") is True, f"Drive list_drive_files failed: {result.get('error')}"
    assert "data" in result, "Response payload missing 'data' field"
    assert "files" in result["data"], "Response data missing 'files' list"


@pytest.mark.gmail
@pytest.mark.integration
def test_email_functions(tool_handler: ToolHandler):
    """Test email list & read tool integration"""
    result_json = tool_handler.list_emails(query="is:unread", max_results=1)
    result = json.loads(result_json)
    
    assert result.get("success") is True, f"list_emails failed: {result.get('error')}"
    
    emails = result.get("data", {}).get("emails", [])
    if emails:
        email_id = emails[0]["id"]
        read_json = tool_handler.read_email(email_id)
        read_result = json.loads(read_json)
        assert read_result.get("success") is True, f"read_email failed for ID {email_id}: {read_result.get('error')}"


@pytest.mark.drive
@pytest.mark.integration
def test_drive_search(tool_handler: ToolHandler):
    """Test Google Drive search_drive tool execution"""
    result_json = tool_handler.search_drive(keyword="test", max_results=5)
    result = json.loads(result_json)
    
    assert result.get("success") is True, f"search_drive failed: {result.get('error')}"
    assert "data" in result, "Response payload missing 'data' field"


# ============================================================================
# CLI RUNNER (For direct 'python test_mcp_server.py' execution)
# ============================================================================

def run_all_tests():
    """Run all tests sequentially for direct CLI execution"""
    print("\n🚀 Running MCP Server Test Suite (Pytest Style)\n" + "="*60)
    handler = get_handler("cli-user")
    
    tests = [
        ("Credentials", lambda: test_credentials()),
        ("Gmail API", lambda: test_gmail_api(handler)),
        ("Drive API", lambda: test_drive_api(handler)),
        ("Email Functions", lambda: test_email_functions(handler)),
        ("Drive Search", lambda: test_drive_search(handler)),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ PASS: {name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {name} - {e}")
        except Exception as e:
            print(f"❌ ERROR: {name} - {e}")
            
    print("\n" + "="*60 + f"\nSummary: {passed}/{total} tests passed\n" + "="*60)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
