"""
Audit logging for compliance and security monitoring
Logs all API calls, errors, and security events
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from config.settings import AUDIT_LOG_PATH, AUDIT_LOGGING_ENABLED, DEBUG, PII_MASKING_ENABLED
from models.schemas import AuditLog


class AuditLogger:
    """
    Centralized audit logging for compliance
    Logs all tool executions, errors, and security events
    """
    
    def __init__(self, log_path: Path = AUDIT_LOG_PATH):
        """
        Initialize audit logger
        
        Args:
            log_path: Path to audit log file
        """
        self.log_path = log_path
        self.enabled = AUDIT_LOGGING_ENABLED
        
        # Create logs directory if it doesn't exist
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set up file logger
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        handler = logging.FileHandler(self.log_path)
        formatter = logging.Formatter('%(message)s')  # Just the JSON
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _mask_pii(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask personally identifiable information (PII)
        
        Args:
            data: Data dictionary to mask
            
        Returns:
            Masked data dictionary
        """
        if not PII_MASKING_ENABLED:
            return data
        
        masked = data.copy()
        
        # Mask email addresses
        for key in ['email', 'to', 'from', 'sender', 'recipient', 'recipients']:
            if key in masked and isinstance(masked[key], str):
                masked[key] = self._mask_email(masked[key])
            elif key in masked and isinstance(masked[key], list):
                masked[key] = [self._mask_email(email) if isinstance(email, str) else email 
                              for email in masked[key]]
        
        # Mask file names that might contain PII
        for key in ['name', 'filename', 'subject']:
            if key in masked and isinstance(masked[key], str):
                # Keep only first 3 chars of file name
                if len(masked[key]) > 3:
                    masked[key] = masked[key][:3] + "***"
        
        return masked
    
    @staticmethod
    def _mask_email(email: str) -> str:
        """Mask email address"""
        if '@' not in email:
            return email
        
        parts = email.split('@')
        local = parts[0]
        domain = parts[1]
        
        # Show only first character and domain
        if len(local) > 1:
            return f"{local[0]}***@{domain}"
        return f"***@{domain}"
    
    def log_tool_execution(
        self,
        user_id: str,
        tool_name: str,
        status: str,
        request_args: Optional[Dict] = None,
        response_status: Optional[str] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """
        Log tool execution
        
        Args:
            user_id: User who made the request
            tool_name: Name of the tool called
            status: "success" or "failure"
            request_args: Arguments passed to tool
            response_status: HTTP status code
            error_message: Error message if failed
            execution_time_ms: Execution time in milliseconds
            ip_address: Source IP address
        """
        if not self.enabled:
            return
        
        # Create audit log entry
        log_entry = AuditLog(
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            action="tool_execution",
            tool_name=tool_name,
            status=status,
            request_args=self._mask_pii(request_args) if request_args else None,
            response_status=response_status,
            error_message=error_message,
            ip_address=ip_address,
            execution_time_ms=execution_time_ms
        )
        
        # Write to log
        self.logger.info(log_entry.to_json())
    
    def log_security_event(
        self,
        user_id: str,
        event_type: str,
        severity: str,  # "low", "medium", "high", "critical"
        message: str,
        ip_address: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> None:
        """
        Log security event (rate limit, validation error, etc.)
        
        Args:
            user_id: User involved
            event_type: Type of security event
            severity: Severity level
            message: Event message
            ip_address: Source IP address
            details: Additional details
        """
        if not self.enabled:
            return
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "ip_address": ip_address,
            "details": self._mask_pii(details) if details else None
        }
        
        self.logger.warning(json.dumps(log_entry))
    
    def log_authentication_attempt(
        self,
        user_id: str,
        success: bool,
        ip_address: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """
        Log authentication attempt
        
        Args:
            user_id: User attempting to authenticate
            success: Whether authentication succeeded
            ip_address: Source IP address
            reason: Reason for failure (if failed)
        """
        if not self.enabled:
            return
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "authentication",
            "user_id": user_id,
            "success": success,
            "ip_address": ip_address,
            "failure_reason": reason if not success else None
        }
        
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, json.dumps(log_entry))
    
    def log_error(
        self,
        tool_name: str,
        error_type: str,
        error_message: str,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log application error
        
        Args:
            tool_name: Tool that errored
            error_type: Type of error
            error_message: Error message
            user_id: User if applicable
        """
        if not self.enabled:
            return
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": "error",
            "tool_name": tool_name,
            "error_type": error_type,
            "error_message": error_message if DEBUG else "See server logs",
            "user_id": user_id
        }
        
        self.logger.error(json.dumps(log_entry))


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create global audit logger"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def log_tool_execution(
    user_id: str,
    tool_name: str,
    status: str,
    **kwargs
) -> None:
    """Log tool execution"""
    get_audit_logger().log_tool_execution(user_id, tool_name, status, **kwargs)


def log_security_event(
    user_id: str,
    event_type: str,
    severity: str,
    message: str,
    **kwargs
) -> None:
    """Log security event"""
    get_audit_logger().log_security_event(user_id, event_type, severity, message, **kwargs)
