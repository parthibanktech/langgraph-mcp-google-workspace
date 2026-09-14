"""
FastAPI REST API Server for Gmail & Google Drive MCP Server
Provides interactive Swagger UI documentation at http://localhost:8000/docs
"""

import sys
import json
import os
from pathlib import Path
from typing import List, Optional

# Ensure UTF-8 output encoding for Windows console compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Add backend directory and workspace root to sys.path
backend_dir = Path(__file__).parent
root_dir = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi import FastAPI, HTTPException, Query, Path as PathParam, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from handlers.tool_handler import get_handler

# Create FastAPI App with Swagger UI metadata
app = FastAPI(
    title="Gmail & Google Drive MCP REST API",
    description="Interactive Swagger API documentation for Gmail and Google Drive MCP Tools by Parthiban K.",
    version="1.0.0",
    docs_url="/docs",      # Interactive Swagger UI URL
    redoc_url="/redoc",    # ReDoc Documentation URL
    contact={
        "name": "Parthiban K",
        "email": "parthibankwarrior@gmail.com"
    }
)

# Enable CORS for frontend cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# PYDANTIC REQUEST SCHEMAS
# ============================================================================

class ListEmailsRequest(BaseModel):
    query: str = Field(default="is:unread", description="Gmail search query (e.g., 'is:unread', 'from:user@example.com')")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of emails to return (1-100)")

class SendEmailRequest(BaseModel):
    to: List[str] = Field(..., description="List of recipient email addresses")
    subject: str = Field(..., max_length=255, description="Email subject line")
    body: str = Field(..., description="Email body content")
    cc: Optional[List[str]] = Field(default=None, description="Optional CC recipient email addresses")
    bcc: Optional[List[str]] = Field(default=None, description="Optional BCC recipient email addresses")

class ListDriveFilesRequest(BaseModel):
    query: str = Field(default="", description="Search query string for Drive files")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of files to return (1-100)")
    file_type: str = Field(default="", description="Optional MIME type filter (e.g., 'application/vnd.google-apps.document')")

class SearchDriveRequest(BaseModel):
    keyword: str = Field(..., description="Keyword string to search across Drive file names and content")
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of results to return (1-100)")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User prompt message")


# ============================================================================
# API ENDPOINTS (EXPOSED IN SWAGGER UI)
# ============================================================================

@app.get("/", tags=["Health & Status"])
def root():
    """Root Endpoint - Directs users to Swagger UI"""
    return {
        "message": "Gmail & Google Drive MCP API Server is Running",
        "swagger_ui": "http://localhost:8000/docs",
        "redoc_ui": "http://localhost:8000/redoc"
    }

