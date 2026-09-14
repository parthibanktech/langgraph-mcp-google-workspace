# 🆘 Troubleshooting & FAQ

## Common Problems & Solutions

---

## 🔴 Setup Issues

### Problem: "ModuleNotFoundError: No module named 'google.auth'"

**Error Message**:
```
ModuleNotFoundError: No module named 'google.auth'
```

**Cause**: Python dependencies not installed

**Solution** (Step by step):
```bash
# Step 1: Navigate to project folder
cd backend/

# Step 2: Verify virtual environment exists
# Windows:
env\Scripts\activate

# Mac/Linux:
source env/bin/activate

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Verify installation
python -c "import google.auth; print('✓ google.auth installed')"

# Step 5: Run tests
python test_mcp_server.py
```

**If still not working**:
```bash
# Option A: Reinstall from scratch
rm -rf env  # or: rmdir /s env (Windows)
python -m venv env
env\Scripts\activate  # or: source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Option B: Check Python version (must be 3.11+)
python --version

# Option C: Check if pip is using right Python
pip --version  # should mention Python 3.11+
```

---

### Problem: "FileNotFoundError: credential.json not found"

**Error Message**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'credential.json'
```

**Cause**: Google Cloud service account key not downloaded

**Solution** (Follow these steps exactly):

1. **Go to Google Cloud Console**
   ```
   https://console.cloud.google.com/
   ```

2. **Create a Project** (if you don't have one)
   - Click "Select a Project" dropdown
   - Click "New Project"
   - Name: `Gmail-Drive-MCP`
   - Click "Create"

3. **Enable APIs**
   - In search bar, type: `Gmail API`
   - Click on "Gmail API" result
   - Click blue "Enable" button
   - Repeat for "Google Drive API"

4. **Create Service Account**
   - Go to: IAM & Admin → Service Accounts
   - Click "Create Service Account"
   - Name: `gmail-drive-mcp-server`
   - Click "Create"

5. **Get Service Account Email**
   - Copy the email shown (looks like: `gmail-drive-mcp-server@project-123.iam.gserviceaccount.com`)
   - You'll need this in next step

6. **Create and Download Key**
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select "JSON"
   - Click "Create"
   - File downloads automatically (usually: Downloads/project-123-abc.json)

7. **Move to Project Folder**
   ```bash
   # Windows (in PowerShell):
   Move-Item "$HOME\Downloads\project-*.json" "backend\credential.json"
   
   # Mac/Linux:
   mv ~/Downloads/project-*.json backend/credential.json
   ```

8. **Verify**
   ```bash
   # Check file exists
   ls backend/credential.json  # (or: dir backend\credential.json on Windows)
   
   # Test it works
   python test_mcp_server.py
   ```

**Still not working?**
- [ ] Verify APIs are enabled (Gmail API, Google Drive API)
- [ ] Verify credential.json is in `backend/` folder (not root)
- [ ] Verify credential.json contains `private_key` field
- [ ] Check file size > 1000 bytes (it's a full JSON file)

---

### Problem: "Permission denied: User does not have permission to access this resource"

**Error Message**:
```
Permission denied: User does not have permission to access this resource
```

**Cause**: Service account missing permissions

**Solution**:

1. **Check Google Cloud Console**
   - Go to: https://console.cloud.google.com/
   - IAM & Admin → Service Accounts
   - Find: `gmail-drive-mcp-server`

2. **Check Current Roles**
   - Click on service account
   - Look for "Gmail API Editor" and "Drive API Editor" roles
   - If missing: Add them

3. **Add Missing Roles**
   - Principal: `gmail-drive-mcp-server@project-*.iam.gserviceaccount.com`
   - Add roles:
     - [ ] `Editor` (temporary, for setup)
     - [ ] `Gmail API Editor` (or custom role with gmail.*)
     - [ ] `Drive API Editor` (or custom role with drive.*)

4. **Wait for Propagation**
   - Changes take 2-3 minutes to propagate
   - Don't test immediately
   - Wait 3 minutes, then test again

5. **Test Again**
   ```bash
   python test_mcp_server.py
   ```

---

## 🟡 Runtime Issues

### Problem: "401 Unauthorized"

**Error Message**:
```
401 Unauthorized: Invalid Credentials
```

**Causes** (try each):

1. **Expired Access Token**
   ```bash
   # Our code auto-refreshes, but if it doesn't:
   # Cause: Service account key is invalid/revoked
   # Fix: Regenerate credential.json from Google Cloud Console
   ```

2. **Invalid Credential File**
   ```bash
   # Check credential.json structure:
   python -c "
   import json
   with open('backend/credential.json') as f:
       data = json.load(f)
       # Should have these fields:
       assert 'type' in data
       assert 'project_id' in data
       assert 'private_key' in data
       assert 'client_email' in data
       print('✓ credential.json is valid JSON')
   "
   ```

3. **Service Account Deleted**
   ```bash
   # Check service account still exists:
   # Go to: IAM & Admin → Service Accounts
   # Should see: gmail-drive-mcp-server
   # If deleted: Create a new one and download key
   ```

---

### Problem: "403 Forbidden"

**Error Message**:
```
403 Forbidden: The user does not have sufficient permissions
```

**Solutions** (in order):

1. **Verify APIs are Enabled**
   ```
   https://console.cloud.google.com/
   Search: "Gmail API" → Click result → Verify "Enable" button is grayed out (✓)
   Search: "Google Drive API" → Click result → Verify "Enable" button is grayed out (✓)
   ```

2. **Verify Service Account Roles**
   ```
   IAM & Admin → Service Accounts
   Click on: gmail-drive-mcp-server
   Under "Roles" you should see:
     - Editor OR
     - Gmail API Editor OR
     - Custom role with gmail.* permissions
   
   Same for Drive API
   ```

3. **Wait for Permission Propagation**
   ```
   This can take 2-3 minutes!
   Don't test immediately after adding roles.
   
   Wait 3 minutes → Run test again
   ```

4. **Check Gmail Delegation** (if using delegated domain admin)
   ```
   If you're using domain admin delegation:
   1. Go to: Admin Console → Security → Access and data control → API controls
   2. Manage Domain Wide Delegation
   3. Find: gmail-drive-mcp-server@project-*.iam.gserviceaccount.com
   4. Check scope: https://www.googleapis.com/auth/gmail
   5. Check scope: https://www.googleapis.com/auth/drive
   ```

---

### Problem: "429 Too Many Requests"

**Error Message**:
```
429 Too Many Requests: Rate limit exceeded
```

**Explanation**: You're making too many API calls too fast

**Solutions**:

1. **Automatic Handling**
   ```python
   # Our code handles 429 automatically:
   # - Waits the time specified by Google
   # - Retries the request
   # - Uses exponential backoff
   # You usually don't need to do anything
   ```

2. **If Still Hitting Limits**
   ```python
   # In your code, add delays:
   import time
   
   emails = []
   for i in range(100):
       email = list_emails(max_results=10)  # Make 10 API calls
       emails.extend(email)
       time.sleep(1)  # Wait 1 second between batches
   ```

3. **Request Higher Quota**
   ```
   Go to: Google Cloud Console
   APIs & Services → Quotas
   Find: Gmail API, Google Drive API
   Click on quota
   Click "Edit Quotas"
   Enter higher limit
   Wait for approval (usually instant for increases)
   ```

4. **Check Your Request Pattern**
   ```python
   # Bad (too many requests too fast):
   for i in range(1000):
       read_email(email_id)
       # No delay = 1000 req/sec
   
   # Good (spaced out):
   for i in range(1000):
       read_email(email_id)
       time.sleep(0.1)  # 10 requests per second
   ```

---

### Problem: "Insufficient storage" when sending emails

**Error Message**:
```
Error: Insufficient storage. Unable to send message.
```

**Cause**: Gmail account is over storage quota

**Solutions**:

1. **Check Gmail Storage**
   ```
   Go to: Gmail → Settings → Storage
   Shows current usage
   ```

2. **Increase Storage**
   ```
   Option A: Buy Google One subscription ($1.99+/month)
   Option B: Delete old emails/attachments
   Option C: Archive emails (reduces storage)
   ```

3. **If Production Account**
   ```
   Use Google Workspace (business account)
   Get more storage included (30+ GB)
   Contact Google Support for enterprise limits
   ```

---

## 🟢 Advanced Issues

### Problem: "ModuleNotFoundError: No module named 'chainlit'"

**When**: Running `chainlit run chainlit_app.py`

**Error Message**:
```
ModuleNotFoundError: No module named 'chainlit'
```

**Solution**:
```bash
# Chainlit is optional (for web UI only)

