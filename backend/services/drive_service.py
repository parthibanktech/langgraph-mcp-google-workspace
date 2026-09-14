"""
Google Drive API Service Wrapper
Handles all Google Drive API interactions with full type annotations and detailed comments.
"""

from typing import Optional, List, Dict, Any  # Type hints for function arguments and return values
from googleapiclient.discovery import build  # Google API client library builder

# Import configuration settings
from config.settings import GOOGLE_SCOPES, CREDENTIALS_PATH, DRIVE_API_TIMEOUT, CACHE_CREDENTIALS, CREDENTIALS_CACHE_TTL
import time  # Time utilities for caching logic


class DriveService:
    """Wrapper for Google Drive API operations"""
    
    def __init__(self):
        """Initialize Google Drive service wrapper with default state"""
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
        Build and cache Google Drive API service client using googleapiclient.discovery.build with explicit HTTP timeout
        """
        if self.service is None:  # Only build service if not already initialized
            import httplib2
            from google_auth_httplib2 import AuthorizedHttp
            
            credentials = self.get_credentials()  # Obtain active Google credentials
            # Construct HTTP transport with explicit socket timeout
            http = AuthorizedHttp(credentials, http=httplib2.Http(timeout=DRIVE_API_TIMEOUT))
            self.service = build(
                'drive',  # Google API name
                'v3',     # Drive API version v3
                http=http  # Pass custom HTTP transport with timeout
            )
        return self.service  # Return cached service instance
    
    def list_files(
        self,
        query: str = "",
        max_results: int = 10,
        file_type: str = ""
    ) -> Dict[str, Any]:
        """
        List Google Drive files with optional filtering and MIME type restriction.
        
        Args:
            query: Search query string (e.g. "name contains 'project'")
            max_results: Maximum number of files to return (capped at 100)
            file_type: MIME type string filter (e.g., "application/vnd.google-apps.document")
            
        Returns:
            Dictionary containing list of files with metadata (id, name, mimeType, etc.)
        """
        service = self.build_service()  # Get Drive service client
        
        # Build composite query string
        full_query = ""
        if query:
            # Auto-format plain keyword queries into valid Google Drive 'name contains' clauses
            if not any(op in query.lower() for op in ["contains", "=", "!=", " in ", "has"]):
                full_query = f"name contains '{query}'"
            else:
                full_query = query

        if file_type:
            if full_query:
                full_query += f" and mimeType = '{file_type}'"
            else:
                full_query = f"mimeType = '{file_type}'"
        
        # Execute Google Drive files.list API request
        results = service.files().list(
            q=full_query if full_query else None,  # Query string filter
            spaces='drive',  # Search in user's main Google Drive space
            fields='files(id, name, mimeType, createdTime, modifiedTime, size, owners, shared)',  # Select fields to return
            pageSize=min(max_results, 100)  # Hard cap results to max 100
        ).execute()  # Execute API request
        return results  # Return search result dictionary
    
    def get_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get detailed metadata for a specific Google Drive file by ID.
        
        Args:
            file_id: Google Drive file ID string
            
        Returns:
            Dictionary containing detailed file metadata (owner, permissions, webViewLink, etc.)
        """
        service = self.build_service()  # Get Drive service client
        file = service.files().get(
            fileId=file_id,  # Target file ID
            fields='id, name, mimeType, createdTime, modifiedTime, size, owners, shared, webViewLink'  # Fields to fetch
        ).execute()  # Execute API request
        return file  # Return file metadata dictionary
    
    def search_files(self, keyword: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search Google Drive files by keyword matching name or file content.
        
        Args:
            keyword: Keyword string to search for
            max_results: Maximum number of search results to return
            
        Returns:
            Dictionary containing matching search files
        """
        service = self.build_service()  # Get Drive service client
        
        # Construct fullText search query
        query = f"fullText contains '{keyword}'"
        
        results = service.files().list(
            q=query,  # fullText query search
            spaces='drive',  # User drive space
            fields='files(id, name, mimeType, createdTime, modifiedTime)',  # Result fields
            pageSize=min(max_results, 100)  # Hard cap max 100
        ).execute()  # Execute search API request
        return results  # Return search response dictionary


# Global singleton instance for Drive service
_drive_service: Optional[DriveService] = None


def get_drive_service() -> DriveService:
    """Get or create singleton Drive service instance"""
    global _drive_service  # Access global instance reference
    if _drive_service is None:  # Instantiate if not created
        _drive_service = DriveService()
    return _drive_service  # Return singleton DriveService instance
