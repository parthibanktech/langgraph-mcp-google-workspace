# 🚀 Gmail & Google Drive MCP Server - Quick Start Guide

## Overview

This project implements a **production-ready MCP (Model Context Protocol) server** that connects Gmail and Google Drive to LLM agents. It enables AI assistants to:

- ✅ Read, search, and send emails
- ✅ List, search, and get info about files in Google Drive  
- ✅ Integrate seamlessly with LangGraph agents
- ✅ Work with Claude, GPT-4, and other LLMs

---

## 📁 Project Structure

```
gmail_agent_development/
├── backend/
│   ├── mcp_server.py              # MCP Server (Gmail + Drive tools)
│   ├── test_mcp_server.py         # Test suite for MCP server
│   ├── requirements.txt           # Python dependencies
│   ├── credential.json            # Google service account key (add this!)
│   └── .env.example               # Environment configuration template
├── langgraph_agent.py             # LangGraph AI agent integration
├── SETUP.md                       # Detailed setup instructions
└── QUICKSTART.md                  # This file
```

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Get Google Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable APIs: **Gmail API** and **Google Drive API**
4. Create a Service Account
5. Download JSON key as `credential.json`
6. Place in `backend/` folder

### Step 3: Test the Server
```bash
python backend/test_mcp_server.py
```

Expected output:
```
✅ Credentials loaded successfully
✅ Gmail API client initialized
✅ Google Drive API client initialized
```

---

## 🎯 Use Cases

### Use Case 1: MCP Server Only (Standalone)
Use the MCP server directly with any MCP-compatible client:

```bash
cd backend
python mcp_server.py
```

This exposes 6 tools:
- `list_emails` - Search emails
- `read_email` - Get email content  
- `send_email` - Send emails
- `list_drive_files` - List Drive files
- `get_file_info` - Get file details
- `search_drive` - Search Drive

---

### Use Case 2: LangGraph Agent (Full AI Integration)

Run the example LangGraph agent:

```bash
python langgraph_agent.py
```

This creates an AI agent that can:
1. Understand natural language queries
2. Decide which tools to call
3. Process results and refine answers
4. Hold multi-turn conversations

**Example Queries:**
- "What are my unread emails?"
- "Send a summary email to my boss"
- "Find my project files in Drive and email them"
- "List all documents created this month"

---

## 📊 API Examples

### Gmail Examples

**List Unread Emails:**
```python
from backend.mcp_server import list_emails

result = list_emails(query="is:unread", max_results=10)
# Returns: JSON with email list
```

**Read Email:**
```python
from backend.mcp_server import read_email

email_content = read_email(email_id="17e1ecdfa2d1234567")
# Returns: Complete email with subject, body, from, to, etc.
```

**Send Email:**
```python
from backend.mcp_server import send_email

result = send_email(
    to="recipient@example.com",
    subject="Hello",
    body="This is a test email",
    cc="manager@example.com"
)
# Returns: Success status and message ID
```

### Google Drive Examples

**List Files:**
```python
from backend.mcp_server import list_drive_files

files = list_drive_files(max_results=20)
# Returns: List of files with metadata (name, size, date, etc.)
```

**Search Files:**
```python
from backend.mcp_server import search_drive

results = search_drive(keyword="project report", max_results=10)
# Returns: Search results with file details
```

**Get File Info:**
```python
from backend.mcp_server import get_file_info

info = get_file_info(file_id="1A2B3C4D5E6F")
# Returns: Complete file metadata (owner, permissions, etc.)
```

---

## 🔧 Configuration

### Environment Variables
Create `.env` file in `backend/`:

```bash
# Optional: Set log level
DEBUG=false
LOG_LEVEL=INFO
```

### Gmail API Scopes
The server requests these permissions:
- `gmail.readonly` - Read emails
- `gmail.send` - Send emails  
- `drive.readonly` - Read Drive files
- `drive.file` - Create/modify Drive files

---

## ✅ Testing

### Test Individual Tools
```bash
python -c "
from backend.mcp_server import list_emails
import json
result = json.loads(list_emails(query='is:unread', max_results=5))
print(f'Found {result[\"count\"]} unread emails')
"
```

