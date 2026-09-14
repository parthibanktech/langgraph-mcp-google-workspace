# 📡 Complete REST API Testing Guide & Payloads

This guide contains copy-paste request bodies, cURL commands, and sample responses for all endpoints in the FastAPI Swagger server (`python backend/api.py` at **http://localhost:8000/docs**).

---

## 🚀 How to Start the API Server

```powershell
cd backend
python api.py
```

Then open **[http://localhost:8000/docs](http://localhost:8000/docs)** in your browser.

---

## 1. 🏥 Health & Status Endpoints

### 1.1 `GET /` (Root Endpoint)
Directs users to interactive documentation URLs.

**cURL Command:**
```bash
curl -X GET "http://localhost:8000/" -H "accept: application/json"
```

**Sample Response:**
```json
{
  "message": "Gmail & Google Drive MCP API Server is Running",
  "swagger_ui": "http://localhost:8000/docs",
  "redoc_ui": "http://localhost:8000/redoc"
}
```

---

### 1.2 `GET /health` (Health Check)
Verifies server health status.

**cURL Command:**
```bash
curl -X GET "http://localhost:8000/health" -H "accept: application/json"
```

**Sample Response:**
```json
{
  "status": "healthy",
  "service": "Gmail & Google Drive MCP REST API"
}
```

---

## 2. 📧 Gmail API Endpoints

### 2.1 `POST /api/gmail/list` (List/Search Emails)
Lists emails matching a query and returns enriched metadata (**Subject**, **From**, **Date**, **Snippet**, **ID**).

**Swagger UI Request Body:**
```json
{
  "query": "is:unread",
  "max_results": 5
}
```

**Alternative Queries to Try:**
- `"from:boss@example.com"`
- `"subject:urgent"`
- `"is:starred"`

**cURL Command:**
```bash
curl -X POST "http://localhost:8000/api/gmail/list" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "is:unread",
    "max_results": 5
  }'
```

**Sample Response:**
```json
{
  "success": true,
  "tool": "list_emails",
  "timestamp": "2026-09-13T16:35:00.000000",
  "data": {
    "count": 5,
    "total_estimate": 201,
    "emails": [
      {
        "id": "1a09b2dff6fa2760",
        "threadId": "1a09b2dff6fa2760",
        "subject": "Weekly Team Sync Notes",
        "from": "manager@example.com",
        "date": "Sun, 13 Sep 2026 21:00:00 GMT",
        "snippet": "Hi team, please find attached the agenda for..."
      }
    ]
  },
  "execution_time_ms": 450
}
```

---

### 2.2 `GET /api/gmail/read/{email_id}` (Read Full Email Content)
Reads full email content by hexadecimal message ID.

> 💡 **Note:** Copy an `id` string (e.g. `1a09b2dff6fa2760`) from `POST /api/gmail/list` response.

**Swagger Path Parameter:**
`email_id`: `1a09b2dff6fa2760`

**cURL Command:**
```bash
curl -X GET "http://localhost:8000/api/gmail/read/1a09b2dff6fa2760" \
  -H "accept: application/json"
```

**Sample Response:**
```json
{
  "success": true,
  "tool": "read_email",
  "timestamp": "2026-09-13T16:35:10.000000",
  "data": {
    "id": "1a09b2dff6fa2760",
    "threadId": "1a09b2dff6fa2760",
    "subject": "Weekly Team Sync Notes",
    "from": "manager@example.com",
    "to": "dev-team@example.com",
    "date": "Sun, 13 Sep 2026 21:00:00 GMT",
    "snippet": "Hi team, please find attached the agenda...",
    "body": "Hi team,\n\nHere are the action items for this week:\n1. Backend refactoring\n2. Security audit logging\n\nBest,\nManager"
  },
  "execution_time_ms": 320
}
```

---

### 2.3 `POST /api/gmail/send` (Send Email)
Sends an email using Gmail API.

**Swagger UI Request Body:**
```json
{
  "to": ["recipient@example.com"],
  "subject": "Test Email via Swagger UI",
  "body": "Hello! This email was sent using the Swagger REST API interface.",
  "cc": ["manager@example.com"],
  "bcc": []
}
```

**cURL Command:**
```bash
curl -X POST "http://localhost:8000/api/gmail/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "Test Email via Swagger UI",
    "body": "Hello! Testing email sending.",
    "cc": []
  }'
```

**Sample Response:**
```json
{
  "success": true,
  "tool": "send_email",
  "timestamp": "2026-09-13T16:35:20.000000",
  "data": {
    "messageId": "1a09c3eef7fa2891",
    "threadId": "1a09c3eef7fa2891",
    "to": ["recipient@example.com"],
    "subject": "Test Email via Swagger UI",
    "status": "sent"
  },
  "execution_time_ms": 680
}
```

---

## 3. 📁 Google Drive API Endpoints

### 3.1 `POST /api/drive/files` (List Drive Files)
Lists Google Drive files with optional MIME type filtering.

**Swagger UI Request Body (All Files):**
```json
{
  "query": "",
  "max_results": 10,
  "file_type": ""
}
```

**Filter Google Docs Only:**
```json
{
  "query": "",
  "max_results": 5,
  "file_type": "application/vnd.google-apps.document"
}
```

**cURL Command:**
```bash
curl -X POST "http://localhost:8000/api/drive/files" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "",
    "max_results": 5,
    "file_type": ""
  }'
```

**Sample Response:**
```json
{
  "success": true,
  "tool": "list_drive_files",
  "timestamp": "2026-09-13T16:35:30.000000",
  "data": {
    "count": 5,
    "files": [
      {
        "id": "1dNSoC4YVmzOEDRjELebbp7LmympRVEmX",
        "name": "Workshop Demo 2 - Monitoring",
        "mimeType": "application/vnd.google-apps.document",
        "createdTime": "2026-09-10T14:20:00Z",
        "modifiedTime": "2026-09-12T18:00:00Z",
        "size": "45210"
      }
    ]
  },
  "execution_time_ms": 390
}
```

---

### 3.2 `GET /api/drive/file/{file_id}` (Get File Details)
Retrieves detailed metadata and web view link for a specific Drive file.

> 💡 **Note:** Copy a file ID string (e.g. `1dNSoC4YVmzOEDRjELebbp7LmympRVEmX`) from `POST /api/drive/files` response.

**Swagger Path Parameter:**
`file_id`: `1dNSoC4YVmzOEDRjELebbp7LmympRVEmX`

**cURL Command:**
```bash
curl -X GET "http://localhost:8000/api/drive/file/1dNSoC4YVmzOEDRjELebbp7LmympRVEmX" \
  -H "accept: application/json"
```

**Sample Response:**
```json
{
  "success": true,
  "tool": "get_file_info",
  "timestamp": "2026-09-13T16:35:40.000000",
  "data": {
    "id": "1dNSoC4YVmzOEDRjELebbp7LmympRVEmX",
    "name": "Workshop Demo 2 - Monitoring",
    "mimeType": "application/vnd.google-apps.document",
    "createdTime": "2026-09-10T14:20:00Z",
    "modifiedTime": "2026-09-12T18:00:00Z",
    "size": "45210",
    "webViewLink": "https://drive.google.com/file/d/1dNSoC4YVmzOEDRjELebbp7LmympRVEmX/view",
    "shared": true
  },
  "execution_time_ms": 280
}
```

---

### 3.3 `POST /api/drive/search` (Search Drive by Keyword)
Performs full-text keyword search across file names and file content.

**Swagger UI Request Body:**
```json
{
  "keyword": "Monitoring",
  "max_results": 5
}
```

**cURL Command:**
```bash
curl -X POST "http://localhost:8000/api/drive/search" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "Monitoring",
    "max_results": 5
  }'
```

**Sample Response:**
```json
{
  "success": true,
  "tool": "search_drive",
  "timestamp": "2026-09-13T16:35:50.000000",
  "data": {
    "count": 1,
    "keyword": "Monitoring",
    "files": [
      {
        "id": "1dNSoC4YVmzOEDRjELebbp7LmympRVEmX",
        "name": "Workshop Demo 2 - Monitoring",
        "mimeType": "application/vnd.google-apps.document"
      }
    ]
  },
  "execution_time_ms": 410
}
```
