## Pipeline Stages & Security Gates

[ Commit / Push ]
│
▼
┌───────────────────┐
│  1. Hadolint      │ ──► Validates Dockerfile syntax & non-root user rules
└─────────┬─────────┘
│ (Pass)
▼
┌───────────────────┐
│  2. Trivy Scan    │ ──► Scans image OS/packages for HIGH/CRITICAL CVEs
└─────────┬─────────┘     (Build fails automatically if vulnerabilities are found)
│ (Pass)
▼
┌───────────────────┐
│  3. GHCR Push     │ ──► Publishes signed container image to GitHub Registry
└─────────┬─────────┘
│
▼
┌───────────────────┐
│  4. OpenShift     │ ──► Applies deployment.yaml & NetworkPolicies via oc apply
└───────────────────┘