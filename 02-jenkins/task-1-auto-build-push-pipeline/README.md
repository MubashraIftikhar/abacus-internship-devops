# 🚀 Task 1: Automated Docker Build & Push Pipeline

## 🎯 Objective
Set up a fully automated CI/CD pipeline: whenever code is pushed to a private GitHub repository, Jenkins automatically builds a new Docker image and pushes it to a Docker registry — with no manual intervention.

## 🧱 Prerequisites
- A private GitHub repository containing a `Dockerfile` and `Jenkinsfile`
- Jenkins server running (with Docker plugin, GitHub plugin installed: As setup in Task0)
- Docker Hub account (or other registry)
- ngrok (to expose local Jenkins to the internet for GitHub webhooks)

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

| Field | Value |
|---|---|
| Kind | Username with password |
| Username | GitHub username |
| Password | Personal Access Token |
| ID | `github-creds` |

### Step 4: Expose Jenkins to the Internet via ngrok
Since GitHub needs to reach Jenkins over the internet, exposed the local Jenkins instance using ngrok:

```bash
ngrok config add-authtoken <token>
ngrok http 8080
```
Generated a forwarding URL like `https://xxxx.ngrok-free.dev`

> ⚠️ Free ngrok plans generate a new URL each restart — the GitHub webhook must be updated whenever this URL changes.

### Step 5: Configure GitHub Webhook
- In the GitHub repo → Settings → Webhooks → Add webhook
- Payload URL: `https://<ngrok-url>/github-webhook/`
- Content type: `application/json`
- Event: Just the push event
- This triggers Jenkins automatically on every push

### Step 6: Configure Jenkins Job
- Created a new Pipeline job
- Under "Build Triggers" → enabled **GitHub hook trigger for GITScm polling**
- Pointed the pipeline to fetch the `Jenkinsfile` from the private repo (using the credential from Step 3)

### Pipeline Configuration
| Setting        | Value                    |
| -------------- | ------------------------ |
| Definition     | Pipeline script from SCM |
| SCM            | Git                      |
| Repository URL | <username>/<repo>.git    |
| Credentials    | github-creds             |
| Branch         | */main                   |
| Script Path    | Jenkinsfile              |

### Step 7: Jenkinsfile Pipeline Logic
File Attached for reference

### Step 8: Test the Automation
- Made a code change and pushed to the repo
- Verified Jenkins auto-triggered the build (via webhook)
- Confirmed a new image version appeared in Docker Hub

## ✅ Result
After the push:
1. GitHub sends a webhook request.
2. Jenkins automatically starts a new pipeline.
3. Jenkins checks out the latest code.
4. A new Docker image is built.
5. The previous container is removed.
6. A new container is deployed.

## 🧠 Key Learnings
- How Jenkins integrates with private GitHub repos securely using PATs
- How webhooks enable real-time build triggers instead of polling
- How to safely inject Docker registry credentials into a pipeline
- How ngrok exposes a local Jenkins instance so GitHub webhooks can reach it
