"""
Configuration and settings for the MCP Server
Loads environment variables and provides configuration
"""

import os
from pathlib import Path

# === Project Paths ===
BACKEND_DIR = Path(__file__).parent.parent.resolve()
PROJECT_ROOT = BACKEND_DIR.parent

cred_setting = os.getenv("GOOGLE_CREDENTIALS_PATH", "credential.json")
if Path(cred_setting).is_absolute():
    CREDENTIALS_PATH = Path(cred_setting)
else:
    possible_paths = [
        BACKEND_DIR / cred_setting,
        Path.cwd() / cred_setting,
        Path("/app") / cred_setting
    ]
    CREDENTIALS_PATH = next((p for p in possible_paths if p.exists()), BACKEND_DIR / cred_setting)

# === Google Cloud Settings ===
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID", "")
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.readonly",
]

# === API Settings ===
GMAIL_API_TIMEOUT = int(os.getenv("GMAIL_API_TIMEOUT", "30"))
DRIVE_API_TIMEOUT = int(os.getenv("DRIVE_API_TIMEOUT", "30"))
MAX_RESULTS_DEFAULT = int(os.getenv("MAX_RESULTS_DEFAULT", "10"))
MAX_RESULTS_MAX = int(os.getenv("MAX_RESULTS_MAX", "100"))

# === Security Settings ===
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))  # Requests per second
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "1"))  # Time window in seconds
MAX_EMAIL_SIZE = int(os.getenv("MAX_EMAIL_SIZE", "52428800"))  # 50 MB
MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "256"))

# === Logging & Audit ===
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
AUDIT_LOGGING_ENABLED = os.getenv("AUDIT_LOGGING_ENABLED", "true").lower() == "true"
AUDIT_LOG_PATH = BACKEND_DIR / os.getenv("AUDIT_LOG_PATH", "logs/audit.json")

# === Application Settings ===
APP_NAME = os.getenv("APP_NAME", "Gmail-Drive-MCP-Server")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# === Feature Flags ===
ENABLE_EMAIL_SEND = os.getenv("ENABLE_EMAIL_SEND", "true").lower() == "true"
ENABLE_FILE_DOWNLOAD = os.getenv("ENABLE_FILE_DOWNLOAD", "true").lower() == "true"
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"

# === Cache Settings ===
CACHE_CREDENTIALS = os.getenv("CACHE_CREDENTIALS", "true").lower() == "true"
CREDENTIALS_CACHE_TTL = int(os.getenv("CREDENTIALS_CACHE_TTL", "3600"))  # 1 hour (Google token expiry)
FILE_METADATA_CACHE_TTL = int(os.getenv("FILE_METADATA_CACHE_TTL", "300"))  # 5 minutes

# === Retry Settings ===
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF_BASE = float(os.getenv("RETRY_BACKOFF_BASE", "1.0"))  # Exponential backoff
RETRY_BACKOFF_MAX = float(os.getenv("RETRY_BACKOFF_MAX", "32.0"))  # Max 32 seconds

# === Compliance Settings ===
GDPR_ENABLED = os.getenv("GDPR_ENABLED", "true").lower() == "true"
PII_MASKING_ENABLED = os.getenv("PII_MASKING_ENABLED", "true").lower() == "true"
DATA_RETENTION_DAYS = int(os.getenv("DATA_RETENTION_DAYS", "30"))

# === Monitoring & Metrics ===
PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "8001"))
METRICS_NAMESPACE = os.getenv("METRICS_NAMESPACE", "gmail_drive_mcp")

# === Validation ===
def validate_config():
    """Validate critical configuration settings"""
    errors = []
    
    # Check credentials file exists
    if not CREDENTIALS_PATH.exists():
        if os.getenv("ALLOW_MISSING_CREDENTIALS", "false").lower() == "true" or os.getenv("CI", "false").lower() == "true":
            print(f"⚠️  Warning: Credentials file not found at {CREDENTIALS_PATH} (CI/Test mode)")
        else:
            errors.append(f"Credentials file not found: {CREDENTIALS_PATH}")
    
    # Validate rate limits
    if RATE_LIMIT_REQUESTS <= 0:
        errors.append("RATE_LIMIT_REQUESTS must be > 0")
    
    # Validate cache TTL
    if CREDENTIALS_CACHE_TTL <= 0:
        errors.append("CREDENTIALS_CACHE_TTL must be > 0")
    
    # Validate data retention
    if DATA_RETENTION_DAYS <= 0:
        errors.append("DATA_RETENTION_DAYS must be > 0")
    
    return errors
    
    # Validate rate limits
    if RATE_LIMIT_REQUESTS <= 0:
        errors.append("RATE_LIMIT_REQUESTS must be > 0")
    
    # Validate cache TTL
    if CREDENTIALS_CACHE_TTL <= 0:
        errors.append("CREDENTIALS_CACHE_TTL must be > 0")
    
    # Validate data retention
    if DATA_RETENTION_DAYS <= 0:
        errors.append("DATA_RETENTION_DAYS must be > 0")
    
    return errors

# Run validation on import
_errors = validate_config()
if _errors and not DEBUG:
    raise ValueError("Configuration errors:\n" + "\n".join(_errors))
elif _errors:
    print("⚠️  Configuration warnings:")
    for error in _errors:
        print(f"  - {error}")
