# 🏢 Production-Ready Deployment Guide
## Gmail & Google Drive MCP Server - Complete Enterprise Setup

---

## 📋 Table of Contents
1. [Security Evaluation Checklist](#security-checklist)
2. [Google Cloud Setup (Step-by-Step)](#google-cloud-setup)
3. [Production Configuration](#production-config)
4. [Security Guardrails](#security-guardrails)
5. [Monitoring & Logging](#monitoring)
6. [Compliance & Auditing](#compliance)
7. [Deployment Options](#deployment)
8. [Disaster Recovery](#disaster-recovery)

---

## 🔒 Security Checklist

### Before Going to Production

- [ ] **Credentials Management**
  - [ ] Service account key stored securely (NOT in code)
  - [ ] Keys rotated every 90 days
  - [ ] Old keys deleted from Google Cloud Console
  - [ ] .gitignore includes `credential.json`
  - [ ] Credentials never logged or exposed

- [ ] **Access Control**
  - [ ] Service account has minimal permissions
  - [ ] Gmail API scope limited to necessary functions
  - [ ] Drive API scope limited to necessary functions
  - [ ] No wildcard permissions
  - [ ] Separate service accounts for dev/staging/prod

- [ ] **Network Security**
  - [ ] TLS/SSL enabled for all connections
  - [ ] API endpoints use HTTPS only
  - [ ] Firewall rules configured
  - [ ] VPN for admin access
  - [ ] Rate limiting configured

- [ ] **Data Protection**
  - [ ] PII data masked in logs
  - [ ] Encryption at rest enabled
  - [ ] Encryption in transit (TLS 1.2+)
  - [ ] No sensitive data in error messages
  - [ ] GDPR compliance verified

- [ ] **Application Security**
  - [ ] Input validation on all endpoints
  - [ ] Output encoding to prevent injection
  - [ ] CORS properly configured
  - [ ] CSRF tokens implemented
  - [ ] Authentication enforced

- [ ] **Monitoring & Alerts**
  - [ ] Audit logging enabled
  - [ ] Real-time alerts configured
  - [ ] Performance monitoring active
  - [ ] Error tracking enabled
  - [ ] Security incident response plan

- [ ] **Code Quality**
  - [ ] All dependencies pinned to specific versions
  - [ ] No known vulnerabilities (run: `pip-audit`)
  - [ ] Code reviewed by security team
  - [ ] Secrets scanning enabled in Git
  - [ ] SAST/DAST testing completed

---

## 🌐 Google Cloud Setup (Step-by-Step)

### Phase 1: Google Cloud Project Creation

#### Step 1.1: Create Project
```bash
# Using Google Cloud Console
1. Go to https://console.cloud.google.com
2. Click "Select a Project" → "New Project"
3. Enter project name: "Gmail-Drive-MCP-Prod"
4. Organization: Select your organization
5. Click "Create"
```

#### Step 1.2: Enable Required APIs
```bash
# In Google Cloud Console:
1. Navigate to "APIs & Services" → "Library"
2. Search for and enable:
   - Gmail API
   - Google Drive API
3. Click "Enable" for each

# Or via gcloud CLI:
gcloud services enable gmail.googleapis.com
gcloud services enable drive.googleapis.com
```

#### Step 1.3: Create Service Account
```bash
# Via Google Cloud Console:
1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Fill in:
   - Service account name: "gmail-drive-mcp-server"
   - Service account ID: "gmail-drive-mcp-server"
   - Description: "MCP Server for Gmail & Drive API access"
4. Click "Create and Continue"

# Or via gcloud CLI:
gcloud iam service-accounts create gmail-drive-mcp-server \
    --display-name="MCP Server for Gmail & Drive API"
```

#### Step 1.4: Configure Service Account Permissions
```bash
# In Google Cloud Console:
1. Click on the created service account
2. Go to "Roles" tab
3. Click "Grant Access"
4. Add these custom roles (or use predefined):
   - Gmail API Editor (custom role)
   - Drive API Editor (custom role)

# Or via gcloud CLI:
gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:gmail-drive-mcp-server@PROJECT_ID.iam.gserviceaccount.com" \
    --role="custom.gmailAPIEditor"
```

#### Step 1.5: Create Service Account Key (JSON)
```bash
# In Google Cloud Console:
1. Click on service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select "JSON"
5. Download the key file
6. Rename to: "credential.json"
7. Move to: backend/credential.json

# Or via gcloud CLI:
gcloud iam service-accounts keys create credential.json \
    --iam-account=gmail-drive-mcp-server@PROJECT_ID.iam.gserviceaccount.com
```

### Phase 2: Configure API Permissions

#### Step 2.1: Gmail API Configuration
```bash
# In Google Cloud Console:
1. Go to "APIs & Services" → "Credentials"
2. Find Gmail API
3. Configure:
   - Allowed referrers: Your domain only
   - Request path: /gmail/v1/users/me/*
   - Rate limiting: 10 requests/sec per user

# Scopes needed:
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]
```

#### Step 2.2: Drive API Configuration
```bash
# In Google Cloud Console:
1. Go to "APIs & Services" → "Credentials"
2. Find Google Drive API
3. Configure:
   - Allowed referrers: Your domain only
   - Request path: /drive/v3/files/*
   - Rate limiting: 1000 requests/sec

# Scopes needed:
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]
```

#### Step 2.3: Enable Audit Logging
```bash
# In Google Cloud Console:
1. Go to "Security" → "Audit Logs"
2. Enable for:
   - Admin Activity
   - Data Access
   - System Events
3. Set log retention: 30 days minimum
```

---

## ⚙️ Production Configuration

### Environment Setup

Create `backend/.env` for production:

```bash
# ============================================
# GOOGLE CLOUD CONFIGURATION
# ============================================
GOOGLE_CREDENTIALS_PATH=credential.json
GOOGLE_PROJECT_ID=gmail-drive-mcp-prod
GOOGLE_SERVICE_ACCOUNT_EMAIL=gmail-drive-mcp-server@PROJECT_ID.iam.gserviceaccount.com

# ============================================
# APPLICATION CONFIGURATION
# ============================================
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
APP_VERSION=1.0.0

# ============================================
# SECURITY CONFIGURATION
# ============================================
# Rate limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=3600  # seconds

# Session management
SESSION_TIMEOUT=3600  # 1 hour
MAX_CONCURRENT_SESSIONS=10

# ============================================
# MONITORING & ALERTING
# ============================================
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
LOG_RETENTION_DAYS=30
ALERT_EMAIL=ops@yourcompany.com

# ============================================
# API CONFIGURATION
# ============================================
GMAIL_API_RATE_LIMIT=10  # requests per second
DRIVE_API_RATE_LIMIT=100  # requests per second
REQUEST_TIMEOUT=30  # seconds

# ============================================
# OPTIONAL: LLM INTEGRATION
# ============================================
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
LLM_TEMPERATURE=0
```

### Docker Configuration

Create `Dockerfile` for containerization:

```dockerfile
# Multi-stage build for production

# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Build wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels

# Install wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY backend/ .
COPY credential.json .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "mcp_server.py"]
```

### Kubernetes Configuration

Create `k8s-deployment.yaml` for Kubernetes:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: gmail-drive-mcp-secret
type: Opaque
stringData:
  credential.json: |
    # Paste your service account JSON here
  
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gmail-drive-mcp-server
  labels:
    app: gmail-drive-mcp-server
    version: v1
spec:
  replicas: 3  # HA configuration
  selector:
    matchLabels:
      app: gmail-drive-mcp-server
  template:
    metadata:
      labels:
        app: gmail-drive-mcp-server
    spec:
      serviceAccountName: gmail-drive-mcp-sa
      
      # Security context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsReadOnlyRootFilesystem: true
      
      containers:
      - name: mcp-server
        image: your-registry/gmail-drive-mcp:latest
        imagePullPolicy: Always
        
        # Resource limits
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        
        # Ports
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        
        # Environment variables
        env:
        - name: DEBUG
          value: "false"
        - name: LOG_LEVEL
          value: "INFO"
        - name: ENVIRONMENT
          value: "production"
        
        # Mount secrets
        volumeMounts:
        - name: credentials
          mountPath: /app/credential.json
          subPath: credential.json
          readOnly: true
        - name: tmp
          mountPath: /tmp
        
        # Health checks
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
      
      # Volumes
      volumes:
      - name: credentials
        secret:
          secretName: gmail-drive-mcp-secret
          defaultMode: 0400  # Read-only
      - name: tmp
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: gmail-drive-mcp-service
spec:
  selector:
    app: gmail-drive-mcp-server
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP

---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: gmail-drive-mcp-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: gmail-drive-mcp-server
```

---

## 🛡️ Security Guardrails

### 1. Input Validation

```python
# Add to mcp_server.py

import re
from typing import Tuple

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email address format and format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 254:
        return False, "Email too long"
    
    return True, ""


def validate_query(query: str, max_length: int = 2048) -> Tuple[bool, str]:
    """Validate search query to prevent injection attacks"""
    if not query:
        return False, "Query cannot be empty"
    
    if len(query) > max_length:
        return False, f"Query exceeds max length of {max_length}"
    
    # Block dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '`', '$', '|', ';', '&']
    for char in dangerous_chars:
        if char in query:
            return False, f"Query contains invalid character: {char}"
    
    return True, ""
```

### 2. Rate Limiting

```python
# Add to mcp_server.py

from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    """Rate limiter to prevent API abuse"""
    
    def __init__(self, requests_per_second: int = 10):
        self.requests_per_second = requests_per_second
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=1)
        
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= self.requests_per_second:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True

# Initialize rate limiter
rate_limiter = RateLimiter(requests_per_second=10)
```

### 3. Audit Logging

```python
# Add to mcp_server.py

import logging
import json
from datetime import datetime

# Configure logging for audit trail
audit_logger = logging.getLogger("audit")

class AuditLog:
    """Log all API calls for compliance and security"""
    
    @staticmethod
    def log_tool_call(tool_name: str, user_id: str, args: dict, result: dict):
        """Log tool usage for audit trail"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool_name,
            "user_id": user_id,
            "success": result.get("success", False),
            "action": tool_name,
            # Mask sensitive data
            "args": {k: "***" for k in args},  # Don't log args
            "status": "success" if result.get("success") else "error"
        }
        
        audit_logger.info(json.dumps(log_entry))
        
        # Also send to external audit service
        # Example: send_to_audit_service(log_entry)
```

### 4. Encryption

```python
# Add encryption at rest for sensitive data

from cryptography.fernet import Fernet
import os

class EncryptedStorage:
    """Encrypt sensitive data at rest"""
    
    def __init__(self):
        # Get encryption key from environment (securely)
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY not set in environment")
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Usage
encrypted_storage = EncryptedStorage()
encrypted_email = encrypted_storage.encrypt("user@example.com")
```

---

## 📊 Monitoring & Logging

### Application Monitoring

```python
# Add to mcp_server.py

import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Metrics
request_count = Counter(
    'mcp_requests_total',
    'Total requests',
    ['tool', 'status']
)

request_duration = Histogram(
    'mcp_request_duration_seconds',
    'Request duration',
    ['tool']
)

active_requests = Gauge(
    'mcp_active_requests',
    'Active requests',
    ['tool']
)

api_errors = Counter(
    'mcp_api_errors_total',
    'Total API errors',
    ['tool', 'error_type']
)

# Example: Wrap tool calls with metrics
def track_tool_call(tool_name: str, func):
    async def wrapper(*args, **kwargs):
        active_requests.labels(tool=tool_name).inc()
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            request_count.labels(tool=tool_name, status='success').inc()
            return result
        except Exception as e:
            api_errors.labels(tool=tool_name, error_type=type(e).__name__).inc()
            request_count.labels(tool=tool_name, status='error').inc()
            raise
        finally:
            duration = time.time() - start_time
            request_duration.labels(tool=tool_name).observe(duration)
            active_requests.labels(tool=tool_name).dec()
    
    return wrapper
```

### Alerting Configuration

Create `alerts.yaml`:

```yaml
groups:
- name: mcp_server_alerts
  interval: 30s
  rules:
  
  # High error rate
  - alert: HighErrorRate
    expr: rate(mcp_api_errors_total[5m]) > 0.1
    for: 5m
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors/sec"
  
  # API latency high
  - alert: HighLatency
    expr: histogram_quantile(0.95, mcp_request_duration_seconds) > 5
    for: 5m
    annotations:
      summary: "High API latency"
      description: "95th percentile latency is {{ $value }}s"
  
  # Too many active requests
  - alert: TooManyActiveRequests
    expr: mcp_active_requests > 100
    for: 2m
    annotations:
      summary: "Too many active requests"
      description: "Active requests: {{ $value }}"
```

---

## ✅ Compliance & Auditing

### GDPR Compliance

```python
# Add GDPR compliance functions

class GDPRCompliance:
    """GDPR compliance utilities"""
    
    @staticmethod
    def mask_pii(data: str) -> str:
        """Mask personally identifiable information"""
        import re
        # Mask email addresses
        data = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 
                     '***@***.***', data)
        # Mask phone numbers
        data = re.sub(r'\d{3}-\d{3}-\d{4}', '***-***-****', data)
        # Mask credit card numbers
        data = re.sub(r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}', 
                     '****-****-****-****', data)
        return data
    
    @staticmethod
    def right_to_be_forgotten(user_id: str) -> bool:
        """Implement right to be forgotten"""
        # Delete all user data from logs and databases
        # This should be implemented with your data storage system
        print(f"Deleting all data for user: {user_id}")
        return True
    
    @staticmethod
    def data_portability(user_id: str) -> dict:
        """Export user data for portability"""
        # Collect all user's data
        return {
            "emails": [],
            "drive_files": [],
            "audit_logs": []
        }
```

### Security Testing

Create `security_tests.py`:

```python
"""
Security testing for MCP server
Run: python security_tests.py
"""

import subprocess
import sys

def run_security_checks():
    """Run all security checks"""
    
    print("🔒 Running Security Tests...\n")
    
    # 1. Dependency vulnerability scan
    print("1️⃣  Scanning dependencies for vulnerabilities...")
    result = subprocess.run(
        ["pip-audit"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("❌ Found vulnerabilities!")
        print(result.stdout)
        return False
    print("✅ No vulnerabilities found")
    
    # 2. Secrets scanning
    print("\n2️⃣  Scanning for hardcoded secrets...")
    result = subprocess.run(
        ["detect-secrets", "scan", "--all-files"],
        capture_output=True,
        text=True
    )
    if "secret" in result.stdout.lower():
        print("❌ Found potential secrets in code!")
        print(result.stdout)
        return False
    print("✅ No secrets found")
    
    # 3. Code quality
    print("\n3️⃣  Running code quality checks...")
    result = subprocess.run(
        ["pylint", "backend/mcp_server.py", "--score=y"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
    # 4. Type checking
    print("\n4️⃣  Running type checks...")
    result = subprocess.run(
        ["mypy", "backend/mcp_server.py"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("⚠️  Type errors found:")
        print(result.stdout)
    else:
        print("✅ All type checks passed")
    
    return True

if __name__ == "__main__":
    success = run_security_checks()
    sys.exit(0 if success else 1)
```

---

## 🚀 Deployment Options

### Option 1: Azure Container Apps

```bash
# 1. Create resource group
az group create --name mcp-rg --location eastus

# 2. Create container registry
az acr create --resource-group mcp-rg \
    --name mcpregistry \
    --sku Basic

# 3. Build and push image
az acr build --registry mcpregistry \
    --image gmail-drive-mcp:latest .

# 4. Create container app
az containerapp create \
    --name gmail-drive-mcp \
    --resource-group mcp-rg \
    --image mcpregistry.azurecr.io/gmail-drive-mcp:latest \
    --environment-variables DEBUG=false \
    --secrets credential-json=@credential.json \
    --ingress external \
    --target-port 8000
```

### Option 2: AWS Lambda

```python
# lambda_handler.py for AWS Lambda

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from mcp_server import list_emails, read_email, send_email

def lambda_handler(event, context):
    """AWS Lambda handler"""
    
    try:
        tool_name = event.get("tool")
        args = event.get("args", {})
        
        # Route to appropriate tool
        if tool_name == "list_emails":
            result = list_emails(**args)
        elif tool_name == "read_email":
            result = read_email(**args)
        elif tool_name == "send_email":
            result = send_email(**args)
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown tool: {tool_name}"})
            }
        
        return {
            "statusCode": 200,
            "body": result
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
```

### Option 3: Google Cloud Run

```bash
# 1. Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/gmail-drive-mcp

# 2. Deploy to Cloud Run
gcloud run deploy gmail-drive-mcp \
    --image gcr.io/PROJECT_ID/gmail-drive-mcp \
    --platform managed \
    --region us-central1 \
    --memory 512Mi \
    --timeout 300 \
    --set-env-vars DEBUG=false,LOG_LEVEL=INFO
```

---

## 🔄 Disaster Recovery

### Backup & Recovery Plan

```yaml
Backup Strategy:
  Frequency: Daily
  Retention: 30 days
  
Recovery Procedures:
  RTO (Recovery Time Objective): 1 hour
  RPO (Recovery Point Objective): 1 day
  
Disaster Scenarios:
  1. API Quota Exceeded
     - Action: Implement exponential backoff and retry
     - Prevention: Monitor quota usage continuously
  
  2. Service Account Key Compromised
     - Action: Immediately revoke key, generate new one
     - Prevention: Rotate keys every 90 days
  
  3. Data Loss
     - Action: Restore from daily backups
     - Prevention: Implement data validation
  
  4. Service Degradation
     - Action: Switch to failover region
     - Prevention: Deploy multi-region setup
```

### Health Checks

```python
# Add health check endpoints

@mcp.tool()
def health_check() -> str:
    """Health check endpoint"""
    try:
        # Check Google APIs accessibility
        gmail_service = init_gmail_service()
        drive_service = init_drive_service()
        
        return json.dumps({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "gmail": "up",
                "drive": "up"
            }
        })
    
    except Exception as e:
        return json.dumps({
            "status": "unhealthy",
            "error": str(e)
        })
```

---

## 📋 Pre-Production Checklist

Before deploying to production, verify:

- [ ] All security tests pass
- [ ] Credentials properly secured
- [ ] Rate limiting configured
- [ ] Audit logging enabled
- [ ] Monitoring and alerts active
- [ ] Backup procedures tested
- [ ] Load testing completed (1000+ req/sec)
- [ ] GDPR compliance verified
- [ ] SSL certificates valid
- [ ] API quotas reviewed and set
- [ ] Incident response plan documented
- [ ] Team trained on deployment
- [ ] Rollback procedure tested
- [ ] Documentation complete
- [ ] Performance benchmarks met

---

## 🎯 Success Metrics

Track these metrics in production:

```
Availability:   99.9% uptime
Response Time:  < 2 seconds (95th percentile)
Error Rate:     < 0.1% of requests
API Quota:      < 80% of daily limit
Security:       Zero breaches, all tests passing
Compliance:     100% GDPR compliant
```

---

**Version**: 1.0  
**Last Updated**: 2026-09-13  
**Status**: Production Ready ✅
