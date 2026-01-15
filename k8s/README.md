# Kubernetes Manifests for Event Horizon

Deploy Event Horizon on Kubernetes (any cloud provider).

---

## Quick Start

### 1. Build and Push Docker Image

```bash
# Build image
docker build -t event-horizon:latest .

# Tag for your registry
docker tag event-horizon:latest your-registry.com/event-horizon:latest

# Push
docker push your-registry.com/event-horizon:latest
```

### 2. Update Image Reference

Edit `deployment.yaml` and `cronjob.yaml`:
```yaml
image: your-registry.com/event-horizon:latest
```

### 3. Configure Secrets

Edit `secret.yaml` and add your API keys:
```yaml
stringData:
  NEWS_API_KEY: "your-actual-api-key-here"
```

### 4. Deploy

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check status
kubectl get all -n event-horizon

# View logs
kubectl logs -f deployment/event-horizon -n event-horizon
```

---

## Files Overview

| File | Purpose |
|------|---------|
| `namespace.yaml` | Creates event-horizon namespace |
| `configmap.yaml` | Configuration (config.yaml) |
| `secret.yaml` | API keys and secrets |
| `pvc.yaml` | Persistent storage for results/logs |
| `deployment.yaml` | Main application deployment |
| `cronjob.yaml` | Scheduled execution (daily at 9 AM) |

---

## Deployment Options

### Option 1: Long-Running Deployment

Use `deployment.yaml` for a service that runs continuously.

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
```

**When to use**: API service, webhook listener, real-time processing

---

### Option 2: Scheduled CronJob

Use `cronjob.yaml` for periodic execution.

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f pvc.yaml
kubectl apply -f cronjob.yaml
```

**When to use**: Daily reports, scheduled analysis

---

### Option 3: Both

Run both deployment and cronjob together.

```bash
kubectl apply -f k8s/
```

---

## Configuration

### Change Schedule

Edit `cronjob.yaml`:

```yaml
# Daily at 9 AM UTC
schedule: "0 9 * * *"

# Every hour
# schedule: "0 * * * *"

# Every 6 hours
# schedule: "0 */6 * * *"
```

[Cron syntax reference](https://crontab.guru/)

---

### Change Resources

Edit `deployment.yaml` or `cronjob.yaml`:

```yaml
resources:
  requests:
    memory: "1Gi"   # Minimum required
    cpu: "500m"
  limits:
    memory: "2Gi"   # Maximum allowed
    cpu: "2000m"
```

---

### Enable/Disable Agents

Edit `configmap.yaml`:

```yaml
agents:
  news_agent:
    enabled: false  # ← Change to true/false

  report_agent:
    enabled: true   # ← Change to true/false
```

Apply changes:
```bash
kubectl apply -f k8s/configmap.yaml
kubectl rollout restart deployment/event-horizon -n event-horizon
```

---

## Monitoring

### View Logs

```bash
# Deployment logs
kubectl logs -f deployment/event-horizon -n event-horizon

# CronJob logs (latest run)
kubectl logs -f job/event-horizon-daily-<job-id> -n event-horizon

# All jobs
kubectl get jobs -n event-horizon
```

### Check Status

```bash
# All resources
kubectl get all -n event-horizon

# Pods
kubectl get pods -n event-horizon

# Deployments
kubectl get deployments -n event-horizon

# CronJobs
kubectl get cronjobs -n event-horizon

# Jobs
kubectl get jobs -n event-horizon
```

### Describe Resources

```bash
# Pod details
kubectl describe pod <pod-name> -n event-horizon

# Deployment details
kubectl describe deployment event-horizon -n event-horizon

# CronJob details
kubectl describe cronjob event-horizon-daily -n event-horizon
```

---

## Scaling

### Scale Deployment

```bash
# Scale to 3 replicas
kubectl scale deployment event-horizon --replicas=3 -n event-horizon

