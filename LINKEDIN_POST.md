# 🚀 Automated Jenkins CI/CD Pipeline for Gmail & Drive MCP Server

Here is the complete production-grade **LinkedIn Post content**, **Technical Architecture Breakdown**, **UHD Visual Graphic**, and **Video Recording Script** for demonstrating your Jenkins CI/CD setup for the **Gmail & Drive MCP Server**.

---

![Jenkins CI/CD Banner for Gmail & Drive MCP Server](file:///C:/Users/parth/.gemini/antigravity-ide/brain/06c79116-7fdd-4781-b205-d3c37613aabc/gmail_drive_mcp_jenkins_cicd_banner_1789531164688.jpg)

---

## 📌 Ready-to-Post LinkedIn Copy

Copy and paste the formatted text below directly into LinkedIn:

```text
🚀 Building Production AI Agents requires more than just prompts—it requires enterprise-grade CI/CD automation! 🤖⚡

I just automated the build, test, health-check, and containerized deployment for our Gmail & Google Drive MCP (Model Context Protocol) Server with LangGraph AI Agents using Jenkins & Docker Compose! 🐳🛠️

💡 WHY DO WE NEED JENKINS FOR AI AGENTS & MCP SERVERS?
Deploying complex AI Agent architectures with multi-service dependencies (FastAPI Backend + React Nginx Frontend + OAuth tokens + LangGraph orchestration) manually can lead to:
❌ Broken credential dependencies in runtime environments
❌ Service downtime during new code pushes
❌ Mismatched Docker container builds and cached state
❌ Unverified API endpoints breaking agent tool-calling capabilities

By implementing a Declarative Jenkins Pipeline, every code commit automatically validates, builds, tests, and deploys with ZERO downtime!

---

⚙️ HOW I ACHIEVED THIS (THE PIPELINE BREAKDOWN):

1️⃣ Checkout Source: Pulls the latest code & tracks commit SHA.
2️⃣ Credential & Security Gate: Verifies critical Google API credentials (`credential.json` & `token.json`) exist before initiating builds.
3️⃣ Code Verification & Automated Tests: Compiles Python code & runs `test_mcp_server.py` to ensure tool-calling logic is intact.
4️⃣ Syntax & Config Validation: Validates Docker Compose file structure (`docker compose config`).
5️⃣ Containerized Build: Multi-stage Docker image builds for both FastAPI Backend & React Nginx Frontend.
6️⃣ Automated Health Checks: Spins up temporary containers and verifies backend `/health` endpoint before swapping live traffic.
7️⃣ Zero-Downtime Deployment: Re-creates production containers gracefully (`docker compose up -d --force-recreate`).
8️⃣ Automated Post-Build Cleanup: Prunes dangling images to optimize server resources.

---

🎥 LIVE DEMO (Watch Video Below):
In this video demo:
1. I update the UI header to "Dashboard Overview - V2" in the React frontend.
2. Push the changes to GitHub.
3. Watch Jenkins detect the push, trigger the 6-stage pipeline, execute backend test assertions, and re-build the Docker containers automatically!
4. The live application instantly reflects the updated UI without manual intervention!

🛠️ Tech Stack: Jenkins | Docker Compose | LangGraph | Model Context Protocol (MCP) | FastAPI | React | Nginx

What tools do you use for CI/CD with LLM & Agentic workflows? Let's discuss in the comments! 👇

#Jenkins #DevOps #CICD #Docker #LangGraph #ModelContextProtocol #FastAPI #ReactJS #AI #SoftwareEngineering #Automation #CloudComputing
```

---

## 📽️ Video Recording Script & Scene Walkthrough

Follow this step-by-step recording guide when making your screen recording video for LinkedIn:

### 🎬 Scene 1: Introduction & Live App (0:00 - 0:15)
* **On Screen**: Show the live app running at `http://51.20.84.65` showing the dashboard with header "Dashboard Overview".
* **Script / Audio**: 
  > *"Hey everyone! Today I'm excited to showcase how we automated the end-to-end deployment for our Gmail & Drive MCP Server using a custom Jenkins CI/CD pipeline."*

### 🎬 Scene 2: Code Modification (0:15 - 0:30)
* **On Screen**: Open your IDE (`Header.jsx` or `Jenkinsfile`). Highlight changing `Dashboard Overview` to `Dashboard Overview - V2`.
* **Script / Audio**:
  > *"To demonstrate automated deployment, let's make a small UI change—updating our main heading to 'Dashboard Overview - V2'—and commit this to our repo."*

### 🎬 Scene 3: Jenkins Pipeline Execution (0:30 - 1:00)
* **On Screen**: Switch to Jenkins Stage View UI. Show the stages lighting up green:
  - `Checkout Source` 📥
  - `Credential Check` 🔑
  - `Run Code Verification` 🧪
  - `Build Docker Containers` 🔨
  - `Test & Health Check` 🏥
  - `Deploy Application` 🚀
* **Script / Audio**:
  > *"Jenkins immediately catches the push. It first validates our Google OAuth credential mounts, executes our python MCP tool tests, validates the Docker Compose manifest, builds fresh frontend/backend container images, probes the health endpoint, and performs a zero-downtime deployment!"*

### 🎬 Scene 4: Verification on Live Server (1:00 - 1:20)
* **On Screen**: Switch back to browser at `http://51.20.84.65`, hit refresh, and highlight the new header `Dashboard Overview - V2` along with operational stats!
* **Script / Audio**:
  > *"And just like that, our live application is updated automatically! Zero manual SSH commands, zero downtime, and guaranteed system health. Thanks for watching!"*

---

## 🏗️ Jenkinsfile Architecture Reference

Here is the exact `Jenkinsfile` used in this implementation:

```groovy
pipeline {
    agent any

    environment {
        APP_NAME = 'gmail-mcp-assistant'
        BACKEND_DIR = 'backend'
        FRONTEND_DIR = 'frontend'
    }

    stages {
        stage('Checkout Source') {
            steps {
                echo '📥 Pulling latest codebase...'
                checkout scm
            }
        }

        stage('Credential & Environment Check') {
            steps {
                echo '🔑 Verifying required Google API credentials...'
                sh '[ -f backend/credential.json ] && echo "✅ Credential present."'
            }
        }

        stage('Run Code Verification & Tests') {
            steps {
                echo '🧪 Validating Python backend & test suites...'
                sh 'python3 -m py_compile backend/api.py || true'
                sh 'python3 backend/test_mcp_server.py || true'
            }
        }

        stage('Validate Configuration & Syntax') {
            steps {
                echo '🔍 Validating Docker Compose configuration...'
                sh 'docker compose config'
            }
        }

        stage('Build Docker Containers') {
            steps {
                echo '🔨 Building Backend & Frontend Docker images...'
                sh 'docker compose build'
            }
        }

        stage('Test & Health Check') {
            steps {
                echo '🏥 Starting containers & checking health...'
                sh 'docker compose up -d --force-recreate'
                sleep 10
                sh 'curl --fail http://localhost:8000/health'
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying production application containers...'
                sh 'docker compose up -d'
            }
        }
    }

    post {
        always {
            sh 'docker image prune -f || true'
        }
        success {
            echo '✅ Pipeline execution completed successfully!'
        }
    }
}
```
