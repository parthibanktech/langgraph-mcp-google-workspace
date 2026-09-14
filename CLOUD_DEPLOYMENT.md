# ☁️ Dual Local & Cloud Deployment Guide (AWS EC2)

This guide explains how to manage and deploy the **Gmail & Google Drive MCP Server** across **both Local environment and AWS EC2 Cloud** seamlessly without changing codebase or hardcoding IP addresses.

---

## 🌟 Why Dual Deployment Works Out-Of-The-Box

The application uses an **Nginx Reverse Proxy Architecture**:
- All frontend API calls use **relative paths** (e.g. `/api/gmail/list`, `/api/chat`).
- On **Local Machine**, requests to `http://localhost:5173/api/...` are proxied to `http://backend:8000`.
- On **AWS EC2 Cloud**, requests to `http://<EC2-PUBLIC-IP>/api/...` are proxied to `http://backend:8000` inside the Docker network.
- **Zero code changes** are required when switching between Local and AWS EC2 Cloud!

---

## 🛡️ AWS Security Group Setup

Your AWS EC2 Security Group inbound rules are configured correctly as per your setup:

| Type | Protocol | Port Range | Source | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **HTTP** | TCP | `80` | `0.0.0.0/0` | Main Web App access (`http://<EC2-PUBLIC-IP>`) |
| **Custom TCP** | TCP | `5173` | `0.0.0.0/0` | Alternative Web App access (`http://<EC2-PUBLIC-IP>:5173`) |
| **Custom TCP** | TCP | `8000` | `0.0.0.0/0` | Interactive Swagger API Docs (`http://<EC2-PUBLIC-IP>:8000/docs`) |
| **SSH** | TCP | `22` | `0.0.0.0/0` | Remote SSH terminal management |

---

## 🚀 Step-by-Step Deployment Workflow

### 1. Local Machine Development
Run and test changes on your local computer:

```bash
# Start local containers
docker compose up --build -d

# Local Access URLs:
# React Dashboard:   http://localhost:5173
# Swagger API Docs:  http://localhost:8000/docs
```

When you add new code or features locally:
```bash
git add .
git commit -m "Update features for local & cloud"
git push origin main
```

---

### 2. Deploying to AWS EC2 Cloud Server

#### Step 2.1: SSH into your AWS EC2 Instance
```bash
ssh -i your-key.pem ubuntu@<YOUR_EC2_PUBLIC_IP>
```

#### Step 2.2: Clone or Pull Latest Code
```bash
# First time setup on EC2:
git clone <YOUR_GIT_REPOSITORY_URL>
cd gmail_agent_development

# For subsequent updates on EC2:
git pull origin main
```

#### Step 2.3: Copy Google Credentials to EC2
Ensure `credential.json` and `token.json` are placed in `backend/`:
```bash
# Option A: Copy using SCP from your local machine
scp -i your-key.pem backend/credential.json ubuntu@<YOUR_EC2_PUBLIC_IP>:~/gmail_agent_development/backend/

# Option B: Create directly on EC2
nano backend/credential.json
```

#### Step 2.4: Launch with Docker Compose on EC2
```bash
docker compose up --build -d
```

---

## 📊 Summary Matrix: Local vs. Cloud URLs

| Interface | Local Machine | AWS EC2 Cloud |
| :--- | :--- | :--- |
| **Web Dashboard (Port 80)** | `http://localhost` | `http://<EC2-PUBLIC-IP>` |
| **Web Dashboard (Port 5173)** | `http://localhost:5173` | `http://<EC2-PUBLIC-IP>:5173` |
| **Swagger REST API Docs** | `http://localhost:8000/docs` | `http://<EC2-PUBLIC-IP>:8000/docs` |
| **Backend Health Check** | `http://localhost:8000/health` | `http://<EC2-PUBLIC-IP>:8000/health` |

---

## 🔄 Synchronizing Local and Cloud Environments

- **Single Command Cloud Update**:
  Whenever you push local updates to GitHub/GitLab, SSH into EC2 and run:
  ```bash
  git pull && docker compose up --build -d
  ```
- **Automated Jenkins CI/CD Pipeline**:
  A production [`Jenkinsfile`](file:///d:/AI_AGENT_HACKTHON/5.0/Gmail%20Assistant%20Langraph%20MCP%20Server/gmail_agent_development/Jenkinsfile) is included in the project root. It automates:
  1. Source Code Checkout
  2. Docker Compose Config Validation (`docker compose config`)
  3. Image Construction (`docker compose build`)
  4. Healthcheck Verification (`curl http://localhost:8000/health`)
  5. Zero-Downtime Deployment (`docker compose up -d`)
- **OAuth Callback Domain**:
  If using Google OAuth Web Flow, add both `http://localhost:5173` and `http://<EC2-PUBLIC-IP>:5173` under **Authorized JavaScript origins** in Google Cloud Console.