### Run Full Test Suite
```bash
python backend/test_mcp_server.py
```

Tests verify:
- ✅ Google credentials are valid
- ✅ Gmail API connectivity
- ✅ Google Drive API connectivity
- ✅ Email functions (list, read, send)
- ✅ Drive search functionality

---

## 🚀 Deployment

### Option 1: Local Development
```bash
# Run MCP server
python backend/mcp_server.py

# In another terminal, run agent
python langgraph_agent.py
```

### Option 2: Docker Deployment (Optional)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "backend/mcp_server.py"]
```

Build and run:
```bash
docker build -t gmail-mcp-server .
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY gmail-mcp-server
```

### Option 3: Cloud Deployment (Azure/AWS)
- **Azure Container Apps**: Deploy Docker container to ACA
- **AWS Lambda**: Use the LangGraph integration as Lambda handler
- **Google Cloud Run**: Deploy Docker image to Cloud Run

---

## 🐛 Troubleshooting

### Issue: "credential.json not found"
```bash
# Solution: Download from Google Cloud Console
# 1. Go to Google Cloud Console
# 2. Service Account > Keys > Add Key > JSON
# 3. Save as backend/credential.json
```

### Issue: "Gmail API error: 403 Forbidden"
```bash
# Solution: Enable delegation for the service account
# 1. Google Cloud Console > Service Account > Details
# 2. Enable domain-wide delegation
# 3. Add OAuth 2.0 scopes in Google Workspace Admin Console
```

### Issue: "No emails found"
```bash
# Solution: Check if service account has access
# Try with different query:
list_emails(query="*", max_results=10)  # List all emails
```

### Issue: Tests fail
```bash
# Run with verbose output
python backend/test_mcp_server.py 2>&1 | head -100
```

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup guide with all steps
- **[mcp_server.py](backend/mcp_server.py)** - MCP server implementation (fully commented)
- **[langgraph_agent.py](langgraph_agent.py)** - LangGraph integration example
- **[test_mcp_server.py](backend/test_mcp_server.py)** - Test suite with examples

---

## 🔒 Security Notes

⚠️ **Important:**
- ✅ Never commit `credential.json` to Git
- ✅ Never hardcode API keys
- ✅ Use `.env` for secrets
- ✅ Rotate service account keys every 90 days
- ✅ Use separate service accounts for prod/dev

Add to `.gitignore`:
```
credential.json
.env
__pycache__/
*.pyc
```

---

## 📈 Performance Tips

- Use specific Gmail queries (`is:unread`, `from:user@example.com`)
- Limit `max_results` to 10-20 for real-time responses
- Cache recently fetched emails/files
- Use file IDs instead of re-fetching when possible

---

## 🎓 Learning Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [MCP Protocol Spec](https://spec.modelcontextprotocol.io/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

---

## ❓ FAQ

**Q: Can I use this with Claude?**
A: Yes! Set up the MCP server and configure Claude to use it as a tool.

**Q: What's the difference between MCP server and LangGraph agent?**
A: MCP server is the tool provider. LangGraph agent is the orchestrator that decides when to use tools.

**Q: Can I add more tools?**
A: Yes! Add functions to `mcp_server.py` with `@mcp.tool()` decorator.

**Q: What's the API rate limit?**
A: Gmail: 10+ requests/sec. Drive: 1000+ requests/sec (check Google Cloud Console).

**Q: Can I send emails with attachments?**
A: Currently supports text emails. For attachments, modify `send_email()` in `mcp_server.py`.

---

## 📞 Support

- Check error messages in terminal output
- Review logs in `.env` LOG_LEVEL setting
- Run `test_mcp_server.py` to diagnose issues
- Check Google Cloud Console for API quotas/errors

---

## 🎉 Next Steps

1. ✅ Set up credentials
2. ✅ Run tests to verify
3. ✅ Try LangGraph agent examples
4. ✅ Deploy to your platform
5. ✅ Integrate with your LLM/chatbot

Happy automating! 🚀