# Auto-scale (HPA)
kubectl autoscale deployment event-horizon \
  --cpu-percent=70 \
  --min=1 \
  --max=5 \
  -n event-horizon
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n event-horizon

# Common issues:
# - Image pull error: Check image name and registry credentials
# - Resource limits: Increase memory/CPU limits
# - ConfigMap/Secret missing: Apply those first
```

### CronJob Not Running

```bash
# Check cronjob
kubectl describe cronjob event-horizon-daily -n event-horizon

# Manual trigger
kubectl create job event-horizon-manual \
  --from=cronjob/event-horizon-daily \
  -n event-horizon

# Check schedule syntax
# Use https://crontab.guru/ to validate
```

### Out of Memory

Increase memory limits in `deployment.yaml`:
```yaml
resources:
  limits:
    memory: "4Gi"  # Increase from 2Gi
```

### Secrets Not Found

```bash
# Check if secret exists
kubectl get secret event-horizon-secrets -n event-horizon

# Recreate secret
kubectl delete secret event-horizon-secrets -n event-horizon
kubectl apply -f secret.yaml
```

---

## Updating

### Update Configuration

```bash
# Edit configmap
kubectl edit configmap event-horizon-config -n event-horizon

# Or apply updated file
kubectl apply -f configmap.yaml

# Restart deployment
kubectl rollout restart deployment/event-horizon -n event-horizon
```

### Update Image

```bash
# Build and push new image
docker build -t your-registry.com/event-horizon:v2 .
docker push your-registry.com/event-horizon:v2

# Update deployment
kubectl set image deployment/event-horizon \
  event-horizon=your-registry.com/event-horizon:v2 \
  -n event-horizon

# Check rollout status
kubectl rollout status deployment/event-horizon -n event-horizon
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/event-horizon -n event-horizon

# Rollback to specific revision
kubectl rollout undo deployment/event-horizon --to-revision=2 -n event-horizon

# View rollout history
kubectl rollout history deployment/event-horizon -n event-horizon
```

---

## Cleanup

### Delete Everything

```bash
# Delete all resources in namespace
kubectl delete namespace event-horizon

# Or delete individual resources
kubectl delete -f k8s/
```

### Delete Only CronJob

```bash
kubectl delete cronjob event-horizon-daily -n event-horizon
```

---

## Cloud-Specific Notes

### AWS EKS

```bash
# Create cluster
eksctl create cluster --name event-horizon --region us-east-1

# Get context
aws eks update-kubeconfig --name event-horizon --region us-east-1

# Deploy
kubectl apply -f k8s/
```

### Google Cloud GKE

```bash
# Create cluster
gcloud container clusters create event-horizon-cluster \
  --num-nodes=2 --region=us-central1

# Get credentials
gcloud container clusters get-credentials event-horizon-cluster

# Deploy
kubectl apply -f k8s/
```

### Azure AKS

```bash
# Create cluster
az aks create --resource-group event-horizon-rg \
  --name event-horizon-cluster --node-count 2

# Get credentials
az aks get-credentials --resource-group event-horizon-rg \
  --name event-horizon-cluster

# Deploy
kubectl apply -f k8s/
```

---

## Production Checklist

- [ ] Use private container registry
- [ ] Set appropriate resource limits
- [ ] Configure proper secrets management (AWS Secrets Manager, etc.)
- [ ] Enable monitoring (Prometheus, Datadog)
- [ ] Configure log aggregation (ELK, Loki)
- [ ] Set up backup for PVCs
- [ ] Configure network policies
- [ ] Enable pod security policies
- [ ] Set up ingress/load balancer if needed
- [ ] Configure auto-scaling (HPA)
- [ ] Set up alerts for failures

---

## Next Steps

1. Deploy to test cluster first
2. Monitor logs and resource usage
3. Adjust resource limits as needed
4. Set up monitoring and alerts
5. Configure backup strategy
6. Plan for scaling (see `docs/multi-agent-architecture.md`)

Ready to deploy? Start with `kubectl apply -f k8s/`!
