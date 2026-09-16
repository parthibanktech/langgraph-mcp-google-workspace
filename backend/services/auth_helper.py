"""
Universal Google Authentication Helper
Supports both Google Service Accounts and OAuth 2.0 Desktop/Web Client Credentials
"""

import json  # Standard library JSON parser to inspect credentials file format
import time  # Time module to manage token expiration caching TTL
import sys  # System utilities
from pathlib import Path  # File system path manipulation
from typing import Any  # Dynamic typing hint for returned Google credentials object

# Import Google authentication classes for Service Accounts and Authorized User tokens
from google.oauth2.service_account import Credentials as ServiceAccountCredentials  # Service account credentials parser
from google.oauth2.credentials import Credentials as UserCredentials  # OAuth 2.0 user credentials parser
from google.auth.transport.requests import Request  # HTTP request transport object to refresh expired tokens

# Import application settings configuration
from config.settings import GOOGLE_SCOPES, CREDENTIALS_PATH, BACKEND_DIR, CACHE_CREDENTIALS, CREDENTIALS_CACHE_TTL

# Global in-memory cache variables for credentials reuse
_cached_credentials = None  # Holds the initialized Google Credentials object
_last_token_refresh = 0  # Timestamp (in seconds) of when credentials were last refreshed


def load_google_credentials():
    """
    Load Google credentials supporting both Service Account key files
    and OAuth 2.0 Client Credentials files (with token caching).
    """
    global _cached_credentials, _last_token_refresh  # Access global cache variables

    # Step 1: Check if cached credentials exist and are still within valid TTL time window
    if _cached_credentials and CACHE_CREDENTIALS:
        if (time.time() - _last_token_refresh) < CREDENTIALS_CACHE_TTL:
            return _cached_credentials  # Return cached credentials without disk/network overhead

    # Step 2: Validate that credential.json exists and is a file (not a directory auto-created by Docker)
    if not CREDENTIALS_PATH.exists() or CREDENTIALS_PATH.is_dir():
        raise FileNotFoundError(f"Google credentials file ('credential.json') is missing or invalid. Please ensure your valid credential.json is placed in backend/ directory.")

    # Step 3: Open and parse the JSON file to identify the authentication type
    try:
        with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)  # Parse JSON content into Python dictionary
    except IsADirectoryError:
        raise FileNotFoundError(f"Google credentials file ('credential.json') is missing or invalid (mounted as directory). Please upload valid credential.json to backend/ directory.")

    # Step 4: Handle Service Account key format ("type": "service_account")
    if data.get("type") == "service_account":
        creds = ServiceAccountCredentials.from_service_account_file(
            str(CREDENTIALS_PATH),  # Path to service account JSON
            scopes=GOOGLE_SCOPES   # OAuth 2.0 scopes (Gmail readonly/send, Drive)
        )

    # Step 5: Handle OAuth 2.0 Client ID Credentials ("installed" or "web")
    elif "installed" in data or "web" in data:
        token_path = BACKEND_DIR / "token.json"  # Path to store authorized user access tokens
        creds = None  # Initialize credentials variable

        # Check if saved user access token file exists
        if token_path.exists():
            try:
                # Load existing user tokens from token.json
                creds = UserCredentials.from_authorized_user_file(str(token_path), GOOGLE_SCOPES)
            except Exception:
                creds = None  # Reset if token file is invalid or corrupted

        # If credentials do not exist or are invalid, refresh or trigger OAuth login flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired access token using refresh_token
                creds.refresh(Request())
            else:
                # Launch local browser OAuth consent flow
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_PATH),  # Path to OAuth 2.0 client secret JSON
                    GOOGLE_SCOPES          # Requested OAuth scopes
                )
                creds = flow.run_local_server(port=0)  # Open browser & wait for local redirect callback

            # Save newly authorized credentials to backend/token.json for future runs
            with open(token_path, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())  # Serialize user credentials to JSON
    else:
        # Raise error if JSON structure is neither Service Account nor OAuth Client ID
        raise ValueError(
            f"Unrecognized format in {CREDENTIALS_PATH}. "
            f"Must be a valid Google Service Account key or OAuth 2.0 Client Credentials JSON."
        )

    # Step 6: Store credentials in global cache and record current timestamp
    _cached_credentials = creds
    _last_token_refresh = time.time()
    return creds  # Return authenticated credentials instance
