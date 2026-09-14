"""
Gmail & Google Drive MCP Server (Refactored with Layered Architecture)
Exposes 6 tools to interact with Gmail and Google Drive through the Model Context Protocol

Uses layered architecture:
├── config/ - Configuration and settings
├── models/ - Data schemas
├── services/ - API wrappers (Gmail, Drive)
├── security/ - Validation, rate limiting, audit logging
└── handlers/ - Business logic and tool routing
"""

import sys
import json
import logging
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ToolError

# Import from layered architecture
from config.settings import APP_NAME, APP_VERSION, DEBUG
from handlers.tool_handler import get_handler
from security.audit_logger import get_audit_logger

# Set up logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP(APP_NAME, version=APP_VERSION)

# Initialize audit logger
audit_logger = get_audit_logger()


# ============================================================================
# GMAIL TOOLS
# ============================================================================

@mcp.tool()
def list_emails(query: str = "", max_results: int = 10) -> str:
    """
    List Gmail emails with optional filtering
    
    Args:
        query: Gmail search query (e.g., "is:unread", "from:sender@example.com", "subject:urgent")
        max_results: Maximum number of results to return (1-100, default 10)
    
    Returns:
        JSON string with email list and metadata
    
    Examples:
        - "is:unread" - List unread emails
        - "from:boss@example.com" - List emails from specific sender
        - "subject:project" - Search by subject
        - "is:starred" - List starred emails
        - "in:inbox has:attachment" - Emails with attachments
    """
    handler = get_handler("default")
    return handler.list_emails(query, max_results)


@mcp.tool()
def read_email(email_id: str) -> str:
    """
    Read full email content
    
    Args:
        email_id: Gmail message ID (from list_emails result)
    
    Returns:
        JSON string with email subject, from, to, date, and body content
    """
    handler = get_handler("default")
    return handler.read_email(email_id)


@mcp.tool()
def send_email(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None
) -> str:
    """
    Send an email via Gmail
    
    Args:
        to: List of recipient email addresses (required)
        subject: Email subject line (max 255 characters)
        body: Email body content
        cc: Optional list of CC recipients
        bcc: Optional list of BCC recipients
    
    Returns:
        JSON string with sent message ID and status
    
    Note:
        - All recipients are validated before sending
        - Maximum 100 recipients per email
        - Subject limited to 255 characters
    """
    handler = get_handler("default")
    return handler.send_email(to, subject, body, cc, bcc)


# ============================================================================
# GOOGLE DRIVE TOOLS
# ============================================================================

@mcp.tool()
def list_drive_files(query: str = "", max_results: int = 10, file_type: str = "") -> str:
    """
    List Google Drive files with optional filtering
    
    Args:
        query: Search query (e.g., "name contains 'project'", "trashed=false")
        max_results: Maximum number of results (1-100, default 10)
        file_type: Filter by MIME type (e.g., "application/vnd.google-apps.document")
    
    Returns:
        JSON string with file list and metadata (name, type, size, created date, etc.)
    
    Common MIME Types:
        - "application/vnd.google-apps.document" - Google Docs
        - "application/vnd.google-apps.spreadsheet" - Google Sheets
        - "application/vnd.google-apps.presentation" - Google Slides
        - "application/vnd.google-apps.folder" - Folders
        - "application/pdf" - PDFs
        - "image/jpeg" - JPEG images
    """
    handler = get_handler("default")
    return handler.list_drive_files(query, max_results, file_type)


@mcp.tool()
def get_file_info(file_id: str) -> str:
    """
    Get detailed information about a Google Drive file
    
    Args:
        file_id: Google Drive file ID
    
    Returns:
        JSON string with file metadata (name, type, size, owners, sharing status, link)
    """
    handler = get_handler("default")
    return handler.get_file_info(file_id)


@mcp.tool()
def search_drive(keyword: str, max_results: int = 10) -> str:
    """
    Search Google Drive files by keyword
    
    Args:
        keyword: Search keyword (searches in file names and content)
        max_results: Maximum number of results (1-100, default 10)
    
    Returns:
        JSON string with matching files
    """
    handler = get_handler("default")
    return handler.search_drive(keyword, max_results)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@mcp.tool()
def health_check() -> str:
    """Check if MCP server is operational and all services are available"""
    return json.dumps({
        "status": "healthy",
        "app": APP_NAME,
        "version": APP_VERSION,
        "tools": ["list_emails", "read_email", "send_email", "list_drive_files", "get_file_info", "search_drive"]
    })


# ============================================================================
# SERVER LIFECYCLE
# ============================================================================

async def startup():
    """Initialize server resources on startup"""
    logger.info(f"🚀 Starting {APP_NAME} v{APP_VERSION}")
    logger.info("📧 Gmail & Drive tools initialized")
    logger.info("Available tools: list_emails, read_email, send_email, list_drive_files, get_file_info, search_drive, health_check")
    if DEBUG:
        logger.debug("🔧 Debug mode enabled - detailed logging active")


async def shutdown():
    """Clean up resources on shutdown"""
    logger.info(f"⏹️  Shutting down {APP_NAME}")


# Register lifecycle hooks
mcp.on_startup(startup)
mcp.on_shutdown(shutdown)


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting MCP Server...")
    mcp.run(transport="stdio")
