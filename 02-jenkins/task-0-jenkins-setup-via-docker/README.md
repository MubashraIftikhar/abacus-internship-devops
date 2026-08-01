# ⚙️ Task 0: Jenkins Setup via Multi-Stage Dockerfile

## 🎯 Objective

Build and deploy a custom Jenkins Docker image using a multi-stage Dockerfile with persistent storage, resulting in a fully functional Jenkins server running inside a container.

---

## 🧱 Prerequisites

- Docker installed and running

---

## 🪜 Step-by-Step Walkthrough

### Step 1: Create Project Directory

```bash
mkdir jenkins-docker
cd jenkins-docker
```

---

### Step 2: Create Multi-Stage Dockerfile

### Why Multi-Stage?

- **Stage 1** downloads the required plugins (`git`, `workflow-aggregator`, `docker-workflow`) using `jenkins-plugin-cli`.
- **Stage 2** copies only the downloaded plugins into a clean Jenkins image, producing a smaller and cleaner final image while running Jenkins as a non-root user.

---

### Step 3: Build the Image

```bash
docker build -t jenkins:multistage .
```

---

### Step 4: Create a Persistent Volume

```bash
docker volume create jenkins_home
```

> This named volume stores Jenkins configuration, plugins, jobs, credentials, and build history independently of the container lifecycle.

---

### Step 5: Run the Jenkins Container

**PowerShell**

```powershell
docker run -d `
  --name jenkins `
  -p 8080:8080 `
  -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  jenkins:multistage
```

| Flag | Purpose |
|------|---------|
| `-p 8080:8080` | Exposes the Jenkins web interface. |
| `-p 50000:50000` | Enables inbound Jenkins agent communication. |
| `-v jenkins_home:/var/jenkins_home` | Mounts a named volume to persist Jenkins data. |

---

### Step 6: Retrieve the Initial Admin Password

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Copy the generated password.

---

### Step 7: Complete the Jenkins Setup Wizard

1. Open **http://localhost:8080** in your browser.
2. Paste the initial administrator password.
3. Install the recommended plugins (the plugins from the Dockerfile are already available).
4. Create your administrator account.
5. Finish the setup.

---

## 🔁 Data Persistence Verification

To verify that Jenkins data persists even after the container is removed:

```bash
docker rm -f jenkins

docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins:multistage
```

After reopening **http://localhost:8080**, the previously created administrator account, installed plugins, jobs, and configuration were still present, confirming that all Jenkins data is stored in the **jenkins_home** Docker volume rather than inside the container.

---
