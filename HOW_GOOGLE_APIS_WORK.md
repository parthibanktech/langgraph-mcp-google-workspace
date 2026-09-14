# 🌐 How Google Cloud APIs Work

## Understanding Gmail & Google Drive Integration

---

## 📧 Gmail API Overview

### What is Gmail API?
The Gmail API allows applications to interact with Gmail accounts programmatically, enabling:
- Reading emails from inbox
- Sending emails
- Creating/deleting labels
- Searching emails with queries
- Accessing attachments

### How Authentication Works

```
Your Application
        ↓ (sends request with credentials)
Google OAuth 2.0 Server
        ↓ (verifies credentials)
        ✓ Valid? → Generate access token
Google Servers
        ↓ (sends data back)
Your Application (receives email data)
```

### Service Account Authentication

```
┌─────────────────────────────────────────────┐
│  Your Application (MCP Server)              │
│  ├─ Reads: credential.json                 │
│  ├─ Contains: service account key + secret │
│  └─ Creates: JWT signed token              │
└──────────────┬──────────────────────────────┘
               │ (sends JWT token)
               ↓
┌─────────────────────────────────────────────┐
│  Google OAuth 2.0 Token Server              │
│  ├─ Verifies JWT signature                 │
│  ├─ Checks service account permissions    │
│  └─ Issues: Access token (expires in 1h)  │
└──────────────┬──────────────────────────────┘
               │ (returns access token)
               ↓
┌─────────────────────────────────────────────┐
│  Your Application (MCP Server)              │
│  ├─ Uses: Access token for API calls       │
│  └─ Caches: Token until expiration         │
└──────────────┬──────────────────────────────┘
               │ (authenticated API requests)
               ↓
┌─────────────────────────────────────────────┐
│  Gmail API Servers                          │
│  ├─ Verifies access token                  │
│  ├─ Checks permissions (scopes)            │
│  └─ Returns: Email data / sends emails     │
└─────────────────────────────────────────────┘
```

### API Quotas & Rate Limits

#### Gmail API Limits
```
Default Limits:
├─ Requests per second: 10 (user account), unlimited (service account)
├─ Daily quota: 1,000,000 user requests
├─ Message size: Max 500 MB
├─ Labels: Max 500 labels per account
└─ Search query complexity: Max 256 characters

Our Configuration:
├─ Configured for: 10 req/sec (safe buffer)
├─ Daily limit: 100,000 requests (monitoring at 80%)
├─ Retry logic: Exponential backoff (1s, 2s, 4s, 8s)
└─ Timeout: 30 seconds per request
```

#### Rate Limit Handling
```python
# When you hit rate limit:
# Google returns: 429 Too Many Requests
# Server responds with: Retry-After header

Our Behavior:
1. Catch 429 error
2. Wait time specified in header
3. Retry request
4. If fails again, fail gracefully
```

### Example API Calls

**List Emails (Gmail API)**
```
GET https://www.googleapis.com/gmail/v1/users/me/messages?q=is:unread
Headers:
  Authorization: Bearer ACCESS_TOKEN
  
Response:
{
  "messages": [
    {"id": "17e1ecdfa2d1234567", "threadId": "17e1ecdfa2d1234567"},
    {"id": "17e1ecdfa2d1234568", "threadId": "17e1ecdfa2d1234568"}
  ],
  "resultSizeEstimate": 2
}
```

**Send Email (Gmail API)**
```
POST https://www.googleapis.com/gmail/v1/users/me/messages/send
Headers:
  Authorization: Bearer ACCESS_TOKEN
  Content-Type: application/json
  
Body:
{
  "raw": "base64_encoded_message"
}

Response:
{
  "id": "17e1ecdfa2d1234567",
  "threadId": "17e1ecdfa2d1234567",
  "labelIds": ["SENT"]
}
```

---

## 📁 Google Drive API Overview

### What is Google Drive API?
The Google Drive API allows applications to interact with Google Drive files programmatically:
- List files and folders
- Search files by name/content
- Get file metadata
- Download/upload files
- Share files
- Manage permissions

### How it Works

```
Your Application
    ↓ (sends file request)
Google OAuth 2.0 Server (validates token)
    ↓
Google Drive Servers
    ├─ Checks permissions
    ├─ Applies sharing rules
    └─ Returns file data
    ↓
Your Application (receives file list/metadata)
```

### Scopes (Permissions)

```
drive.readonly
├─ Can: View files and folders
├─ Cannot: Create, modify, delete
└─ Use case: Read-only access

drive.file
├─ Can: Access files created by app
├─ Cannot: Access all Drive files
└─ Use case: App-specific files

drive
├─ Can: Full access to all Drive files
├─ Cannot: Limited by account owner
└─ Use case: Full Drive integration
```

### API Quotas & Rate Limits

