# 🧪 Testing Prompts & Payloads Cheat-Sheet

This guide provides copy-paste prompts, Swagger UI JSON payloads, cURL terminal commands, and Pytest commands to test all 6 Gmail & Google Drive MCP tools.

---

## 1. 🤖 LangGraph AI Agent & Web UI Prompts
Copy and paste these natural language prompts directly into:
- `python backend/langgraph_agent.py`
- `chainlit run backend/chainlit_app.py` (Web UI at http://localhost:8000)

### 📧 Gmail AI Prompts

#### **List & Search Emails**
```text
Show me my 5 most recent unread emails.
```
```text
Search for emails from "boss@example.com" with a maximum of 3 results.
```
```text
Find emails with subject "Urgent" or "Action Required".
```
```text
List all starred emails in my inbox.
```

#### **Read Email Content**
```text
Read the complete content of email ID "18e1a2b3c4d5e6f7".
```
```text
Summarize the latest unread email in my inbox.
```

#### **Send Emails**
```text
Send an email to "colleague@example.com" with subject "Project Status Update" and body "The backend refactoring and testing are complete!".
```
```text
Send an email to "dev-team@example.com" with CC "manager@example.com", subject "Release Notes v1.0", and body "The new MCP server version is ready for staging deployment.".
```

---

### 📁 Google Drive AI Prompts

#### **List & Filter Drive Files**
```text
List my 10 most recent files in Google Drive.
```
```text
Show me all Google Docs in my Drive (file_type="application/vnd.google-apps.document").
```
```text
Find all PDF documents in Google Drive.
```
```text
List all Google Sheets spreadsheets in Drive.
```

#### **Search Drive Files**
```text
Search Google Drive for files containing the keyword "Architecture".
```
```text
Find documents with "Quarterly Report" in their title or content.
```

#### **Get File Info**
```text
Get detailed information and sharing status for file ID "1A2B3C4D5E6F7G8H9I".
```

---

### 🔄 Multi-Step Multi-Tool Agent Workflows
```text
Check my unread emails, summarize the first one, and search Google Drive for any files related to its subject.
```

---

## 2. 🌐 Swagger UI JSON Payloads (`http://localhost:8000/docs`)
Run `python backend/api.py` and open **http://localhost:8000/docs**. Click **Try it out** on any endpoint and paste the corresponding JSON body below:

### `POST /api/gmail/list` (List/Search Emails)
```json
{
  "query": "is:unread",
  "max_results": 5
}
```

### `GET /api/gmail/read/{email_id}` (Read Email Content)
Replace `{email_id}` in URL path with your message ID:
`http://localhost:8000/api/gmail/read/18e1a2b3c4d5e6f7`

### `POST /api/gmail/send` (Send Email)
```json
{
  "to": ["recipient@example.com"],
  "subject": "Test Email via Swagger UI",
  "body": "Hello! This is a test email sent using the Swagger UI endpoint.",
  "cc": ["manager@example.com"],
  "bcc": []
}
```

### `POST /api/drive/files` (List Drive Files)
```json
{
  "query": "",
  "max_results": 10,
  "file_type": "application/vnd.google-apps.document"
}
```

### `GET /api/drive/file/{file_id}` (Get File Info)
Replace `{file_id}` in URL path with your file ID:
`http://localhost:8000/api/drive/file/1A2B3C4D5E6F7G8H9I`

### `POST /api/drive/search` (Search Drive)
```json
{
  "keyword": "project",
  "max_results": 5
}
```

---

## 3. 💻 cURL Terminal Commands (PowerShell / Command Prompt / Bash)

### **List Unread Emails:**
```bash
curl -X POST "http://localhost:8000/api/gmail/list" -H "Content-Type: application/json" -d "{\"query\": \"is:unread\", \"max_results\": 5}"
```

### **Send Email:**
```bash
curl -X POST "http://localhost:8000/api/gmail/send" -H "Content-Type: application/json" -d "{\"to\": [\"user@example.com\"], \"subject\": \"cURL Test\", \"body\": \"Testing REST API via cURL.\"}"
```

### **List Drive Files:**
```bash
curl -X POST "http://localhost:8000/api/drive/files" -H "Content-Type: application/json" -d "{\"query\": \"\", \"max_results\": 5}"
```

### **Search Drive:**
```bash
curl -X POST "http://localhost:8000/api/drive/search" -H "Content-Type: application/json" -d "{\"keyword\": \"report\", \"max_results\": 5}"
```

---

## 4. 🧪 Pytest Verification Commands

### **Run all unit tests:**
```powershell
cd backend
python test_mcp_server.py
```

### **Run Pytest with verbose output:**
```powershell
pytest backend/test_mcp_server.py -v
```

### **Run ONLY Gmail tests:**
```powershell
pytest backend/test_mcp_server.py -m gmail -v
```

### **Run ONLY Drive tests:**
```powershell
pytest backend/test_mcp_server.py -m drive -v
```
