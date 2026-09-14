"""
Gmail API Service Wrapper
Handles all Gmail API interactions with full type annotations and detailed comments.
"""

from typing import Optional, List, Dict, Any  # Type hints for function arguments and return types
from googleapiclient.discovery import build  # Google API client library builder

# Import configuration settings
from config.settings import GOOGLE_SCOPES, CREDENTIALS_PATH, GMAIL_API_TIMEOUT, CACHE_CREDENTIALS, CREDENTIALS_CACHE_TTL
import time  # Time utilities for caching logic


class GmailService:
    """Wrapper for Gmail API operations"""
    
    def __init__(self):
        """Initialize Gmail service wrapper with default state"""
        self.service = None  # Holds the built googleapiclient service instance
        self.credentials = None  # Holds the Google authentication credentials
        self.last_token_refresh = 0  # Timestamp of last credential refresh
    
    def get_credentials(self) -> Any:
        """
        Get or refresh Google credentials (supports Service Account & OAuth 2.0 Client ID)
        
        Returns:
            Google credentials instance
        """
        # Lazy import of universal auth helper to prevent circular dependencies
        from services.auth_helper import load_google_credentials
        self.credentials = load_google_credentials()  # Load or refresh Google credentials
        return self.credentials  # Return active credentials object
    
    def build_service(self):
        """
        Build and cache Gmail API service client using googleapiclient.discovery.build with explicit HTTP timeout
        """
        if self.service is None:  # Only build service if not already initialized
            import httplib2
            from google_auth_httplib2 import AuthorizedHttp
            
            credentials = self.get_credentials()  # Obtain active Google credentials
            # Construct HTTP transport with explicit socket timeout
            http = AuthorizedHttp(credentials, http=httplib2.Http(timeout=GMAIL_API_TIMEOUT))
            self.service = build(
                'gmail',  # Google API name
                'v1',     # API version
                http=http  # Pass custom HTTP transport with timeout
            )
        return self.service  # Return cached service instance
    
    def list_messages(
        self,
        query: str = "",
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        List Gmail messages matching search query.
        
        Args:
            query: Gmail search query (e.g., "is:unread", "from:sender@example.com")
            max_results: Maximum number of messages to return (capped at 100)
            
        Returns:
            Dictionary containing message IDs and total size estimates
        """
        service = self.build_service()  # Get Gmail service client
        results = service.users().messages().list(
            userId='me',  # 'me' refers to the authenticated user account
            q=query,  # Search query parameter
            maxResults=min(max_results, 100)  # Enforce hard cap of 100 results max
        ).execute()  # Execute HTTP request against Gmail API
        return results  # Return API response dictionary
    
    def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        Get full email message content by ID.
        
        Args:
            message_id: Gmail message ID string
            
        Returns:
            Full message payload including headers, body, snippet, and threadId
        """
        service = self.build_service()  # Get Gmail service client
        message = service.users().messages().get(
            userId='me',  # Authenticated account
            id=message_id,  # Specific message ID to retrieve
            format='full'  # Fetch full payload including raw headers and parts
        ).execute()  # Execute API request
        return message  # Return message object dictionary
    
    def send_message(self, message_content: str) -> Dict[str, Any]:
        """
        Send an email message via Gmail API.
        
        Args:
            message_content: Base64 urlsafe encoded MIME email message string
            
        Returns:
            Sent message metadata (id, threadId, labelIds)
        """
        service = self.build_service()  # Get Gmail service client
        message = {'raw': message_content}  # Construct raw message payload dictionary
        sent = service.users().messages().send(
            userId='me',  # Send on behalf of authenticated account
            body=message  # Raw message dictionary payload
        ).execute()  # Execute send request
        return sent  # Return sent message metadata response


# Global singleton instance for Gmail service
_gmail_service: Optional[GmailService] = None


def get_gmail_service() -> GmailService:
    """Get or create singleton Gmail service instance"""
    global _gmail_service  # Access global instance reference
    if _gmail_service is None:  # Instantiate if not created
        _gmail_service = GmailService()
    return _gmail_service  # Return singleton GmailService instance
