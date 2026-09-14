# Gmail & Google Drive MCP Server - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Cloud Project with service account
- Gmail API enabled
- Google Drive API enabled

### Setup Steps

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Create Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable APIs:
   - Gmail API
   - Google Drive API
4. Create a Service Account:
   - IAM & Admin → Service Accounts → Create Service Account
   - Name: `gmail-drive-mcp-server`
5. Create and download JSON key:
   - Service Account → Keys → Add Key → JSON
   - Save as `credential.json` in `backend/` folder
6. (Optional for Gmail) Enable delegated auth:
   - Add scopes in API Console
   - Delegate domain-wide authority to the service account

#### 3. Configure Environment
```bash
cp .env.example .env
# Update .env with any custom settings
```

#### 4. Run the Server
```bash
python mcp_server.py
```

Expected output:
```
🚀 Starting MCP Server: Google Tools (Gmail + Drive)
Tools available:
  📧 Gmail: list_emails, read_email, send_email
  📁 Drive: list_drive_files, get_file_info, search_drive
```

---

## 📧 Gmail Tool Examples

### List Unread Emails
```python
list_emails(query="is:unread", max_results=10)
```

### Search Emails by Sender
```python
list_emails(query="from:boss@company.com", max_results=20)
```

### Search by Subject
```python
list_emails(query="subject:meeting", max_results=15)
```

### Read Complete Email
```python
read_email(email_id="17e1ecdfa2d1234567")
```

### Send Email
```python
send_email(
    to="recipient@example.com",
    subject="Project Update",
    body="Here's the latest status...",
    cc="manager@example.com"
)
```

---

## 📁 Google Drive Tool Examples

### List All Files
```python
list_drive_files(max_results=20)
```

### List Folders Only
```python
list_drive_files(
    file_type="application/vnd.google-apps.folder",
    max_results=10
)
```

### List Google Docs
```python
list_drive_files(
    file_type="application/vnd.google-apps.document",
    max_results=10
)
```

### Search Files by Name
```python
search_drive(keyword="project report", max_results=20)
```

### Get File Details
```python
get_file_info(file_id="1A2B3C4D5E6F7G8H9I0J")
```

---

## 🔒 Security Best Practices

1. **Never commit `credential.json`** to version control
   - Add to `.gitignore`:
   ```
   credential.json
   .env
   ```

2. **Rotate keys regularly**
   - Delete old keys from Google Cloud Console
   - Create new key every 90 days

3. **Limit service account permissions**
   - Only grant necessary Gmail/Drive scopes
   - Use custom roles if available

4. **Use .env for secrets**
   - Never hardcode credentials in code

5. **Monitor API usage**
   - Check Google Cloud Console API quotas
   - Set up alerts for unusual activity

---

## 🛠️ Integration with LLMs

### Claude/ChatGPT Integration
The MCP server can be used with Agentic frameworks:

```python
# Use with LangGraph
from langchain_mcp_adapters import MCPClient

client = MCPClient("stdio", ["python", "mcp_server.py"])
tools = client.get_tools()
```

### Use with LLM Agent
```python
# Agent can now call Gmail/Drive tools
agent.invoke({
    "messages": [
        {"role": "user", "content": "List my unread emails"}
    ],
    "tools": tools
})
```

---

## 📊 Tool Response Format

All tools return JSON with this structure:
```json
{
  "success": true,
  "message": "optional message",
  "count": 10,
  "emails": [...],  // or "files", "results" depending on tool
  "error": "error message if success is false"
}
```

---

## 🐛 Troubleshooting

### Issue: "credential.json not found"
**Solution**: Ensure credential.json is in the `backend/` folder

### Issue: "Gmail API error: 403 Forbidden"
**Solution**: 
- Verify service account has Gmail API access
- Check Google Cloud Console permissions
- Ensure APIs are enabled in the project

### Issue: "Drive API error: 401 Unauthorized"
**Solution**:
- Verify credential.json is valid
- Check if service account key is expired
- Regenerate key in Google Cloud Console

### Issue: "No files found" or "No emails found"
**Solution**:
- Verify service account has delegated domain authority
- For Gmail: Enable Gmail API delegation
- Try different search queries

---

## 📈 Performance Tips

1. **Use max_results wisely**
   - Smaller batches = faster responses
   - Recommended: 10-20 for real-time use

2. **Cache results**
   - Store recently fetched emails/files
   - Implement TTL-based cache

3. **Use specific queries**
   - `is:unread` is faster than fetching all emails
   - Use MIME type filters for Drive searches

4. **Lazy loading**
   - API clients are initialized on first use
   - Reduces startup time

---

## 📝 License & Support

For issues or questions:
- Check Google API documentation
- Review MCP protocol docs
- Test with `mcp_server.py` directly

Happy automating! 🎉