#### Drive API Limits
```
Default Limits:
├─ Requests per second: 1000
├─ Daily quota: 10,000,000 requests
├─ File size: Max 5TB per file
├─ Search query: Max 1024 characters
└─ Results per request: Max 1000 files

Our Configuration:
├─ Configured for: 100 req/sec (safe buffer)
├─ Daily limit: 500,000 requests (monitoring at 80%)
├─ Retry logic: Exponential backoff
└─ Timeout: 30 seconds per request
```

### Search Queries

```python
# Gmail-style search for Drive:

# Search by name
"name contains 'project'"

# Search by type
"mimeType = 'application/vnd.google-apps.folder'"

# Search by modification date
"modifiedTime > '2024-01-01T00:00:00'"

# Search by owner
"'user@example.com' in owners"

# Search by sharing status
"visibility = 'anyoneCanFind'"

# Combine multiple conditions
"name contains 'project' and mimeType = 'application/vnd.google-apps.document'"
```

### Common MIME Types

```
Documents:
├─ application/vnd.google-apps.document (Google Docs)
├─ application/vnd.google-apps.spreadsheet (Google Sheets)
├─ application/vnd.google-apps.presentation (Google Slides)
├─ application/vnd.google-apps.form (Google Forms)
├─ application/pdf (PDF files)
└─ application/msword (Microsoft Word)

Folders:
├─ application/vnd.google-apps.folder

Media:
├─ image/jpeg (Photos)
├─ image/png (Images)
├─ video/mp4 (Videos)
└─ application/zip (Archives)
```

---

## 🔐 Security Architecture

### How Google Protects Your Data

```
Layer 1: Transportation
├─ HTTPS/TLS 1.2+ encryption
├─ Data encrypted in transit
└─ Man-in-the-middle attacks prevented

Layer 2: Authentication
├─ OAuth 2.0 standard
├─ Service account keys (secure key pair)
├─ JWT token signing
└─ Access token expiration (1 hour)

Layer 3: Authorization
├─ Scope-based permissions
├─ Role-based access control (RBAC)
├─ User-level access checks
└─ Audit logging on every access

Layer 4: Data Protection
├─ Encryption at rest (Google's infrastructure)
├─ Encryption in transit (TLS)
├─ Multi-factor authentication (optional)
└─ Suspicious activity detection

Layer 5: Audit & Compliance
├─ Complete audit logs
├─ Compliance with GDPR/SOC 2/ISO 27001
├─ Data residency options
└─ Transparent privacy policies
```

### Service Account Key Security

```
credential.json contains:
├─ type: "service_account"
├─ project_id: "your-project"
├─ private_key_id: "key-id-123"
├─ private_key: "-----BEGIN PRIVATE KEY-----\n..."
├─ client_email: "service-account@project.iam.gserviceaccount.com"
└─ client_id: "123456789"

⚠️ SECURITY: This is like a password!
├─ Never share it
├─ Never commit to Git
├─ Never hardcode in application
├─ Store in secure vault (Azure Key Vault, AWS Secrets Manager)
├─ Rotate every 90 days
└─ Immediately revoke if compromised
```

---

## 🚀 Performance Characteristics

### Typical Response Times

```
Gmail API:
├─ List emails: 200-500 ms
├─ Read single email: 300-700 ms
├─ Send email: 500-1000 ms
└─ Search: 400-800 ms

Google Drive API:
├─ List files (50 items): 300-600 ms
├─ Get file info: 200-400 ms
├─ Search files: 500-1000 ms
└─ Download file metadata: 200-300 ms

Factors affecting performance:
├─ Network latency (your location to Google servers)
├─ API server load (time of day)
├─ Query complexity (filters, sort, etc.)
├─ Data size (large attachments, many files)
└─ Service account rate limits
```

### Caching Strategy

```
What we DO cache:
├─ Service account credentials (1 hour - matches Google's token expiry)
├─ API clients (connection pooling)
└─ Frequently accessed file metadata (5 minutes)

What we DON'T cache (always fresh):
├─ Email content (might change)
├─ File lists (might change)
└─ User permissions (security critical)

Cache invalidation:
├─ On error → Refresh immediately
├─ On timeout → Refresh next request
└─ On expiration → Refresh
```

---

## 📊 Billing & Cost

### Gmail API Costs
```
Gmail API: FREE
├─ Unlimited read operations
├─ Unlimited send operations
├─ Unlimited search operations
└─ No per-call charges
```

### Google Drive API Costs
```
Google Drive API: FREE
├─ Unlimited read operations
├─ Unlimited list operations
├─ Unlimited search operations
└─ No per-call charges

File Storage:
├─ First 15 GB: FREE (shared with Gmail, Google Photos)
├─ Additional storage: $1.99/100GB, $9.99/1TB, etc.
└─ Our server: Only reads metadata (no storage impact)
```

### Why APIs Are Free

Google provides free API access because:
1. They want developers to build apps
2. They make money from Google Workspace subscriptions
3. API usage is small compared to storage
4. Rate limits prevent abuse

---

## ⚡ Common Issues & Solutions

### Issue 1: 401 Unauthorized