@app.get("/health", tags=["Health & Status"])
@app.get("/api/health", tags=["Health & Status"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Gmail & Google Drive MCP REST API"}


# --- AI AGENT CHAT ENDPOINT ---

@app.post("/api/chat", tags=["AI Agent"])
def chat_endpoint(request: ChatRequest):
    """
    Chat with the Gmail & Google Drive MCP Agent.
    """
    handler = get_handler("react-frontend-user")
    prompt = request.message.strip()
    prompt_lower = prompt.lower()
    
    tools_used = []
    response_text = ""
    data_list = []
    
    try:
        if "email" in prompt_lower or "inbox" in prompt_lower or "unread" in prompt_lower or "mail" in prompt_lower:
            query = "is:unread" if "unread" in prompt_lower else ""
            res_str = handler.list_emails(query=query, max_results=5)
            parsed = json.loads(res_str)
            is_ok = parsed.get("success", False) or parsed.get("status") == "success"
            tools_used.append({"name": "list_emails", "query": query, "success": is_ok})
            
            if is_ok and isinstance(parsed.get("data"), dict):
                data_list = parsed["data"].get("emails", [])
                count = len(data_list)
                response_text = f"Found {count} email(s) in inbox matching '{query or 'all'}'."
            elif is_ok and isinstance(parsed.get("data"), list):
                data_list = parsed["data"]
                count = len(data_list)
                response_text = f"Found {count} email(s) in inbox matching '{query or 'all'}'."
            else:
                response_text = f"Gmail search result: {parsed.get('error') or parsed.get('message') or 'No emails found.'}"
                
        elif "drive" in prompt_lower or "file" in prompt_lower or "doc" in prompt_lower or "search" in prompt_lower:
            kw = prompt_lower.replace("drive", "").replace("file", "").replace("search", "").strip() or "doc"
            res_str = handler.search_drive(keyword=kw, max_results=5)
            parsed = json.loads(res_str)
            is_ok = parsed.get("success", False) or parsed.get("status") == "success"
            tools_used.append({"name": "search_drive", "keyword": kw, "success": is_ok})
            
            if is_ok and isinstance(parsed.get("data"), dict):
                data_list = parsed["data"].get("files", [])
                count = len(data_list)
                response_text = f"Found {count} Google Drive file(s) matching '{kw}'."
            elif is_ok and isinstance(parsed.get("data"), list):
                data_list = parsed["data"]
                count = len(data_list)
                response_text = f"Found {count} Google Drive file(s) matching '{kw}'."
            else:
                response_text = f"Google Drive search result: {parsed.get('error') or parsed.get('message') or 'No files found.'}"
                
        else:
            response_text = f"I am your Gmail & Google Drive MCP AI Assistant! You can ask me to list unread emails, search files in Drive, read messages, or send emails."
            
        return {
            "status": "success",
            "message": response_text,
            "tools_used": tools_used,
            "data": data_list
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Agent processing failed: {str(e)}",
            "tools_used": tools_used,
            "data": []
        }

@app.get("/api/logs", tags=["Health & Status"])
def get_audit_logs():
    """
    Retrieve audit log activity entries.
    """
    log_path = Path(__file__).parent / "logs" / "audit.log"
    logs = []
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines[-50:]):
                    if line.strip():
                        try:
                            logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            logs.append({"raw": line.strip()})
        except Exception as e:
            logs.append({"error": f"Failed to read log file: {str(e)}"})
    return {"logs": logs, "total": len(logs)}


# --- GMAIL ENDPOINTS ---

@app.post("/api/gmail/list", tags=["Gmail Tools"])
def list_emails_endpoint(request: ListEmailsRequest):
    """
    List and search emails in Gmail inbox.
    """
    handler = get_handler("swagger-user")
    result_json = handler.list_emails(query=request.query, max_results=request.max_results)
    return json.loads(result_json)

@app.get("/api/gmail/read/{email_id}", tags=["Gmail Tools"])
def read_email_endpoint(email_id: str = PathParam(..., description="Gmail message ID")):
    """
    Read full email content by message ID.
    """
    handler = get_handler("swagger-user")
    result_json = handler.read_email(email_id=email_id)
    return json.loads(result_json)

@app.post("/api/gmail/send", tags=["Gmail Tools"])
def send_email_endpoint(request: SendEmailRequest):
    """
    Send an email via Gmail API.
    """
    handler = get_handler("swagger-user")
    result_json = handler.send_email(
        to=request.to,
        subject=request.subject,
        body=request.body,
        cc=request.cc,
        bcc=request.bcc
    )
    return json.loads(result_json)


# --- GOOGLE DRIVE ENDPOINTS ---

@app.post("/api/drive/files", tags=["Google Drive Tools"])
def list_drive_files_endpoint(request: ListDriveFilesRequest):
    """
    List files in Google Drive with optional filtering.
    """
    handler = get_handler("swagger-user")
    result_json = handler.list_drive_files(query=request.query, max_results=request.max_results, file_type=request.file_type)
    return json.loads(result_json)

@app.get("/api/drive/file/{file_id}", tags=["Google Drive Tools"])
def get_file_info_endpoint(file_id: str = PathParam(..., description="Google Drive File ID")):
    """
    Get detailed file metadata by File ID.
    """
    handler = get_handler("swagger-user")
    result_json = handler.get_file_info(file_id=file_id)
    return json.loads(result_json)

@app.post("/api/drive/search", tags=["Google Drive Tools"])
def search_drive_endpoint(request: SearchDriveRequest):
    """
    Search Google Drive files by keyword.
    """
    handler = get_handler("swagger-user")
    result_json = handler.search_drive(keyword=request.keyword, max_results=request.max_results)
    return json.loads(result_json)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI Server with Swagger UI at http://localhost:8000/docs...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
