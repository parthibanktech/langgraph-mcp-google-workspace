"""
MCP Tool handlers - Routes tool calls to services
Implements business logic and error handling
"""

import json
import base64
import time
from email.mime.text import MIMEText
from typing import List, Optional, Dict, Any
from datetime import datetime

from services.gmail_service import get_gmail_service
from services.drive_service import get_drive_service
from security.validators import (
    validate_list_emails_params,
    validate_read_email_params,
    validate_send_email_params,
    validate_drive_search_params,
    sanitize_query
)
from security.rate_limiter import allow_request, RateLimitError
from security.audit_logger import log_tool_execution, log_security_event
from models.schemas import EmailData, DriveFile, ToolResult


class ToolHandler:
    """Base handler for all MCP tools"""
    
    def __init__(self, user_id: str = "default"):
        """
        Initialize handler
        
        Args:
            user_id: User executing the tool
        """
        self.user_id = user_id
        self.gmail_service = get_gmail_service()
        self.drive_service = get_drive_service()
    
    def _execute_with_rate_limit(self, tool_name: str, func, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute function with rate limiting and error handling
        
        Args:
            tool_name: Name of the tool
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Tool result dictionary
        """
        start_time = time.time()
        
        try:
            # Check rate limit
            allow_request(self.user_id)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log success
            log_tool_execution(
                user_id=self.user_id,
                tool_name=tool_name,
                status="success",
                execution_time_ms=execution_time_ms
            )
            
            return {
                "success": True,
                "tool": tool_name,
                "timestamp": datetime.utcnow().isoformat(),
                "data": result,
                "execution_time_ms": execution_time_ms
            }
        
        except RateLimitError as e:
            # Log rate limit event
            log_security_event(
                user_id=self.user_id,
                event_type="rate_limit_exceeded",
                severity="medium",
                message=str(e)
            )
            return {
                "success": False,
                "error": "Rate limit exceeded",
                "error_code": "RATE_LIMIT"
            }
        
        except Exception as e:
            # Log error
            execution_time_ms = int((time.time() - start_time) * 1000)
            log_tool_execution(
                user_id=self.user_id,
                tool_name=tool_name,
                status="failure",
                error_message=str(e),
                execution_time_ms=execution_time_ms
            )
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "EXECUTION_ERROR"
            }
    
    def list_emails(self, query: str = "", max_results: int = 10) -> str:
        """List emails"""
        # Validate parameters
        valid, error = validate_list_emails_params(query, max_results)
        if not valid:
            log_security_event(
                user_id=self.user_id,
                event_type="validation_error",
                severity="low",
                message=f"Invalid parameters for list_emails: {error}"
            )
            return json.dumps({"success": False, "error": error, "error_code": "VALIDATION_ERROR"})
        
        # Sanitize query
        query = sanitize_query(query)
        
        def _execute():
            results = self.gmail_service.list_messages(query, max_results)
            messages = results.get('messages', [])
            
            detailed_emails = []
            for m in messages:
                try:
                    msg_detail = self.gmail_service.get_message(m['id'])
                    headers = msg_detail.get('payload', {}).get('headers', [])
                    header_dict = {h['name']: h['value'] for h in headers}
                    detailed_emails.append({
                        "id": m['id'],
                        "threadId": m['threadId'],
                        "subject": header_dict.get('Subject', '(No Subject)'),
                        "from": header_dict.get('From', ''),
                        "date": header_dict.get('Date', ''),
                        "snippet": msg_detail.get('snippet', '')
                    })
                except Exception:
                    detailed_emails.append({
                        "id": m['id'],
                        "threadId": m['threadId']
                    })
            
            return {
                "count": len(detailed_emails),
                "total_estimate": results.get('resultSizeEstimate', 0),
                "emails": detailed_emails
            }
        
        result = self._execute_with_rate_limit("list_emails", _execute)
        return json.dumps(result)
    
    def read_email(self, email_id: str) -> str:
        """Read email content"""
        # Validate parameters
        valid, error = validate_read_email_params(email_id)
        if not valid:
            return json.dumps({"success": False, "error": error, "error_code": "VALIDATION_ERROR"})
        
        def _execute():
            target_id = email_id
            # If email_id contains '@', resolve it to the latest message ID from or to that address
            if "@" in email_id:
                search_res = self.gmail_service.list_messages(f"from:{email_id} OR to:{email_id}", max_results=1)
                msgs = search_res.get('messages', [])
                if not msgs:
                    raise ValueError(f"No emails found from or to address: {email_id}")
                target_id = msgs[0]['id']
            
            message = self.gmail_service.get_message(target_id)
            
            headers = message['payload'].get('headers', [])
            header_dict = {h['name']: h['value'] for h in headers}
            
            # Extract body
            body = ""
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                data = message['payload']['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            return {
                "id": message['id'],
                "threadId": message['threadId'],
                "subject": header_dict.get('Subject', ''),
                "from": header_dict.get('From', ''),
                "to": header_dict.get('To', ''),
                "date": header_dict.get('Date', ''),
                "body": body[:500],  # Limit to 500 chars for preview
                "snippet": message.get('snippet', '')
            }
        
        result = self._execute_with_rate_limit("read_email", _execute)
        return json.dumps(result)
    
    def send_email(self, to: List[str], subject: str, body: str, cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None) -> str:
        """Send email"""
        # Validate parameters
        valid, error = validate_send_email_params(to, subject, body, cc, bcc)
        if not valid:
            return json.dumps({"success": False, "error": error, "error_code": "VALIDATION_ERROR"})
        
        def _execute():
            # Create email message
            message = MIMEText(body)
            message['to'] = ', '.join(to)
            message['subject'] = subject
            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            sent = self.gmail_service.send_message(raw_message)
            
            return {
                "messageId": sent['id'],
                "threadId": sent['threadId'],
                "to": to,
                "subject": subject,
                "status": "sent"
            }
        
        result = self._execute_with_rate_limit("send_email", _execute)
        return json.dumps(result)
    
    def list_drive_files(self, query: str = "", max_results: int = 10, file_type: str = "") -> str:
        """List Drive files"""
        # Validate parameters
        valid, error = validate_drive_search_params(query, max_results)
        if not valid:
            return json.dumps({"success": False, "error": error, "error_code": "VALIDATION_ERROR"})
        
        # Sanitize query
        query = sanitize_query(query)
        
        def _execute():
            results = self.drive_service.list_files(query, max_results, file_type)
            files = results.get('files', [])
            
            return {
                "count": len(files),
                "files": [
                    {
                        "id": f['id'],
                        "name": f['name'],
                        "mimeType": f['mimeType'],
                        "createdTime": f.get('createdTime'),
                        "modifiedTime": f.get('modifiedTime'),
                        "size": f.get('size')
                    }
                    for f in files
                ]
            }
        
        result = self._execute_with_rate_limit("list_drive_files", _execute)
        return json.dumps(result)
    
    def get_file_info(self, file_id: str) -> str:
        """Get Drive file info"""
        # Validate parameters
        valid, error = validate_read_email_params(file_id)  # Same validation
        if not valid:
            return json.dumps({"success": False, "error": error, "error_code": "VALIDATION_ERROR"})
        
        def _execute():
            file = self.drive_service.get_file(file_id)
            
            return {
                "id": file['id'],
                "name": file['name'],
                "mimeType": file['mimeType'],
                "createdTime": file.get('createdTime'),
                "modifiedTime": file.get('modifiedTime'),
                "size": file.get('size'),
                "webViewLink": file.get('webViewLink'),
                "shared": file.get('shared', False)
            }
        
        result = self._execute_with_rate_limit("get_file_info", _execute)
        return json.dumps(result)
    
    def search_drive(self, keyword: str, max_results: int = 10) -> str:
        """Search Drive files"""
        # Validate parameters
        valid, error = validate_drive_search_params(keyword, max_results)
        if not valid:
            return json.dumps({"success": False, "error": error, "error_code": "VALIDATION_ERROR"})
        
        # Sanitize keyword
        keyword = sanitize_query(keyword)
        
        def _execute():
            results = self.drive_service.search_files(keyword, max_results)
            files = results.get('files', [])
            
            return {
                "count": len(files),
                "keyword": keyword,
                "files": [
                    {
                        "id": f['id'],
                        "name": f['name'],
                        "mimeType": f['mimeType']
                    }
                    for f in files
                ]
            }
        
        result = self._execute_with_rate_limit("search_drive", _execute)
        return json.dumps(result)


# Global handler instance
_handler: Optional[ToolHandler] = None


def get_handler(user_id: str = "default") -> ToolHandler:
    """Get or create handler"""
    global _handler
    if _handler is None or _handler.user_id != user_id:
        _handler = ToolHandler(user_id)
    return _handler