# Option A: Install Chainlit
pip install chainlit

# Option B: Skip web UI, use CLI only
python backend/test_mcp_server.py  # This works without Chainlit

# Option C: Use with the MCP server programmatically
python
>>> from backend.mcp_server import list_emails, read_email
>>> emails = list_emails("is:unread", 10)
>>> print(emails)
```

---

### Problem: "SSL: CERTIFICATE_VERIFY_FAILED"

**Error Message**:
```
urllib3.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] 
certificate verify failed: unable to get local issuer certificate
```

**Cause**: SSL certificate verification failing (usually network/firewall issue)

**Solutions**:

1. **Update Certificates** (recommended)
   ```bash
   # Windows:
   python -m pip install --upgrade certifi
   
   # Mac:
   /Applications/Python\ 3.11/Install\ Certificates.command
   
   # Linux:
   sudo apt-get install ca-certificates
   ```

2. **Check Network/Firewall**
   ```bash
   # Can you reach Google servers?
   ping www.google.com
   
   # Can you access Gmail API?
   python
   >>> import requests
   >>> requests.get('https://www.googleapis.com/discovery/v1/apis/gmail/v1/rest')
   ```

3. **Disable Verification** (NOT recommended for production)
   ```python
   # ⚠️ SECURITY RISK: Only for debugging
   import ssl
   import urllib3
   urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
   
   # Then test
   python test_mcp_server.py
   
   # After fixing, remove this code!
   ```

---

### Problem: "Connection timeout after 30 seconds"

**Error Message**:
```
TimeoutError: Connection timeout after 30 seconds
```

**Causes** (check each):

1. **Network Connectivity**
   ```bash
   # Check if you can reach Google
   ping www.googleapis.com
   curl https://www.googleapis.com
   ```

2. **Proxy/Firewall Blocking**
   ```bash
   # If behind corporate proxy:
   pip install -r requirements.txt --proxy [user:passwd@]proxy.server:port
   
   # Check firewall rules
   # Allow: *.googleapis.com on port 443
   ```

3. **High Latency**
   ```bash
   # Check latency
   ping www.googleapis.com  # Should be <100ms
   
   # If high, may be:
   - Geographic distance (use Google's regional endpoints)
   - Congested network (retry later)
   - ISP routing issues (contact ISP)
   ```

4. **Increase Timeout** (temporary fix)
   ```python
   # In mcp_server.py, find build_service():
   # Add: timeout=60  # instead of default 30
   
   from googleapiclient.discovery import build
   service = build(
       'gmail',
       'v1',
       credentials=credentials,
       timeout=60  # Increase timeout
   )
   ```

---

## 🔍 Debugging Tips

### Enable Debug Logging

```python
# Add to top of your script:
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable library logging
logging.getLogger('google').setLevel(logging.DEBUG)
logging.getLogger('googleapiclient').setLevel(logging.DEBUG)

# Now run your code
python your_script.py
```

**Output shows**:
- Every API call made
- Request/response headers
- Full error messages
- Timing information

---

### Test Individual Components

```bash
# Test 1: Can we load credentials?
python
>>> from backend.mcp_server import get_credentials
>>> creds = get_credentials()
>>> print(f"✓ Credentials loaded: {creds}")

# Test 2: Can we connect to Gmail API?
python
>>> from backend.mcp_server import init_gmail_service
>>> service = init_gmail_service()
>>> print(f"✓ Gmail service connected")

# Test 3: Can we list emails?
python
>>> from backend.mcp_server import list_emails
>>> result = list_emails()
>>> print(f"✓ Found {result['count']} emails")

# Test 4: Run full test suite
python backend/test_mcp_server.py
```

---

### Check Environment Variables

```bash
# View current environment
python -c "import os; print(os.environ)"

# Check specific variables
python -c "import os; print(f'GOOGLE_CREDENTIALS_PATH: {os.getenv(\"GOOGLE_CREDENTIALS_PATH\")}')"

# Set for current session only (Windows):
$env:GOOGLE_CREDENTIALS_PATH = "backend/credential.json"
python test_mcp_server.py

# Set for current session only (Mac/Linux):
export GOOGLE_CREDENTIALS_PATH="backend/credential.json"
python test_mcp_server.py
```

---

## ❓ Frequently Asked Questions

### Q: Do I need a Gmail account to use this?
**A**: Yes! The service account accesses Gmail through a Google Cloud project. You need:
- A Google account (personal or Workspace)
- A Google Cloud project linked to that account
- A service account with Gmail/Drive permissions

### Q: Can I use this with multiple Gmail accounts?
**A**: Not directly. Each service account can only access one set of Google accounts. To support multiple accounts:
- Create multiple service accounts (one per Gmail account)
- Switch between them based on which account you need
- Or use domain delegation (Workspace accounts only)

### Q: Is my email data safe?
**A**: Yes, if you:
- [ ] Keep credential.json secure (don't share, don't commit to Git)
- [ ] Use HTTPS only
- [ ] Rotate keys every 90 days
- [ ] Enable audit logging
- [ ] Use strong passwords on Google accounts
- [ ] Enable 2FA on Google accounts

### Q: Can I use this with Yahoo/Outlook/other email?
**A**: No. This only works with Gmail because it uses the Gmail API. For other email providers, you'd need different APIs (Microsoft Graph for Outlook, etc.).

### Q: How do I send emails with attachments?
**A**: Currently `send_email()` doesn't support attachments. To add it:
```python
# You would need to:
1. Base64-encode the file
2. Add it to the MIME message
3. Use email.mime library
4. Then send via send_email()
```
See: [Python email with attachments](https://docs.python.org/3/library/email.examples.html)

### Q: Can I delete emails or files?
**A**: Not yet. The current tools are read-only + send (for emails). To add delete:
```python
# Gmail delete:
def delete_email(email_id):
    service.users().messages().delete(userId='me', id=email_id)

# Drive delete:
def delete_file(file_id):
    service.files().delete(fileId=file_id)
```

### Q: What's the difference between access token and refresh token?
**A**: 
- **Access Token**: Short-lived (1 hour), used for API calls
- **Refresh Token**: Long-lived, used to get new access tokens
- **Service Account**: No refresh token needed (system generates new ones)

### Q: How do I export my data (GDPR)?
**A**: 
```bash
# Export all emails to JSON:
python
>>> emails = list_emails()
>>> import json
>>> with open('emails_export.json', 'w') as f:
>>>     json.dump(emails, f)

# Export all Drive files:
python
>>> files = list_drive_files()
>>> with open('drive_export.json', 'w') as f:
>>>     json.dump(files, f)
```

### Q: Can I use this in production?
**A**: Yes! But you must:
- [ ] Complete the PRODUCTION_CHECKLIST.md (all items)
- [ ] Run security tests
- [ ] Set up monitoring
- [ ] Implement rate limiting
- [ ] Enable audit logging
- [ ] Test disaster recovery
- [ ] Have on-call support ready

### Q: How do I monitor API usage?
**A**: 
```
Google Cloud Console:
1. Go to: APIs & Services → Quotas
2. Find: Gmail API, Google Drive API
3. See current usage vs. limits
4. Set up alerts if usage > 80%
```

### Q: What if I hit the API quota?
**A**: 
1. Our code auto-retries with exponential backoff
2. If still hitting limit, either:
   - Wait until quota resets (midnight Pacific Time)
   - Request higher quota in Google Cloud Console
   - Spread requests across time

---

## 📞 Getting Help

### Before Asking for Help, Check:

1. **Run the diagnostic**
   ```bash
   python
   >>> from backend.mcp_server import get_credentials
   >>> from backend.mcp_server import init_gmail_service, init_drive_service
   >>> creds = get_credentials()
   >>> gmail = init_gmail_service()
   >>> drive = init_drive_service()
   >>> print("✓ All systems operational")
   ```

2. **Check error logs**
   ```bash
   # See detailed error messages
   python backend/test_mcp_server.py
   ```

3. **Review documentation**
   - SETUP.md (how to set up)
   - QUICKSTART.md (how to use)
   - HOW_GOOGLE_APIS_WORK.md (understanding APIs)
   - PRODUCTION_DEPLOYMENT.md (deploying to production)

### Where to Get Help

| Issue | Where to Ask |
|-------|-------------|
| Google API question | [Google Developers](https://developers.google.com/gmail/api/support) |
| Python error | [Stack Overflow](https://stackoverflow.com) |
| MCP Protocol question | [MCP Documentation](https://modelcontextprotocol.io) |
| LangGraph question | [LangChain Discord](https://discord.gg/langchain) |
| Deployment question | See PRODUCTION_DEPLOYMENT.md |
| Security question | Your security team + Google Cloud Security |

---

## ✅ Final Checklist

Before declaring "production ready":

- [ ] All tests pass: `python backend/test_mcp_server.py`
- [ ] No error logs in console
- [ ] Credentials test passes
- [ ] Gmail API test passes
- [ ] Drive API test passes
- [ ] Email send/read works
- [ ] File list/search works
- [ ] Response times < 2 seconds
- [ ] No memory leaks (run for 1 hour)
- [ ] Monitoring set up
- [ ] Alert configured
- [ ] Rate limiting implemented
- [ ] Audit logging works
- [ ] Encryption in transit verified (HTTPS)
- [ ] Security checklist complete

---

**Document**: Troubleshooting & FAQ  
**Version**: 1.0  
**Updated**: 2026-09-13  
**Status**: Production Ready ✅

Last updated: 2026-09-13