**Cause**: Invalid or expired credentials
**Solution**:
```python
# Check:
✓ credential.json exists and is valid
✓ Service account has necessary permissions
✓ Token hasn't expired
✓ No typos in project ID or service account email

# Fix:
1. Regenerate credential.json from Google Cloud Console
2. Verify service account has Gmail/Drive API permissions
3. Restart application
```

### Issue 2: 403 Forbidden

**Cause**: Service account lacks required permissions
**Solution**:
```python
# Check:
✓ Gmail API is enabled in Google Cloud Console
✓ Google Drive API is enabled in Google Cloud Console
✓ Service account has correct roles assigned

# Fix:
1. Go to Google Cloud Console
2. IAM & Admin → Service Accounts
3. Assign Gmail API Editor role
4. Assign Drive API Editor role
5. Wait 2-3 minutes for permissions to propagate
```

### Issue 3: 429 Too Many Requests

**Cause**: Hit rate limit
**Solution**:
```python
# Our code automatically handles this:
1. Catches 429 error
2. Waits time specified in response header
3. Retries request
4. Exponential backoff (1s → 2s → 4s → 8s)

# To prevent:
✓ Don't loop more than 10 requests/sec
✓ Use batch operations when possible
✓ Cache results when feasible
```

### Issue 4: No Emails/Files Found

**Cause**: Search query returns empty results
**Solution**:
```python
# Check:
✓ Query syntax is correct
✓ Query returns any results
✓ Service account can access the data

# Test:
1. Try broader query: "*" instead of specific filter
2. Try simpler query: "is:unread" instead of complex filter
3. Check if service account is delegated for Gmail
```

---

## 🔄 Data Flow Diagram

### Request Flow (Detailed)

```
┌─────────────────────────────────────────────────────────┐
│ Your Application (MCP Server)                           │
│  User: "List my unread emails"                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓ (1) Prepare request
            ┌────────────────────┐
            │ Call list_emails() │
            │ Query: "is:unread" │
            │ MaxResults: 10     │
            └────────┬───────────┘
                     │
                     ↓ (2) Lazy-load Gmail service
            ┌────────────────────────┐
            │ Get Gmail API client   │
            │ (if not already cached)│
            └────────┬───────────────┘
                     │
                     ↓ (3) Authenticate
            ┌────────────────────────────────┐
            │ Load credential.json           │
            │ Create JWT token               │
            │ Exchange for access token      │
            └────────┬──────────────────────┘
                     │
                     ↓ (4) Make API call
            ┌────────────────────────────────┐
            │ POST /gmail/v1/users/me/       │
            │         messages               │
            │ Headers:                       │
            │   Authorization: Bearer TOKEN  │
            │ Query:                         │
            │   q=is:unread&maxResults=10    │
            └────────┬──────────────────────┘
                     │
         ┌───────────┴────────────┐
         │ Google Servers         │
         │ ├─ Verify token       │
         │ ├─ Check permissions  │
         │ ├─ Execute search     │
         │ └─ Return results     │
         └───────────┬────────────┘
                     │
                     ↓ (5) Receive response
            ┌────────────────────────────────┐
            │ Parse JSON                     │
            │ Extract email IDs              │
            │ Count results                  │
            └────────┬──────────────────────┘
                     │
                     ↓ (6) Return to user
            ┌────────────────────────────────┐
            │ Format response                │
            │ {                              │
            │   "success": true,             │
            │   "count": 5,                  │
            │   "emails": [...]             │
            │ }                              │
            └────────┬──────────────────────┘
                     │
                     ↓
        ┌──────────────────────────────┐
        │ User receives results         │
        │ See 5 unread emails           │
        └───────────────────────────────┘
```

---

## 📚 Reference Documentation

### Google API Documentation
- Gmail API: https://developers.google.com/gmail/api
- Google Drive API: https://developers.google.com/drive/api
- OAuth 2.0: https://developers.google.com/identity/protocols/oauth2

### Best Practices
- Always use HTTPS
- Never expose private keys
- Implement exponential backoff for retries
- Cache access tokens (max 1 hour)
- Monitor API quota usage
- Set up audit logging
- Use service accounts for server applications

### Troubleshooting
- Check Google Cloud Console for API errors
- Enable debug logging to see API requests/responses
- Test API calls with Google's API Explorer
- Review Google API documentation for error codes
- Contact Google Cloud Support for quota issues

---

## ✅ Checklist: Understanding Google APIs

Before proceeding to production, ensure you understand:

- [ ] How OAuth 2.0 service account authentication works
- [ ] Difference between access tokens and refresh tokens
- [ ] How rate limiting works and when it triggers
- [ ] Gmail API search query syntax
- [ ] Google Drive API search query syntax
- [ ] How to generate and rotate service account keys
- [ ] Why we cache credentials vs. why we don't cache data
- [ ] Security implications of exposing private keys
- [ ] Cost structure (APIs are free, storage is paid)
- [ ] Common error codes (401, 403, 429) and solutions

---

**Document**: How Google Cloud APIs Work  
**Version**: 1.0  
**Updated**: 2026-09-13  
**Status**: Production Ready ✅
