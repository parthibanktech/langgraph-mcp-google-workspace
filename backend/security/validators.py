"""
Input validation for security
Prevents injection attacks and validates parameters
"""

import re
from typing import Optional, List
from config.settings import MAX_EMAIL_SIZE, MAX_QUERY_LENGTH


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_email_address(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    if not email or len(email) > 254:
        return False
    
    # RFC 5322 simplified regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_file_id(file_id: str) -> bool:
    """
    Validate Google Drive file ID format
    
    Args:
        file_id: File ID to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not file_id or len(file_id) > 100:
        return False
    
    # Google Drive file IDs are typically alphanumeric with - and _
    pattern = r'^[a-zA-Z0-9_-]{1,100}$'
    return bool(re.match(pattern, file_id))


def validate_query(query: str, max_length: int = MAX_QUERY_LENGTH) -> bool:
    """
    Validate search query
    Prevents query injection and overly complex queries
    
    Args:
        query: Search query to validate
        max_length: Maximum allowed query length
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(query, str):
        return False
    
    if len(query) > max_length:
        return False
    
    # Block dangerous characters that could be used for injection
    dangerous_patterns = [
        r'[<>"`]',  # HTML/template injection
        r'\$\{',     # Template injection
        r'__proto__', # Prototype pollution
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query):
            return False
    
    return True


def validate_email_body(body: str, max_size: int = MAX_EMAIL_SIZE) -> bool:
    """
    Validate email body content
    
    Args:
        body: Email body to validate
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(body, str):
        return False
    
    if len(body.encode('utf-8')) > max_size:
        return False
    
    return True


def validate_recipient_list(recipients: List[str]) -> bool:
    """
    Validate list of email recipients
    
    Args:
        recipients: List of email addresses
        
    Returns:
        True if all valid, False otherwise
    """
    if not isinstance(recipients, list):
        return False
    
    if len(recipients) == 0:
        return False
    
    if len(recipients) > 100:  # Limit recipients per email
        return False
    
    return all(validate_email_address(email) for email in recipients)


def sanitize_query(query: str) -> str:
    """
    Sanitize query by removing potentially harmful characters
    
    Args:
        query: Query to sanitize
        
    Returns:
        Sanitized query
    """
    # Remove leading/trailing whitespace
    query = query.strip()
    
    # Replace multiple spaces with single space
    query = re.sub(r'\s+', ' ', query)
    
    # Remove control characters
    query = re.sub(r'[\x00-\x1F\x7F]', '', query)
    
    return query


# Validation functions for all parameters
def validate_list_emails_params(query: str, max_results: int) -> tuple[bool, Optional[str]]:
    """Validate parameters for list_emails"""
    if not isinstance(query, str):
        return False, "query must be a string"
    
    if not validate_query(query):
        return False, f"Invalid query format (max {MAX_QUERY_LENGTH} chars)"
    
    if not isinstance(max_results, int) or max_results <= 0 or max_results > 100:
        return False, "max_results must be integer between 1 and 100"
    
    return True, None


def validate_read_email_params(email_id: str) -> tuple[bool, Optional[str]]:
    """Validate parameters for read_email (supports Hex Message ID or Email Address)"""
    if not email_id or not isinstance(email_id, str):
        return False, "email_id must be a non-empty string"
    if len(email_id) > 254:
        return False, "email_id parameter too long"
    
    # Allow hexadecimal message IDs, file IDs, and email addresses (letters, numbers, @, ., -, _)
    pattern = r'^[a-zA-Z0-9._%+-@]{1,254}$'
    if not bool(re.match(pattern, email_id)):
        return False, "Invalid email ID format"
    
    return True, None


def validate_send_email_params(
    to: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
) -> tuple[bool, Optional[str]]:
    """Validate parameters for send_email"""
    # Validate recipients
    if not validate_recipient_list(to):
        return False, "Invalid recipient list"
    
    if cc and not validate_recipient_list(cc):
        return False, "Invalid CC list"
    
    if bcc and not validate_recipient_list(bcc):
        return False, "Invalid BCC list"
    
    # Validate subject
    if not isinstance(subject, str) or len(subject) == 0 or len(subject) > 255:
        return False, "Subject must be 1-255 characters"
    
    # Validate body
    if not validate_email_body(body):
        return False, f"Email body too large (max {MAX_EMAIL_SIZE} bytes)"
    
    return True, None


def validate_drive_search_params(keyword: str, max_results: int) -> tuple[bool, Optional[str]]:
    """Validate parameters for search_drive"""
    if not isinstance(keyword, str):
        return False, "keyword must be a string"
    
    if not validate_query(keyword):
        return False, f"Invalid search keyword (max {MAX_QUERY_LENGTH} chars)"
    
    if not isinstance(max_results, int) or max_results <= 0 or max_results > 100:
        return False, "max_results must be integer between 1 and 100"
    
    return True, None
