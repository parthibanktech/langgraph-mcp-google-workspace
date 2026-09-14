# ⚡ Quick Reference: Backend Architecture

## 📁 Where to Make Changes

| Change Type | File | Line |
|-------------|------|------|
| **Add new tool** | `handlers/tool_handler.py` | - |
| **Change rate limit** | `config/settings.py` | RATE_LIMIT_REQUESTS |
| **Add validation rule** | `security/validators.py` | - |
| **Change MCP tool routing** | `mcp_server_refactored.py` | ~80 |
| **Add new Google service** | `services/new_service.py` | - |
| **Change log format** | `security/audit_logger.py` | - |

---

## 🔧 Common Tasks

### **Add a New Tool (30 seconds)**

1. **Handler Method** (`backend/handlers/tool_handler.py`):
```python
def my_tool(self, param: str) -> str:
    def _execute():
        # Your logic
        result = self.gmail_service.some_method(param)
        return {"success": True, "data": result}
    
    result = self._execute_with_rate_limit("my_tool", _execute)
    return json.dumps(result)
```

2. **MCP Tool** (`backend/mcp_server_refactored.py`):
```python
@mcp.tool()
def my_tool(param: str) -> str:
    """Tool documentation"""
    handler = get_handler("default")
    return handler.my_tool(param)
```

3. **Validation** (`backend/security/validators.py`):
```python
def validate_my_tool_params(param: str) -> tuple[bool, Optional[str]]:
    if not isinstance(param, str):
        return False, "param must be string"
    return True, None
```

---

### **Change Rate Limit (5 seconds)**

Edit `backend/config/settings.py`:
```python
RATE_LIMIT_REQUESTS = 20  # Change from 10 to 20 req/sec
RATE_LIMIT_WINDOW = 1     # Per 1 second
```

---

### **Test a Single Tool (1 minute)**

```python
# Create test file: backend/test_single_tool.py
from handlers.tool_handler import get_handler
import json

handler = get_handler("test_user")
result = handler.list_emails("is:unread", 5)
print(json.loads(result))
```

---

### **View Audit Logs (10 seconds)**

```bash
# Raw logs
tail -f backend/logs/audit.json

# Pretty print (requires jq)
cat backend/logs/audit.json | jq .

# Count events
grep -c "event_type" backend/logs/audit.json
```

---

### **Debug a Rate Limit Issue (2 minutes)**

```python
# Check remaining tokens
from security.rate_limiter import get_rate_limiter

rl = get_rate_limiter()
remaining = rl.get_remaining_tokens("user@example.com")
print(f"Tokens remaining: {remaining}")

# Reset a user
rl.reset_user("user@example.com")
```

---

### **Check Credentials Validity (1 minute)**

```python
# Check if credentials are valid
from services.gmail_service import get_credentials

try:
    creds = get_credentials()
    print(f"✅ Credentials valid")
except FileNotFoundError:
    print("❌ credential.json not found")
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## 🎯 Import Paths (Copy-Paste)

```python
# Configuration
from config.settings import (
    APP_NAME,
    APP_VERSION, 
    RATE_LIMIT_REQUESTS,
    DEBUG,
)

# Models
from models.schemas import (
    EmailData,
    DriveFile,
    ToolResult,
    AuditLog,
)

# Services
from services.gmail_service import get_service as get_gmail
from services.drive_service import get_service as get_drive

# Security
from security.validators import validate_email_address
from security.rate_limiter import get_rate_limiter, allow_request
from security.audit_logger import get_audit_logger, log_tool_execution

# Handlers
from handlers.tool_handler import get_handler, ToolHandler
```

---

## 🧪 Test Patterns

### **Test a Validator**
```python
from security.validators import validate_email_address

valid, error = validate_email_address("test@example.com")
assert valid == True
assert error == None
```

### **Test Rate Limiting**
```python
from security.rate_limiter import allow_request
from security.rate_limiter import RateLimitError

