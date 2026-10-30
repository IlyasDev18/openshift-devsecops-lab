# 🛡️ OpenShift Production DevSecOps Lab

An enterprise-grade, cloud-native microservice deployment on **Red Hat OpenShift**, engineered with automated CI/CD security gates, non-root container compliance, and zero-trust network isolation.

## 📐 System Architecture

```text
                               ┌──────────────────────────────────────────────┐
                               │             GitHub Actions CI/CD             │
                               │                                              │
                               │  [Hadolint] ──► [Trivy Scan] ──► [GHCR Push]  │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ OpenShift Cluster (Namespace: ilyas-dev)                                                               │
│                                                                                                        │
│                          ┌─────────────────────────────────────────┐                                   │
│                          │         OpenShift Ingress Router         │                                   │
│                          └────────────────────┬────────────────────┘                                   │
│                                               │                                                        │
│                                               ▼ (HTTP / Port 8080)                                     │
│                          ┌─────────────────────────────────────────┐                                   │
│                          │          backend-route (Route)          │                                   │
│                          └────────────────────┬────────────────────┘                                   │
│                                               │                                                        │
│                                               ▼                                                        │
│                          ┌─────────────────────────────────────────┐                                   │
│                          │         backend-service (SVC)           │                                   │
│                          └────────────────────┬────────────────────┘                                   │
│                                               │                                                        │
│                                               ▼ (ClusterIP / Port 8080)                                │
│                                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Zero-Trust Isolation Boundary (NetworkPolicy: default-deny)                                      │  │
│  │                                                                                                  │  │
│  │   ┌──────────────────────────────────┐             ┌──────────────────────────────────┐          │  │
│  │   │  Pod 1: backend-app (Replica)    │             │  Pod 2: backend-app (Replica)    │          │  │
│  │   │  - Non-Root Execution (UID 1001) │             │  - Non-Root Execution (UID 1001) │          │  │
│  │   │  - Restricted SCC Compliant      │             │  - Restricted SCC Compliant      │          │  │
│  │   └──────────────────────────────────┘             └──────────────────────────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🔒 Security & Compliance Controls

* **Zero-Trust Network Isolation:** Implements a `default-deny` ingress policy across the namespace. Traffic to application pods is explicitly whitelisted only from allowed sources.
* **Non-Root Execution (SCC):** Containers comply with OpenShift `restricted-v2` Security Context Constraints (SCC) by running under non-privileged user IDs (`UID 1001`) with read-only root filesystems and disabled privilege escalation.
* **Automated Security Gates (CI/CD):**
  * **Dockerfile Linting:** Enforces container best practices using **Hadolint**.
  * **Vulnerabilities Scanning:** Automates OS and library CVE detection via **Trivy** prior to registry publishing.
* **Credential Protection:** Secrets and deployment tokens are secured using GitHub Actions Encrypted Secrets and injected at runtime via ephemeral service tokens.

## 🛠️ Tech Stack & Tooling

| Domain | Technology |
| :--- | :--- |
| **Platform** | Red Hat OpenShift Developer Sandbox |
| **Orchestration** | Kubernetes / OpenShift CLI (`oc`) |
| **CI/CD Automation** | GitHub Actions |
| **Security & Scanning** | Aqua Security Trivy, Hadolint |
| **Container Registry** | GitHub Container Registry (`ghcr.io`) |
| **Runtime & Base** | Docker, Node.js / Express |

## 📂 Repository Structure

```text
openshift-devsecops-lab/
├── .github/
│   └── workflows/
│       └── devsecops-pipeline.yml   # CI/CD pipeline (Lint, Scan, Build, Push)
├── 01-app-deployment/               # Application manifests (Deployment, Service, Route)
├── 02-network-security/             # Security policies (NetworkPolicy)
│   └── networkpolicy.yaml           # Zero-Trust default-deny & ingress rules
├── Dockerfile                       # Non-root container specification
├── package.json
└── README.md
```

## 🚀 CI/CD Pipeline Workflow

The automated pipeline defined in `.github/workflows/devsecops-pipeline.yml` executes on every push to `main` and all Pull Requests:

1. **Lint Phase:** Executes `hadolint` against the `Dockerfile` to detect anti-patterns and security misconfigurations.
2. **Build Phase:** Compiles the container image locally inside the runner context using the Git commit SHA as a unique tag.
3. **Scan Phase:** Executes `trivy` to audit OS packages and application dependencies for `CRITICAL` or `HIGH` vulnerabilities.
4. **Publish Phase:** Authenticates to GitHub Container Registry (`ghcr.io`) using `GITHUB_TOKEN` and pushes dual-tagged images (`:latest` and `:${{ github.sha }}`).

## 📋 Local Setup & Deployment Guide

### Prerequisites

* OpenShift CLI (`oc`) installed locally.
* Access to a Red Hat OpenShift cluster (or OpenShift Developer Sandbox).
* Docker / Podman runtime.

### 1. Authenticate to OpenShift

Retrieve your token from the OpenShift Web Console (**Copy login command**) and run:

```bash
oc login --server=https://api.sandbox-cell-1.openshiftapps.com:6443 --token=sha256~YOUR_TOKEN
```

### 2. Deploy Infrastructure Manifests

```bash
# 1. Target your development project/namespace
oc project ilyas-dev

# 2. Deploy application workloads (Deployments, Services, Routes)
oc apply -f 01-app-deployment/

# 3. Enforce zero-trust network security policies
oc apply -f 02-network-security/
```

### 3. Verify Deployment & Zero-Trust Policies

```bash
# Verify pod health and replica status
oc get pods -l app=backend -o wide

# Verify active routes and get public endpoint URL
oc get routes

# Execute zero-trust testing (Authorized vs. Unauthorized traffic)
# Authorized test pod:
oc run test-allowed --image=curlimages/curl --labels="app=frontend" --restart=Never -- rm -rf /
oc exec test-allowed -- curl -s --connect-timeout 3 http://backend-service:8080/healthz

# Unauthorized test pod (Should time out / be dropped by NetworkPolicy):
oc run test-blocked --image=curlimages/curl --labels="app=unauthorized" --restart=Never -- rm -rf /
oc exec test-blocked -- curl -s --connect-timeout 3 http://backend-service:8080/healthz
```
