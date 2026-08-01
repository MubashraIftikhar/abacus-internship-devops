# ☸️ Kubernetes

## 📌 Why Kubernetes When We Already Have Docker?

Docker lets you package and run applications in containers — but running containers manually becomes unmanageable at scale (multiple containers, multiple hosts, crashes, traffic spikes). **Kubernetes (K8s)** is a container **orchestration platform** that automates deployment, scaling, networking, and management of containerized applications across a cluster of machines.

### 🎯 Key Benefits Over Plain Docker

| Benefit | Description |
|---|---|
| **Automated Scheduling** | Automatically places containers (pods) onto available nodes based on resource requirements, without manual intervention |
| **Self-Healing** | Automatically restarts failed containers, replaces unhealthy pods, and reschedules pods from failed nodes |
| **Rollouts & Rollbacks** | Deploys new versions gradually (rolling updates) and can instantly revert to a previous stable version if something breaks |
| **Scaling** | Manually or automatically scales the number of running pod replicas up/down based on load (Horizontal Pod Autoscaler) |
| **Load Balancing** | Automatically distributes network traffic across multiple pod replicas to prevent overload on a single instance |

## 🏗️ Kubernetes Architecture

<img width="518" height="260" alt="image" src="https://github.com/user-attachments/assets/06c4740c-a4e5-44ac-9d64-6d7b214d6711" />


**Control Plane Components:**
- **API Server** – Front-end of the cluster; all commands (kubectl, internal components) go through it
- **etcd** – Distributed key-value store holding the entire cluster's state/configuration
- **Scheduler** – Decides which node a newly created pod should run on
- **Controller Manager** – Runs controllers that ensure the cluster's actual state matches the desired state (e.g., restarting failed pods)

**Worker Node Components:**
- **Kubelet** – Agent on each node that ensures containers are running as expected
- **Kube-proxy** – Manages networking rules, enabling communication to/from pods
- **Pods** – Smallest deployable unit, wraps one or more containers

## ❤️ Health Probes

Kubernetes uses probes to monitor container health and readiness:

| Probe | Purpose |
|---|---|
| **Startup Probe** | Checks if the application inside the container has **started successfully**. Other probes are disabled until this passes — useful for slow-starting apps |
| **Liveness Probe** | Checks if the container is still **running/healthy**. If it fails, Kubernetes **restarts** the container |
| **Readiness Probe** | Checks if the container is **ready to accept traffic**. If it fails, the pod is removed from service load balancing (but not restarted) |


## 🔄 Pod Lifecycle

| Phase | Description |
|---|---|
| **Pending** | Pod has been accepted by the cluster but one or more containers aren't set up/running yet (e.g., still pulling images or waiting to be scheduled) |
| **Running** | Pod has been scheduled to a node, and at least one container is running |
| **Succeeded** | All containers in the pod terminated successfully and won't be restarted (common for jobs/batch tasks) |
| **Failed** | All containers terminated, and at least one container failed (non-zero exit) |

## 📄 A Simple YAML File — Explained

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:latest
          ports:
            - containerPort: 80
```

| Field | Explanation |
|---|---|
| `apiVersion` | Specifies which version of the Kubernetes API to use for this object (e.g., `apps/v1` for Deployments, `v1` for core objects like Pods/Services) |
| `kind` | The type of Kubernetes object being created (Deployment, Pod, Service, etc.) |
| `metadata` | Data that identifies the object — name, labels, namespace |
| `spec` | The desired state of the object — what you want Kubernetes to achieve/maintain |
| `replicas` | Number of identical pod copies to run |
| `selector` | How the Deployment finds which pods it manages (matches labels) |
| `template` | The pod blueprint — its own metadata and spec, used to create each replica |
| `containers` | List of containers to run inside the pod, including image and exposed ports |

## 🚀 Workload Types

| Type | What It Is | Use Case | Benefits |
|---|---|---|---|
| **Deployment** | Manages stateless pods, ensures a specified number of replicas are running | Web servers, APIs, stateless microservices | Easy rolling updates/rollbacks, self-healing, scaling |
| **StatefulSet** | Manages stateful pods with stable, unique network identities and persistent storage | Databases (MySQL, MongoDB), apps needing stable identity/storage | Ordered deployment/scaling, stable pod names, persistent volumes tied to each pod |
| **DaemonSet** | Ensures a copy of a pod runs on **every** (or selected) node in the cluster | Log collectors, monitoring agents, node-level networking tools | Automatic deployment to new nodes, guarantees one instance per node |

## 🌐 Service Types

Services expose pods to network traffic — either within the cluster or externally.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
```

| Service Type | What It Is | Use Case | Benefits |
|---|---|---|---|
| **ClusterIP** (default) | Exposes the service on an internal IP, reachable only within the cluster | Internal communication between microservices (e.g., backend talking to database) | Simple, secure — no external exposure needed |
| **NodePort** | Exposes the service on a static port on each node's IP | Basic external access for dev/testing environments | Easy to set up, doesn't require a cloud load balancer |
| **ExternalIP** | Routes traffic arriving at a specific external IP (manually assigned) to the service | When traffic needs to reach the cluster via a specific pre-existing external IP | Direct control over which external IP routes to the service |
| **LoadBalancer** | Provisions an external load balancer (via cloud provider) that routes traffic to the service | Production-grade external access to a service | Automatic external IP provisioning, built-in load distribution across pods |

## 🔐 ConfigMaps & Secrets

| | ConfigMap | Secret |
|---|---|---|
| **Purpose** | Stores non-sensitive configuration data (key-value pairs) | Stores sensitive data (passwords, tokens, keys) |
| **Storage** | Stored as plain text | Stored as Base64-encoded (not encrypted by default, but access-controlled) |
| **Use Case** | App configuration like environment variables, config files, feature flags | Database credentials, API keys, TLS certificates |

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: production
  LOG_LEVEL: info
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=      # base64 encoded
  password: cGFzc3dvcmQ=  # base64 encoded
```