try:
    for i in range(20):  # Try 20 requests
        allow_request("test_user")
    print("All passed")
except RateLimitError:
    print(f"Rate limited at request {i}")
```

### **Test Audit Logging**
```python
from security.audit_logger import log_tool_execution

log_tool_execution(
    user_id="test_user",
    tool_name="list_emails",
    status="success",
    execution_time_ms=45,
    request_args={"query": "is:unread"}
)
```

---

## 🔍 Debugging Tips

### **Check what imports work**
```bash
cd backend
python -c "from config.settings import *; print('✓ config works')"
python -c "from models.schemas import *; print('✓ models work')"
python -c "from services.gmail_service import *; print('✓ services work')"
python -c "from security.validators import *; print('✓ security works')"
python -c "from handlers.tool_handler import *; print('✓ handlers work')"
```

### **See all rate limit errors**
```bash
grep "rate_limit_exceeded" backend/logs/audit.json | jq .
```

### **See all tool execution times**
```bash
grep "tool_execution" backend/logs/audit.json | jq '.execution_time_ms'
```

### **Find slow operations**
```bash
grep "tool_execution" backend/logs/audit.json | jq 'select(.execution_time_ms > 1000)'
```

---

## 📊 Performance Notes

| Operation | Typical Time | Notes |
|-----------|--------------|-------|
| List emails | 200-500ms | Cached credentials |
| Read single email | 150-300ms | Full body included |
| Send email | 300-800ms | Includes base64 encoding |
| Search Drive | 400-1000ms | Full-text search |
| Get file info | 150-300ms | Single API call |
| Rate limit check | <1ms | In-memory token bucket |
| Audit log write | 5-10ms | JSON to disk |

---

## 🚨 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: config` | Not in backend folder | `cd backend` first |
| `FileNotFoundError: credential.json` | Missing Google key | Download from Cloud Console |
| `RateLimitError` | Too many requests | Wait 1 second, try again |
| `ValueError: Invalid email` | Bad email format | Check sender address |
| `HttpError 401` | Invalid credentials | Check credential.json |

---

## 📌 Key Concepts

### **Rate Limiting**
- **Type:** Token bucket algorithm
- **Default:** 10 requests per 1 second per user
- **How it works:** Tokens refill automatically
- **When triggered:** Raises `RateLimitError`

### **Audit Logging**
- **What's logged:** Every tool call, errors, security events
- **Where:** `backend/logs/audit.json`
- **PII Protection:** Emails masked, file names truncated
- **Fields:** timestamp, user_id, tool_name, status, execution_time

### **Validation**
- **When:** Before tool execution
- **What's checked:** Email format, file IDs, query strings
- **Injection prevention:** Blocks SQL/prompt injection patterns
- **Custom rules:** Per-tool validation

---

## 🎓 Architecture Diagram

```
User/Agent Request
        ↓
    mcp_server.py
        ↓
  handlers/tool_handler.py  ←─ Orchestration layer
    ↙     ↓      ↖
   /      │       \
  /       │        \
security/ │     services/
  │      │          │
  ├─validators.py  ├─gmail_service.py
  ├─rate_limiter.py└─drive_service.py
  └─audit_logger.py
        ↓
    Google APIs
        ↓
   Email/Drive Data
```

---

## ✅ Pre-Deployment Checklist

Before deploying to production:

- [ ] Run: `python test_mcp_server.py`
- [ ] Check: `backend/logs/audit.json` exists
- [ ] Verify: `backend/credential.json` present
- [ ] Test: One tool manually
- [ ] Confirm: Rate limiting works
- [ ] Review: Audit logs for errors

---

**📚 Full documentation:** See `FOLDER_ORGANIZATION.md` for complete guide
**🆘 Stuck?** Check `VERIFICATION_CHECKLIST.md` or debug using Debugging Tips section above
