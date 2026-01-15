# Event Horizon - Deployment Guide

Complete guide for deploying Event Horizon multi-agent system on various platforms.

---

## Table of Contents

1. [Quick Start (Docker)](#quick-start-docker)
2. [Deployment Platforms](#deployment-platforms)
   - [AWS (Amazon Web Services)](#1-aws-amazon-web-services)
   - [Google Cloud Platform (GCP)](#2-google-cloud-platform-gcp)
   - [Microsoft Azure](#3-microsoft-azure)
   - [Kubernetes (Any Cloud)](#4-kubernetes-any-cloud)
   - [Digital Ocean](#5-digital-ocean)
   - [Heroku](#6-heroku)
   - [Railway](#7-railway)
   - [Fly.io](#8-flyio)
3. [Scheduled Execution](#scheduled-execution)
4. [Scaling Architecture](#scaling-architecture)

---

## Quick Start (Docker)

### Local Development

```bash
# Build image
docker build -t event-horizon:latest .

# Run with config
docker-compose -f docker-compose.dev.yml up
```

### Production (Local)

```bash
# Build and run
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

---

## Deployment Platforms

## 1. AWS (Amazon Web Services)

### Option A: AWS ECS (Elastic Container Service)

**Best for**: Managed container orchestration, easy scaling

**Setup**:

```bash
# 1. Install AWS CLI
pip install awscli

# 2. Configure AWS
aws configure

# 3. Create ECR repository
aws ecr create-repository --repository-name event-horizon

# 4. Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# 5. Build and tag
docker build -t event-horizon:latest .
docker tag event-horizon:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/event-horizon:latest

# 6. Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/event-horizon:latest
```

**ECS Task Definition** (`ecs-task-definition.json`):

```json
{
  "family": "event-horizon",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "event-horizon",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/event-horizon:latest",
      "essential": true,
      "environment": [
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {
          "name": "NEWS_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account>:secret:event-horizon/news-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/event-horizon",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Deploy**:

```bash
# Create cluster
aws ecs create-cluster --cluster-name event-horizon-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster event-horizon-cluster \
  --service-name event-horizon-service \
  --task-definition event-horizon \
  --desired-count 1 \
  --launch-type FARGATE
```

**Cost**: ~$30-50/month (Fargate with 1 vCPU, 2GB RAM)

---

### Option B: AWS Lambda (Serverless)

**Best for**: Scheduled runs, cost optimization (pay per execution)

**Setup**:

1. Package code with dependencies:
```bash
pip install -r requirements.txt -t lambda_package/
cp -r agents services utils main.py config.yaml lambda_package/
cd lambda_package && zip -r ../event-horizon-lambda.zip . && cd ..
```

2. Create Lambda function:
```bash
aws lambda create-function \
  --function-name event-horizon \
  --runtime python3.11 \
  --role arn:aws:iam::<account>:role/lambda-execution-role \
  --handler lambda_handler.handler \
  --zip-file fileb://event-horizon-lambda.zip \
  --timeout 900 \
  --memory-size 1024
```

3. Set up EventBridge trigger for scheduled execution:
```bash
# Run daily at 9 AM UTC
aws events put-rule \
  --name event-horizon-daily \
  --schedule-expression "cron(0 9 * * ? *)"

aws events put-targets \
  --rule event-horizon-daily \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:<account>:function:event-horizon"
```

**Cost**: ~$5-10/month (for daily runs)

---

### Option C: AWS EC2

**Best for**: Full control, long-running processes

```bash
# 1. Launch EC2 instance (t3.medium or larger)
# 2. SSH into instance
ssh -i key.pem ec2-user@<instance-ip>

# 3. Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# 4. Clone repository and run
git clone <your-repo>
cd Event-Horizon
docker-compose -f docker-compose.prod.yml up -d
```

**Cost**: ~$30-40/month (t3.medium)

---

## 2. Google Cloud Platform (GCP)

### Option A: Cloud Run (Serverless Containers)

**Best for**: Auto-scaling, pay-per-use

```bash
# 1. Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# 2. Initialize
gcloud init

# 3. Build and push to Artifact Registry
gcloud builds submit --tag gcr.io/<project-id>/event-horizon

# 4. Deploy to Cloud Run
gcloud run deploy event-horizon \
  --image gcr.io/<project-id>/event-horizon \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --set-env-vars NEWS_API_KEY=<key>
```

**Scheduled Execution**:
```bash
# Create Cloud Scheduler job (daily at 9 AM)
gcloud scheduler jobs create http event-horizon-daily \
  --schedule="0 9 * * *" \
  --uri="https://event-horizon-<hash>-uc.a.run.app" \
  --http-method=POST
```

**Cost**: ~$5-15/month (pay per execution)

---

### Option B: GKE (Google Kubernetes Engine)

```bash
# 1. Create cluster
gcloud container clusters create event-horizon-cluster \
  --num-nodes=2 \
  --machine-type=n1-standard-2 \
  --region=us-central1

# 2. Get credentials
gcloud container clusters get-credentials event-horizon-cluster

# 3. Deploy (see Kubernetes section below)
kubectl apply -f k8s/
```

**Cost**: ~$70-100/month (2 nodes)

---

## 3. Microsoft Azure

### Option A: Azure Container Instances (ACI)

**Best for**: Simple container deployment

```bash
# 1. Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 2. Login
az login

# 3. Create resource group
az group create --name event-horizon-rg --location eastus

# 4. Create Azure Container Registry
az acr create --resource-group event-horizon-rg \
  --name eventhorizonacr --sku Basic

# 5. Build and push
az acr build --registry eventhorizonacr \
  --image event-horizon:latest .

# 6. Deploy
az container create \
  --resource-group event-horizon-rg \
  --name event-horizon \
  --image eventhorizonacr.azurecr.io/event-horizon:latest \
  --cpu 2 \
  --memory 4 \
  --restart-policy OnFailure \
  --environment-variables NEWS_API_KEY=<key>
```

**Cost**: ~$30-50/month

---

### Option B: Azure Kubernetes Service (AKS)

```bash
# Create AKS cluster
az aks create \
  --resource-group event-horizon-rg \
  --name event-horizon-cluster \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --enable-addons monitoring

# Get credentials
az aks get-credentials --resource-group event-horizon-rg --name event-horizon-cluster

# Deploy
kubectl apply -f k8s/
```

**Cost**: ~$100-150/month

---

## 4. Kubernetes (Any Cloud)

**Best for**: Production scale, multi-agent orchestration

### Kubernetes Manifests

**`k8s/namespace.yaml`**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: event-horizon
```

**`k8s/configmap.yaml`**:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: event-horizon-config
  namespace: event-horizon
data:
  config.yaml: |
    agents:
      news_agent:
        enabled: false
      report_agent:
        enabled: true
    # ... rest of config
```

**`k8s/secret.yaml`**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: event-horizon-secrets
  namespace: event-horizon
type: Opaque
stringData:
  NEWS_API_KEY: "your-api-key-here"
```

**`k8s/deployment.yaml`**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: event-horizon
  namespace: event-horizon
spec:
  replicas: 1
  selector:
    matchLabels:
      app: event-horizon
  template:
    metadata:
      labels:
        app: event-horizon
    spec:
      containers:
      - name: event-horizon
        image: event-horizon:latest
        imagePullPolicy: Always
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        env:
        - name: NEWS_API_KEY
          valueFrom:
            secretKeyRef:
              name: event-horizon-secrets
              key: NEWS_API_KEY
        - name: LOG_LEVEL
          value: "INFO"
        volumeMounts:
        - name: config
          mountPath: /app/config.yaml
          subPath: config.yaml
        - name: results
          mountPath: /app/results
      volumes:
      - name: config
        configMap:
          name: event-horizon-config
      - name: results
        persistentVolumeClaim:
          claimName: event-horizon-results-pvc
```

**`k8s/cronjob.yaml`** (for scheduled execution):
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: event-horizon-daily
  namespace: event-horizon
spec:
  schedule: "0 9 * * *"  # Daily at 9 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: event-horizon
            image: event-horizon:latest
            envFrom:
            - secretRef:
                name: event-horizon-secrets
            volumeMounts:
            - name: config
              mountPath: /app/config.yaml
              subPath: config.yaml
          restartPolicy: OnFailure
          volumes:
          - name: config
            configMap:
              name: event-horizon-config
```

**Deploy**:
```bash
# Apply all manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n event-horizon
kubectl logs -f deployment/event-horizon -n event-horizon
```

---

## 5. Digital Ocean

**Best for**: Simple, affordable cloud

```bash
# 1. Install doctl
brew install doctl  # or download from digitalocean.com

# 2. Authenticate
doctl auth init

# 3. Create Droplet with Docker
doctl compute droplet create event-horizon \
  --image docker-20-04 \
  --size s-2vcpu-4gb \
  --region nyc1

# 4. SSH and deploy
ssh root@<droplet-ip>
git clone <your-repo>
cd Event-Horizon
docker-compose -f docker-compose.prod.yml up -d
```

**Cost**: ~$24/month (2 vCPU, 4GB RAM)

---

## 6. Heroku

**Best for**: Quick deployment, CI/CD

```bash
# 1. Install Heroku CLI
brew install heroku/brew/heroku

# 2. Login
heroku login

# 3. Create app
heroku create event-horizon-app

# 4. Add container registry
heroku container:login

# 5. Build and push
heroku container:push web -a event-horizon-app
heroku container:release web -a event-horizon-app

# 6. Set environment variables
heroku config:set NEWS_API_KEY=<key> -a event-horizon-app

# 7. Schedule with Heroku Scheduler
heroku addons:create scheduler:standard -a event-horizon-app
heroku addons:open scheduler -a event-horizon-app
# Add job: python main.py
```

**Cost**: ~$25-50/month (Hobby/Standard dynos)

---

## 7. Railway

**Best for**: Modern, simple deployment

1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Railway auto-detects Dockerfile
4. Add environment variables in dashboard
5. Deploy automatically on push

**Cost**: ~$5-20/month (pay-as-you-go)

---

## 8. Fly.io

**Best for**: Edge deployment, global distribution

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Login
flyctl auth login

# 3. Launch app
flyctl launch

# 4. Set secrets
flyctl secrets set NEWS_API_KEY=<key>

# 5. Deploy
flyctl deploy
```

**Cost**: ~$0-10/month (free tier available)

---

## Scheduled Execution

### Option 1: Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add line (daily at 9 AM)
0 9 * * * cd /path/to/Event-Horizon && docker-compose -f docker-compose.prod.yml up >> logs/cron.log 2>&1
```

### Option 2: GitHub Actions

**`.github/workflows/daily-run.yml`**:
```yaml
name: Daily Agent Run

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  run-agents:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: docker build -t event-horizon:latest .

      - name: Run agents
        env:
          NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
        run: |
          docker run --rm \
            -e NEWS_API_KEY=$NEWS_API_KEY \
            -v $(pwd)/results:/app/results \
            event-horizon:latest

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: agent-results
          path: results/
```

---

## Scaling Architecture

### Single Agent (Current)

```
┌─────────────────┐
│   Docker        │
│  ┌───────────┐  │
│  │  main.py  │  │
│  │           │  │
│  │  - News   │  │
│  │  - Report │  │
│  └───────────┘  │
└─────────────────┘
```

### Multiple Agents (Future)

```
┌────────────────────────────────────────┐
│         Kubernetes Cluster             │
│                                        │
│  ┌─────────────┐    ┌──────────────┐  │
│  │ News Agent  │    │ Report Agent │  │
│  │  (Pod 1)    │    │   (Pod 2)    │  │
│  └─────────────┘    └──────────────┘  │
│                                        │
│  ┌─────────────┐    ┌──────────────┐  │
│  │ Sentiment   │    │ Technical    │  │
│  │   Agent     │    │  Analysis    │  │
│  │  (Pod 3)    │    │   Agent      │  │
│  └─────────────┘    └──────────────┘  │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │      Orchestrator Service        │ │
│  │  (Coordinates all agents)        │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │      Message Queue (Redis)       │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │      Database (PostgreSQL)       │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

**See `docs/multi-agent-architecture.md` for detailed scaling guide**

---

## Comparison Table

| Platform | Cost/Month | Ease of Setup | Scalability | Best For |
|----------|------------|---------------|-------------|----------|
| **AWS Lambda** | $5-10 | Medium | Auto | Scheduled jobs |
| **AWS ECS** | $30-50 | Medium | High | Production |
| **AWS EC2** | $30-40 | Easy | Medium | Full control |
| **GCP Cloud Run** | $5-15 | Easy | Auto | Serverless |
| **GCP GKE** | $70-100 | Hard | Very High | Large scale |
| **Azure ACI** | $30-50 | Easy | Medium | Simple deployment |
| **Azure AKS** | $100-150 | Hard | Very High | Enterprise |
| **Digital Ocean** | $24 | Easy | Medium | Small/medium |
| **Heroku** | $25-50 | Very Easy | Medium | Quick start |
| **Railway** | $5-20 | Very Easy | Medium | Modern apps |
| **Fly.io** | $0-10 | Easy | High | Edge/global |

---

## Recommendations

### For Learning/Testing:
→ **Railway** or **Fly.io** (free tier, easy)

### For Small Production:
→ **Digital Ocean** or **AWS Lambda** (affordable, simple)

### For Medium Production:
→ **AWS ECS** or **GCP Cloud Run** (managed, scalable)

### For Large Scale:
→ **Kubernetes (GKE/EKS/AKS)** (full control, multi-agent)

### For Cost Optimization:
→ **AWS Lambda** or **GCP Cloud Run** (pay per execution)

---

## Next Steps

1. **Choose platform** based on your needs
2. **Set up CI/CD** for automatic deployments
3. **Add monitoring** (Prometheus, Datadog, CloudWatch)
4. **Scale to multiple agents** (see `docs/multi-agent-architecture.md`)
5. **Add database** for persistence
6. **Implement API** for external access

Ready to deploy? Pick a platform and follow the guide above!
