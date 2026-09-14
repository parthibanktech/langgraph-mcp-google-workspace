"""
Data schemas and models for Gmail and Drive data
"""

from typing import Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class EmailData:
    """Represents a Gmail email"""
    email_id: str
    thread_id: str
    subject: Optional[str] = None
    sender: Optional[str] = None
    date: Optional[str] = None
    snippet: Optional[str] = None
    labels: List[str] = None
    is_unread: bool = False
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_dict(cls, data: dict) -> "EmailData":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class DriveFile:
    """Represents a Google Drive file"""
    file_id: str
    name: str
    mime_type: str
    created_time: Optional[str] = None
    modified_time: Optional[str] = None
    size: Optional[int] = None
    owners: List[str] = None
    shared: bool = False
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_dict(cls, data: dict) -> "DriveFile":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class ToolResult:
    """Standardized tool execution result"""
    success: bool
    tool_name: str
    timestamp: str
    data: Optional[dict] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    execution_time_ms: Optional[int] = None
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self))


@dataclass
class AuditLog:
    """Audit log entry for compliance and security"""
    timestamp: str
    user_id: str
    action: str
    tool_name: str
    status: str  # "success" or "failure"
    request_args: Optional[dict] = None
    response_status: Optional[str] = None
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    execution_time_ms: Optional[int] = None
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self))
