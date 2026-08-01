# Kubernetes Service Types — Hands-On Test Bench
 
A small Flask-based GUI deployed on a Minikube cluster (running inside a VMware Workstation VM) to visually test and understand the three core Kubernetes Service types: **ClusterIP**, **NodePort**, and **LoadBalancer** — including how (and why) each one is or isn't reachable from outside the cluster.
 
---
 
## 🎯 Goal
 
Kubernetes Service types are usually taught abstractly ("ClusterIP is internal-only," "NodePort exposes a port on every node," etc.), but that's hard to *feel* until you've tried to actually break through the networking yourself. The goal of this project was to:
 
1. Deploy a real, multi-replica application on a local Minikube cluster.
2. Expose that same application through all three Service types simultaneously.
3. Physically test connectivity from three different vantage points — inside a Pod, from the VM's own OS, and from an external host machine outside the VM — to see exactly where each Service type succeeds or fails.
4. Build a visual tool that proves load-balancing is actually happening across replicas, rather than just trusting that it does.
---
