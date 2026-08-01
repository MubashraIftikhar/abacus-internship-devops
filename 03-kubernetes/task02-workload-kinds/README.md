# Kubernetes Workload Kinds — StatefulSet vs Deployment

## Goal
To understand the difference between **StatefulSets** and **Deployments** in Kubernetes by testing how each one handles data when a pod is deleted and recreated.

## What We Did
1. Created a **StatefulSet** (`mysql`) with 3 replicas, using `volumeClaimTemplates` so each pod gets its own PVC mounted at `/var/lib/mysql`.
2. Created a **Deployment** (`nginx-deployment`) with 3 replicas, using an `emptyDir` volume mounted at `/usr/share/nginx/html`.
3. Wrote data into a pod in each case, deleted the pod, waited for it to come back, and checked if the data was still there.

## How We Achieved It
- **MySQL (StatefulSet):**
  - Wrote a row into the database (`mysql-0`).
  - Deleted `mysql-0`.
  - After it restarted, queried the database again — the data was still there.
  - Reason: the PVC (and its underlying PV) exists independently of the pod. The new pod just remounted the same PVC.

- **Nginx (Deployment):**
  - Wrote a test file (`index.html`) inside one nginx pod.
  - Deleted that pod.
  - After a new pod was created, checked for the file — it was gone.
  - Reason: `emptyDir` storage is tied to the pod's lifecycle. A new pod means a brand-new empty volume; nothing carries over.

## Why This Matters
- **StatefulSets** give each replica its own stable identity and storage (PVC), so data survives pod restarts — this is why databases run as StatefulSets.
- **Deployments** treat pods as disposable and interchangeable. Without a real PVC attached, any data written inside a pod is lost when it's replaced.
- This is the core reason stateful apps (databases, message queues) use StatefulSets, while stateless apps (web servers, APIs) use Deployments.

## Commands Used
```bash
# Apply workloads
kubectl apply -f mysql-statefulset.yaml
kubectl apply -f nginx-deployment.yaml

# Check pods/PVCs
kubectl get pods
kubectl get pvc

# Write & verify data (MySQL)
kubectl exec -it mysql-0 -- mysql -uroot -ppassword -e "CREATE DATABASE test; USE test; CREATE TABLE t(id INT); INSERT INTO t VALUES(1);"
kubectl exec -it mysql-0 -- mysql -uroot -ppassword -e "SELECT * FROM test.t;"

# Write & verify data (Nginx)
kubectl exec -it $POD -- sh -c "echo 'hello persistence test' > /usr/share/nginx/html/index.html"
kubectl exec -it $POD -- cat /usr/share/nginx/html/index.html

# Delete pod and observe behavior after recreation
kubectl delete pod <pod-name>
kubectl get pods -w
```
