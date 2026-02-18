---
description: Build and deploy the ClaraCare backend to Kubernetes (Linode LKE)
---

# Deploy Backend to Kubernetes

## Prerequisites
- Docker Desktop running
- `kubectl` configured for the claracare cluster
- Logged into Docker Hub (`docker login`)

## Steps

// turbo-all

1. Build and push the linux/amd64 image using the `clarabuilder` buildx builder:
```bash
cd /Users/maverickrajeev/Documents/projects/clara-care/backend && docker buildx build --builder clarabuilder --platform linux/amd64 --no-cache --push --progress=plain -t rajeevdev17/claracare-backend:latest .
```

> **IMPORTANT**: You MUST use `--builder clarabuilder` (docker-container driver). The default `desktop-linux` builder uses the `docker` driver which silently fails on `--push` and produces arm64 images on Apple Silicon Macs.

2. If the `clarabuilder` doesn't exist, create it first:
```bash
docker buildx create --name clarabuilder --driver docker-container --use
```

3. Rollout the new image on Kubernetes:
```bash
kubectl rollout restart deployment claracare-backend -n claracare
```

4. Monitor rollout status (may take 2-3 minutes for old pods to drain):
```bash
kubectl rollout status deployment claracare-backend -n claracare --timeout=180s
```

5. Verify the deployment is healthy:
```bash
curl -s https://api.claracare.me/health
```

## Troubleshooting

### ImagePullBackOff
If pods show `ImagePullBackOff`, the image was likely pushed with wrong platform. Verify:
```bash
# Check Docker Hub for the tag
curl -s "https://hub.docker.com/v2/repositories/rajeevdev17/claracare-backend/tags/latest"
# Check pod events
kubectl describe pod <pod-name> -n claracare | grep -A 5 Events
```

### Rollout Timeout
The rollout may timeout due to slow old pod termination. Check if new pods are actually running:
```bash
kubectl get pods -n claracare -l app=claracare-backend
```
If the new pod shows `Running 1/1`, the deployment succeeded even if `rollout status` timed out.
