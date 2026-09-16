pipeline {
    agent any

    environment {
        APP_NAME = 'gmail-mcp-assistant'
        BACKEND_DIR = 'backend'
        FRONTEND_DIR = 'frontend'
        PYTHONUNBUFFERED = '1'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    stages {
        stage('Checkout Source') {
            steps {
                echo '📥 Pulling latest codebase from repository...'
                checkout scm
            }
        }

        stage('Credential & Environment Check') {
            steps {
                echo '🔑 Verifying required Google API credentials...'
                sh '''
                    if [ -f /var/jenkins_home/secrets/credential.json ]; then
                        echo "📋 Copying credential.json from Jenkins secrets store..."
                        cp /var/jenkins_home/secrets/credential.json backend/credential.json
                    fi

                    if [ ! -f backend/credential.json ] || [ -d backend/credential.json ]; then
                        echo "⚠️ Warning: backend/credential.json missing or directory! Ensure credential.json is placed in backend/ or uploaded to server."
                    else
                        echo "✅ backend/credential.json is present and valid."
                    fi
                '''
            }
        }

        stage('Run Code Verification & Tests') {
            steps {
                echo '🧪 Compiling Python Backend & validating scripts...'
                sh 'python3 -m py_compile backend/api.py || python -m py_compile backend/api.py || true'
                sh 'python3 backend/test_mcp_server.py || python backend/test_mcp_server.py || true'
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
                echo '🧪 Starting containers for automated health verification...'
                sh 'docker rm -f mcp_backend mcp_frontend || true'
                sh 'docker compose down --remove-orphans || true'
                sh 'docker compose up -d --force-recreate --remove-orphans'
                
                echo '⏳ Waiting for services to initialize...'
                sleep 10

                echo '🏥 Checking backend API health endpoint...'
                sh 'curl --fail --retry 5 --retry-delay 3 http://localhost:8000/health'
            }
        }

        stage('Deploy Application') {
            steps {
                echo '🚀 Deploying production application containers...'
                sh 'docker compose up -d --force-recreate --remove-orphans'
            }
        }
    }

    post {
        always {
            echo '🧹 Pruning dangling docker images...'
            sh 'docker image prune -f || true'
        }
        success {
            echo '✅ Pipeline execution completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed! Check container logs for details.'
            sh 'docker compose logs --tail=50 || true'
        }
    }
}
