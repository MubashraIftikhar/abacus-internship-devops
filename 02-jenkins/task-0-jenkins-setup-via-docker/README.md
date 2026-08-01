\# ⚙️ Task 0: Jenkins Setup via Multi-Stage Dockerfile



\## 🎯 Objective

Build and deploy a custom Jenkins Docker image using a multi-stage Dockerfile with pre-installed plugins and persistent storage, resulting in a fully functional Jenkins server running inside a container.



\## 🧱 Prerequisites

\- Docker installed and running



\## 🪜 Step-by-Step Walkthrough



\### Step 1: Create Project Directory

```bash

mkdir jenkins-docker

cd jenkins-docker

```



\### Step 2: Create Multi-Stage Dockerfile



```dockerfile

\# Stage 1: Download Jenkins plugins

FROM jenkins/jenkins:lts AS plugin-builder

USER jenkins

RUN jenkins-plugin-cli \\

&#x20;   --plugins "git workflow-aggregator docker-workflow" \\

&#x20;   --plugin-download-directory /tmp/plugins



\# Stage 2: Final image

FROM jenkins/jenkins:lts

COPY --from=plugin-builder --chown=jenkins:jenkins \\

&#x20;   /tmp/plugins/ /usr/share/jenkins/ref/plugins/

USER jenkins

VOLUME /var/jenkins\_home

```



\*\*Why multi-stage?\*\*

\- \*\*Stage 1\*\* downloads required plugins (`git`, `workflow-aggregator`, `docker-workflow`) using `jenkins-plugin-cli`

\- \*\*Stage 2\*\* copies only the plugins into a clean Jenkins image — keeping the final image lean and running as non-root



\### Step 3: Build the Image

```bash

docker build -t jenkins:multistage .

```



\### Step 4: Create a Persistent Volume

```bash

docker volume create jenkins\_home

```

> Stores Jenkins config, plugins, jobs, credentials, and build history — independent of the container lifecycle.



\### Step 5: Run the Jenkins Container

```powershell

docker run -d `

&#x20; --name jenkins `

&#x20; -p 8080:8080 `

&#x20; -p 50000:50000 `

&#x20; -v jenkins\_home:/var/jenkins\_home `

&#x20; jenkins:multistage

```



| Flag | Purpose |

|---|---|

| `-p 8080:8080` | Jenkins web UI |

| `-p 50000:50000` | Inbound agent communication |

| `-v jenkins\_home:/var/jenkins\_home` | Persists Jenkins data via named volume |



\### Step 6: Retrieve Initial Admin Password

```bash

docker exec jenkins cat /var/jenkins\_home/secrets/initialAdminPassword

```



\### Step 7: Complete Setup Wizard

\- Opened `http://localhost:8080`

\- Entered the initial admin password

\- Installed recommended plugins (pre-installed ones from Dockerfile were already available)

\- Created a custom administrator account



\## 🔁 Data Persistence Verification

To confirm Jenkins data survives container recreation:



```bash

docker rm -f jenkins



docker run -d \\

&#x20; --name jenkins \\

&#x20; -p 8080:8080 \\

&#x20; -p 50000:50000 \\

&#x20; -v jenkins\_home:/var/jenkins\_home \\

&#x20; jenkins:multistage

```



Reopening `http://localhost:8080` showed the same admin account, plugins, and configuration — confirming all data lives in the \*\*jenkins\_home\*\* volume, not the container itself.



\## ✅ Result

A fully functional, persistent Jenkins server — set up via a lean multi-stage Docker image, with data safely decoupled from the container lifecycle.



\## 📸 Screenshots

\*(Add: docker build output, unlock Jenkins screen, admin setup, running container list)\*



\## 🧠 Key Learnings

\- Multi-stage builds keep final images clean by discarding build-only artifacts

\- Named Docker volumes decouple persistent data from container lifecycle

\- Jenkins' first-run flow: unlock → plugins → admin account creation

