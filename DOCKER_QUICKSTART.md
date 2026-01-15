# Event Horizon - Docker Quick Start

Get Event Horizon running in Docker in 5 minutes!

---

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

---

## Quick Start (3 Commands)

```bash
# 1. Build the image
docker build -t event-horizon:latest .

# 2. Run the container
docker run --rm \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/results:/app/results \
  event-horizon:latest

# 3. Check results
ls results/
```

That's it! Results are in the `results/` directory.

---

## Using Docker Compose (Recommended)

### Development

```bash
# Start
docker-compose -f docker-compose.dev.yml up

# Stop
docker-compose -f docker-compose.dev.yml down
```

### Production

```bash
# Start (detached)
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

---

## Configuration

### Set API Keys

Create `.env` file:
```bash
NEWS_API_KEY=your_key_here
```

Or pass as environment variable:
```bash
docker run -e NEWS_API_KEY=your_key event-horizon:latest
```

### Enable/Disable Agents

Edit `config.yaml`:
```yaml
agents:
  news_agent:
    enabled: false  # ← OFF

  report_agent:
    enabled: true   # ← ON
```

---

## Common Commands

### Build Image

```bash
docker build -t event-horizon:latest .
```

### Run Once

```bash
docker run --rm event-horizon:latest
```

### Run with Volume Mounts

```bash
docker run --rm \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/results:/app/results \
  event-horizon:latest
```

### Run Interactively

```bash
docker run -it --rm event-horizon:latest /bin/bash
```

### View Logs

```bash
# If using docker-compose
docker-compose logs -f

# If using docker run
docker logs -f <container-id>
```

---

## Deployment Platforms

Choose where to deploy:

1. **[AWS](#deploy-to-aws)** - ECS, Lambda, or EC2
2. **[Google Cloud](#deploy-to-google-cloud)** - Cloud Run or GKE
3. **[Azure](#deploy-to-azure)** - ACI or AKS
4. **[Kubernetes](#deploy-to-kubernetes)** - Any cloud
5. **[Digital Ocean](#deploy-to-digital-ocean)** - Droplets
6. **[Heroku](#deploy-to-heroku)** - Simple PaaS
7. **[Railway](#deploy-to-railway)** - Modern deployment
8. **[Fly.io](#deploy-to-flyio)** - Edge deployment

**See `DEPLOYMENT.md` for detailed guides for each platform.**

---

## Deploy to AWS

### Option 1: AWS ECS (Recommended)

```bash
# 1. Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag event-horizon:latest \
  <account>.dkr.ecr.us-east-1.amazonaws.com/event-horizon:latest

docker push <account>.dkr.ecr.us-east-1.amazonaws.com/event-horizon:latest

# 2. Deploy to ECS
aws ecs create-service --cli-input-json file://ecs-task-definition.json
```

**Cost**: ~$30-50/month

### Option 2: AWS Lambda (Cheapest)

```bash
# Package and deploy
zip -r lambda.zip .
aws lambda create-function --function-name event-horizon \
  --zip-file fileb://lambda.zip --handler lambda_handler.handler
```

**Cost**: ~$5-10/month (pay per execution)

---

## Deploy to Google Cloud

### Cloud Run (Serverless)

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/<project>/event-horizon
gcloud run deploy event-horizon \
  --image gcr.io/<project>/event-horizon \
  --platform managed
```

**Cost**: ~$5-15/month (pay per use)

---

## Deploy to Azure

### Azure Container Instances

```bash
az container create \
  --resource-group event-horizon-rg \
  --name event-horizon \
  --image event-horizon:latest \
  --cpu 2 --memory 4
```

**Cost**: ~$30-50/month

---

## Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n event-horizon
```

**Cost**: Depends on cluster size (~$70-150/month)

---

## Deploy to Digital Ocean

```bash
# Create droplet with Docker
doctl compute droplet create event-horizon \
  --image docker-20-04 \
  --size s-2vcpu-4gb

# SSH and run
ssh root@<droplet-ip>
docker run -d event-horizon:latest
```

**Cost**: ~$24/month

---

## Deploy to Heroku

```bash
heroku container:login
heroku container:push web -a event-horizon-app
heroku container:release web -a event-horizon-app
```

**Cost**: ~$25-50/month

---

## Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Connect GitHub repo
3. Deploy automatically

**Cost**: ~$5-20/month

---

## Deploy to Fly.io

```bash
flyctl launch
flyctl deploy
```

**Cost**: ~$0-10/month (free tier available)

---

## Scheduled Execution

### Option 1: Kubernetes CronJob

```bash
kubectl apply -f k8s/cronjob.yaml
```

Runs daily at 9 AM automatically.

### Option 2: AWS EventBridge

```bash
aws events put-rule --name event-horizon-daily \
  --schedule-expression "cron(0 9 * * ? *)"
```

### Option 3: Cron (Linux)

```bash
crontab -e
# Add: 0 9 * * * docker run event-horizon:latest
```

---

## Scaling Architecture

### Current (2-5 agents)
```
Single Docker Container
└── All agents run sequentially
```

### Future (10+ agents)
```
Kubernetes Cluster
├── Agent 1 (Pod)
├── Agent 2 (Pod)
├── Agent 3 (Pod)
├── Agent N (Pod)
└── Orchestrator (coordinates)
```

**See `docs/multi-agent-architecture.md` for scaling guide**

---

## Troubleshooting

### Image won't build

```bash
# Clear cache and rebuild
docker build --no-cache -t event-horizon:latest .
```

### Container exits immediately

```bash
# Check logs
docker logs <container-id>

# Run interactively
docker run -it event-horizon:latest /bin/bash
```

### Config not found

```bash
# Make sure config.yaml exists
ls config.yaml

# Mount it properly
docker run -v $(pwd)/config.yaml:/app/config.yaml event-horizon:latest
```

### Results not saved

```bash
# Mount results directory
docker run -v $(pwd)/results:/app/results event-horizon:latest
```

---

## File Structure

```
Event-Horizon/
├── Dockerfile                    # Main Docker image
├── .dockerignore                 # Files to exclude
├── docker-compose.yml            # Default compose
├── docker-compose.dev.yml        # Development
├── docker-compose.prod.yml       # Production
├── config.yaml                   # Configuration
├── config.dev.yaml               # Dev config
├── config.prod.yaml              # Prod config
└── k8s/                          # Kubernetes manifests
    ├── namespace.yaml
    ├── configmap.yaml
    ├── secret.yaml
    ├── deployment.yaml
    ├── cronjob.yaml
    └── README.md
```

---

## Next Steps

1. **Choose deployment platform** (see DEPLOYMENT.md)
2. **Set up CI/CD** for automatic deployments
3. **Add more agents** (see docs/multi-agent-architecture.md)
4. **Monitor** with Prometheus/Datadog
5. **Scale** with Kubernetes when needed

---

## Quick Reference

### Build
```bash
docker build -t event-horizon:latest .
```

### Run
```bash
docker run --rm event-horizon:latest
```

### Run with Config
```bash
docker run --rm \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/results:/app/results \
  event-horizon:latest
```

### Compose Dev
```bash
docker-compose -f docker-compose.dev.yml up
```

### Compose Prod
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Deploy to Cloud
```bash
# See DEPLOYMENT.md for detailed platform guides
```

---

## Resources

- **Full Deployment Guide**: `DEPLOYMENT.md`
- **Scaling Guide**: `docs/multi-agent-architecture.md`
- **Configuration Guide**: `docs/configuration-guide.md`
- **Kubernetes Guide**: `k8s/README.md`

---

Ready to deploy? Pick a platform and go! 🚀
