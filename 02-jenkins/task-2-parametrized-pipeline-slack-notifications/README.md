# 🔔 Task 2: Parametrized Pipeline with Slack Notifications

## 🎯 Objective
Build a Jenkins pipeline that accepts user-defined parameters at build time, and integrate it with Slack so the team receives real-time build status notifications (success/failure) directly in a Slack channel.

## 🧱 Prerequisites
- Jenkins server with **Slack Notification Plugin** installed
- A Slack workspace with:
  - A channel created for build notifications (e.g., `#jenkins-builds`)
  - Incoming Webhook / Jenkins CI app configured for that workspace
- Slack **credentials/token** added to Jenkins

## 🪜 Step-by-Step Walkthrough

### Step 1: Install Slack Notification Plugin
- Manage Jenkins → Plugins → Available Plugins
- Installed **Slack Notification Plugin**

### Step 2: Set Up Slack App / Webhook
- Added the **Jenkins CI** app to the Slack workspace (via Slack App Directory)
- Authorized it for the target channel (e.g., `#jenkins-builds`)
- Generated the Slack **Workspace/Team domain** and **Integration Token Credential ID**

### Step 3: Configure Slack in Jenkins Global Settings
- Manage Jenkins → System → Slack section
- Added:
  - Workspace name
  - Default channel (`#jenkins-builds`)
  - Credential (Slack token added via Manage Jenkins → Credentials)
- Tested connection using "Test Connection" button

### Step 4: Create a Parametrized Pipeline
- Created a new Pipeline job
- Enabled **"This project is parameterized"**
- Added parameters (example used):
  - `ENVIRONMENT` (choice: dev / staging / prod)
  - `VERSION_TAG` (string input)

### Step 5: Jenkinsfile — Parameters + Slack Integration

File Attached for refrence

### Step 6: Test the Pipeline
- Triggered "Build with Parameters" manually
- Selected environment + version tag
- Verified:
  - Correct parameter values used inside pipeline stages
  - Slack channel received a formatted success/failure message immediately after build completion

## ✅ Result
Jenkins now supports flexible, user-driven builds through parameters, and the team gets instant visibility into build outcomes via Slack — removing the need to manually check the Jenkins dashboard.

<img width="766" height="397" alt="image" src="https://github.com/user-attachments/assets/2055471c-31fd-4baf-aa2a-a7ddf9ca5e97" />


## 🧠 Key Learnings
- How to make pipelines flexible and reusable using parameters
- How Jenkins integrates with third-party tools (Slack) via plugins
- How the `post` block enables outcome-based actions (success/failure notifications)
