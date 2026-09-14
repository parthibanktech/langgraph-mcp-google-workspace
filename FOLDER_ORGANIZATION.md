# Backend Organization Guide

## 📁 New Layered Architecture Structure

```
backend/
├── config/
│   ├── __init__.py
│   └── settings.py              # All configuration and environment variables
│
├── models/
│   ├── __init__.py
│   └── schemas.py               # Data models: EmailData, DriveFile, ToolResult, AuditLog
│
├── services/
│   ├── __init__.py
│   ├── gmail_service.py         # Gmail API wrapper
│   └── drive_service.py         # Google Drive API wrapper
│
├── security/
│   ├── __init__.py
│   ├── validators.py            # Input validation & sanitization
│   ├── rate_limiter.py          # Rate limiting (token bucket algorithm)
│   └── audit_logger.py          # Audit logging for compliance
│
├── handlers/
│   ├── __init__.py
│   └── tool_handler.py          # Business logic for all 6 MCP tools
│
├── mcp_server.py                # MCP server entry point (tool definitions)
├── mcp_server_refactored.py     # New refactored version (use this!)
├── langgraph_agent.py           # AI agent for natural language understanding
├── chainlit_app.py              # Web UI
├── test_mcp_server.py           # Test suite
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── credential.json              # Google service account key (git ignored)
```

---

## 🎯 Benefits of This Organization

### **Separation of Concerns**
- `config/` - Configuration management (no business logic)
- `models/` - Data structures only (no side effects)
- `services/` - API interactions (no validation logic)
- `security/` - Cross-cutting concerns (validation, rate limiting, audit)
- `handlers/` - Business logic and orchestration
- `mcp_server.py` - Tool definitions only (thin layer)

### **Testability**
- Each module can be tested independently
- Easy to mock dependencies
- Security layer can be tested in isolation

### **Maintainability**
- Clear responsibility for each module
- Easy to find where to add new features
- Changes in one layer don't affect others

### **Scalability**
- Easy to add new tools (just add to handler)
- Easy to add new security policies (validators, rate limits)
- Easy to change API wrappers (swap Gmail service)

### **Security**
- All input validation in one place (`security/validators.py`)
- All rate limiting in one place (`security/rate_limiter.py`)
- All audit logging in one place (`security/audit_logger.py`)

---

## 📝 How to Use This Structure

### **Adding a New Tool**

1. **Add handler method** in `handlers/tool_handler.py`:
   ```python
   def my_new_tool(self, param1: str) -> str:
       def _execute():
           # Business logic here
           return result
       result = self._execute_with_rate_limit("my_new_tool", _execute)
       return json.dumps(result)
   ```

2. **Add MCP tool** in `mcp_server.py`:
   ```python
   @mcp.tool()
   def my_new_tool(param1: str) -> str:
       """Tool documentation"""
       handler = get_handler("default")
       return handler.my_new_tool(param1)
   ```

3. **Add validation** in `security/validators.py`:
   ```python
   def validate_my_new_tool_params(param1: str) -> tuple[bool, Optional[str]]:
       # Validation logic
       return True, None
   ```

### **Adding a New Service**

1. Create new file in `services/`:
   ```python
   # services/slack_service.py
   class SlackService:
       def __init__(self):
           self.service = None
       
       def send_message(self, channel: str, text: str):
           # API call
           pass
   ```

2. Import in `handlers/tool_handler.py`:
   ```python
   from services.slack_service import get_slack_service
   
   def __init__(self, user_id: str = "default"):
       self.slack_service = get_slack_service()
   ```

### **Adding a New Validation Rule**

1. Add validator in `security/validators.py`:
   ```python
   def validate_my_param(value: str) -> bool:
       # Validation logic
       return True
   ```

2. Use in handler:
   ```python
   valid, error = validate_my_param(param)
   if not valid:
       return json.dumps({"success": False, "error": error})
   ```

### **Reviewing Security Events**

All security events are logged to `logs/audit.json`:

```bash
# View recent security events
tail -f backend/logs/audit.json

# Search for rate limit events
grep "rate_limit_exceeded" backend/logs/audit.json

# Count security events
grep "event_type" backend/logs/audit.json | wc -l
```

---

## 🔧 Configuration

All configuration is in `config/settings.py`. Use environment variables:

```bash
# .env file
DEBUG=false
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=10
AUDIT_LOGGING_ENABLED=true
GOOGLE_PROJECT_ID=my-project
ENVIRONMENT=production
```

Or set via Python:
```python
from config.settings import RATE_LIMIT_REQUESTS
print(RATE_LIMIT_REQUESTS)  # 10
```

---

## 🧪 Testing This Architecture

```bash
# Run all tests
python -m pytest backend/test_mcp_server.py -v

# Test a specific module
python -m pytest backend/tests/test_validators.py -v

# Test with coverage
python -m pytest backend/ --cov=backend --cov-report=html
```

---

## 🚀 Migration from Old Code

The old monolithic `mcp_server.py` (backed up as `mcp_server.py.backup`) has been refactored into this modular architecture. 

**To switch to the new structure:**

1. Replace the old `mcp_server.py` with `mcp_server_refactored.py`
2. Test everything works: `python test_mcp_server.py`
3. Delete `mcp_server.py.backup` when confident

---

## 📊 Code Metrics

| Metric | Old Code | New Code | Improvement |
|--------|----------|----------|-------------|
| Lines in single file | 450+ | ~100 | 78% smaller |
| Number of files | 1 | 14 | Better organization |
| Functions per file | 10 | 2-3 | Clear focus |
| Testability | Medium | High | Easier to test |
| Reusability | Low | High | Components isolated |

---

## ✅ What You Get

✓ **Clean architecture** - Clear separation of concerns  
✓ **Scalable** - Easy to add features  
✓ **Secure** - Centralized security controls  
✓ **Testable** - Each module independently testable  
✓ **Maintainable** - Clear where to make changes  
✓ **Enterprise-ready** - Proper logging and audit trails  

---

**Ready to use!** Run your MCP server with:
```bash
python mcp_server_refactored.py
```
