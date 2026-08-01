# 🚀 Task 1: Automated Docker Build & Push Pipeline

## 🎯 Objective
Set up a fully automated CI/CD pipeline: whenever code is pushed to a private GitHub repository, Jenkins automatically builds a new Docker image and pushes it to a Docker registry — with no manual intervention.

## 🧱 Prerequisites
- A private GitHub repository containing a `Dockerfile` and `Jenkinsfile`
- Jenkins server running (with Docker plugin, GitHub plugin installed: As setup in Task0)
- Docker Hub account (or other registry)

## 🪜 Step-by-Step Walkthrough

### Step 1: Create the Private Repository
- Created a private repo containing:
  - `Dockerfile` — defines how the app image is built
  - `Jenkinsfile` — defines the CI/CD pipeline steps

### Step 2: Generate a Personal Access Token (PAT)
- Went to GitHub → Settings → Developer Settings → Personal Access Tokens
- Generated a PAT (Define Scope and Permissions)
- This token is used by Jenkins to authenticate with the private repo

### Step 3: Add Credentials in Jenkins
- Manage Jenkins → Credentials → Add Credentials
- Added:
  - GitHub PAT (as Secret Text / Username-Password)
  - Docker Hub username & password (as Username-Password credential)

### Step 4: Configure GitHub Webhook
- In the GitHub repo → Settings → Webhooks → Add webhook
- Payload URL: `http://<jenkins-server>/github-webhook/`
- Content type: `application/json`
- Event: Just the push event
- This triggers Jenkins automatically on every push

### Step 5: Configure Jenkins Job
- Created a new Pipeline job
- Under "Build Triggers" → enabled **GitHub hook trigger for GITScm polling**
- Pointed the pipeline to fetch the `Jenkinsfile` from the private repo (using the credential from Step 3)

### Step 6: Jenkinsfile Pipeline Logic
```groovy
pipeline {
    agent any
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds-id')
        IMAGE_NAME = 'yourusername/your-image'
    }
    stages {
        stage('Checkout') {
            steps {
                git credentialsId: 'github-pat-id', url: 'https://github.com/yourusername/your-private-repo.git'
            }
        }
        stage('Build Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME:latest .'
            }
        }
        stage('Push to Docker Hub') {
            steps {
                sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                sh 'docker push $IMAGE_NAME:latest'
            }
        }
    }
    post {
        success {
            echo 'Image built and pushed successfully!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
```

### Step 7: Test the Automation
- Made a code change and pushed to the repo
- Verified Jenkins auto-triggered the build (via webhook)
- Confirmed a new image version appeared in Docker Hub

## ✅ Result
On every `git push`, Jenkins automatically:
1. Pulls latest code from the private repo
2. Builds a new Docker image
3. Pushes it to Docker Hub — fully automated, no manual builds needed

## 🧠 Key Learnings
- How Jenkins integrates with private GitHub repos securely using PATs
- How webhooks enable real-time build triggers instead of polling
- How to safely inject Docker registry credentials into a pipeline
