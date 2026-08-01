\# 🐳 Docker



\## 📌 What is Docker?



Docker is an open-source containerization platform that allows developers to package applications along with all their dependencies (libraries, configs, runtime) into a single lightweight, portable unit called a \*\*container\*\*. Unlike virtual machines, containers share the host OS kernel, making them faster to start and much more resource-efficient. This ensures the application runs consistently across different environments — "it works on my machine" problems are eliminated.



\## 🏗️ Docker Architecture



Docker follows a \*\*client-server architecture\*\*:



```mermaid

graph LR

&#x20;   A\[Docker Client<br/>CLI] -->|REST API| B\[Docker Daemon<br/>dockerd]

&#x20;   B --> C\[Images]

&#x20;   B --> D\[Containers]

&#x20;   B --> E\[Networks]

&#x20;   B --> F\[Volumes]

&#x20;   B <-->|pull/push| G\[Docker Registry<br/>Docker Hub]

```



\*\*Components:\*\*

\- \*\*Docker Client\*\* – The CLI/tool used to interact with Docker (`docker build`, `docker run`, etc.)

\- \*\*Docker Daemon (dockerd)\*\* – Background service that manages images, containers, networks, and volumes

\- \*\*Docker Registry\*\* – Stores Docker images (e.g., Docker Hub); used to pull/push images

\- \*\*Docker Objects\*\* – Images, Containers, Networks, Volumes



\## 🧩 Core Concepts



| Concept | Description |

|---|---|

| \*\*Dockerfile\*\* | A text file containing step-by-step instructions to build a Docker image (base image, dependencies, commands, ports, etc.) |

| \*\*Docker Image\*\* | A read-only template/blueprint used to create containers. Built from a Dockerfile. |

| \*\*Docker Container\*\* | A running (or stopped) instance of an image — the actual isolated environment where the app executes |

| \*\*Docker Hub\*\* | A cloud-based registry where Docker images are stored and shared publicly/privately |



\## ⚙️ Docker Networking



Docker provides several network drivers:



| Network Type | Description |

|---|---|

| \*\*Bridge\*\* (default) | Containers on the same host can communicate via an internal private network |

| \*\*Host\*\* | Container shares the host's network stack directly (no isolation) |

| \*\*None\*\* | Container has no network access |

| \*\*Overlay\*\* | Used for multi-host communication, typically in Docker Swarm |



```bash

docker network ls

docker network create my\_network

docker network inspect my\_network

```



\## 💾 Docker Volumes vs Docker Mounts



| Docker Volumes | Bind Mounts |

|---|---|

| Managed entirely by Docker (stored in `/var/lib/docker/volumes`) | Maps a specific host directory/file into the container |

| Easier to back up, migrate, and share between containers | Directly tied to host filesystem structure |

| Recommended for persistent data | Useful for local development (live code reload, etc.) |



```bash

docker volume create my\_volume

docker run -v my\_volume:/app/data myapp

docker run -v /host/path:/container/path myapp   # bind mount

```



\## 🚀 Image Optimization Techniques



\- \*\*Multi-stage builds\*\* – Separate build and runtime stages to keep final image small

\- \*\*Use slim/alpine base images\*\* – e.g., `python:3.11-slim` instead of `python:3.11`

\- \*\*.dockerignore\*\* – Exclude unnecessary files (like `.git`, `node\_modules`) from build context

\- \*\*Minimize layers\*\* – Combine `RUN` commands using `\&\&` to reduce image layers

\- \*\*Order instructions properly\*\* – Place less-frequently changed instructions (like installing dependencies) before frequently changed ones (like copying source code) to leverage build cache



```dockerfile

\# Example: Multi-stage build

FROM node:18 AS build

WORKDIR /app

COPY . .

RUN npm install \&\& npm run build



FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

```



\## 💻 Useful Commands



```bash

\# Images

docker build -t myapp .

docker images

docker rmi <image\_id>



\# Containers

docker run -d -p 8080:80 --name mycontainer myapp

docker ps                  # running containers

docker ps -a                # all containers

docker stop <container\_id>

docker start <container\_id>

docker restart <container\_id>

docker rm <container\_id>



\# Logs \& Debugging

docker logs <container\_id>

docker exec -it <container\_id> bash



\# System

docker system prune         # clean up unused data

docker inspect <container\_id>

```



\## ❓ Interview Questions \& Answers



\*\*Q1. CMD vs ENTRYPOINT — what's the difference?\*\*

> `CMD` provides default arguments/commands that \*\*can be overridden\*\* when running the container (`docker run myapp <new-command>`). `ENTRYPOINT` defines a fixed command that \*\*always executes\*\*, and any arguments passed at runtime are appended to it rather than replacing it. They're often used together — `ENTRYPOINT` sets the executable, `CMD` sets default arguments.



\*\*Q2. docker run vs docker start — what's the difference?\*\*

> `docker run` creates a \*\*new container\*\* from an image and starts it. `docker start` restarts an \*\*existing (stopped) container\*\* without creating a new one.



\*\*Q3. docker start vs docker exec — what's the difference?\*\*

> `docker start` simply resumes a stopped container's main process. `docker exec` runs an \*\*additional command inside an already running container\*\* (e.g., opening a shell for debugging) without affecting the main process.



\## 📚 Resources

\- \[Docker Docs](https://docs.docker.com/)

\- GeeksforGeeks Docker Tutorial (referenced for learning)

