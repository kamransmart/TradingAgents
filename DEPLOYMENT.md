# 🚀 Deployment Guide - TradingAgents Web Interface

This guide covers deploying the TradingAgents Chainlit web interface to various cloud platforms.

## Table of Contents

1. [Local Testing](#local-testing)
2. [Railway Deployment](#railway-deployment-easiest)
3. [Render Deployment](#render-deployment)
4. [Google Cloud Run](#google-cloud-run)
5. [AWS ECS/Fargate](#aws-ecsfargate)
6. [Docker Deployment](#docker-deployment-any-platform)

---

## Local Testing

### Prerequisites
- Python 3.11+
- API keys for LLM providers (at least one)
- Optional: Alpha Vantage API key for enhanced data

### Steps

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Run the Chainlit app**:
```bash
chainlit run chainlit_app.py
```

4. **Open your browser**:
- Navigate to: `http://localhost:8000`
- Start chatting with the agents!

---

## Railway Deployment (Easiest) ⭐

**Best for**: Quick deployment, minimal configuration
**Cost**: ~$5-20/month (512MB RAM plan)
**Time**: 5 minutes

### Steps

1. **Sign up at [Railway.app](https://railway.app)**

2. **Install Railway CLI** (optional):
```bash
npm install -g @railway/cli
```

3. **Deploy via CLI**:
```bash
# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set OPENAI_API_KEY=your_key_here
railway variables set ALPHA_VANTAGE_API_KEY=your_key_here

# Deploy
railway up
```

4. **Or deploy via GitHub**:
   - Push your code to GitHub
   - Connect Railway to your repo
   - Railway auto-detects the Dockerfile
   - Add environment variables in Railway dashboard
   - Deploy!

5. **Get your URL**:
   - Railway provides a public URL like: `https://tradingagents-production.up.railway.app`

### Railway Configuration

Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "chainlit run chainlit_app.py --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## Render Deployment

**Best for**: Auto-scaling, simple pricing
**Cost**: $7-25/month (starter plans)
**Time**: 10 minutes

### Steps

1. **Sign up at [Render.com](https://render.com)**

2. **Create a new Web Service**:
   - Connect your GitHub/GitLab repository
   - Or use the Render Blueprint (see below)

3. **Configure settings**:
   - **Name**: tradingagents-web
   - **Environment**: Docker
   - **Region**: Choose closest to your users
   - **Instance Type**: Starter ($7/mo) or higher

4. **Add environment variables**:
   ```
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   ALPHA_VANTAGE_API_KEY=your_key_here
   ```

5. **Deploy**:
   - Render auto-builds from your Dockerfile
   - Get a URL like: `https://tradingagents-web.onrender.com`

### Render Blueprint (Optional)

Create `render.yaml`:
```yaml
services:
  - type: web
    name: tradingagents-web
    env: docker
    dockerfilePath: ./Dockerfile
    plan: starter
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: ALPHA_VANTAGE_API_KEY
        sync: false
      - key: CHAINLIT_HOST
        value: 0.0.0.0
      - key: CHAINLIT_PORT
        value: 8000
    healthCheckPath: /health
```

---

## Google Cloud Run

**Best for**: Serverless, pay-per-use, auto-scaling
**Cost**: ~$10-50/month (depending on usage)
**Time**: 15 minutes

### Prerequisites
- Google Cloud account
- `gcloud` CLI installed

### Steps

1. **Set up Google Cloud**:
```bash
# Login
gcloud auth login

# Create project
gcloud projects create tradingagents-prod --name="TradingAgents"

# Set project
gcloud config set project tradingagents-prod

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

2. **Build and push Docker image**:
```bash
# Configure Docker for GCR
gcloud auth configure-docker

# Build image
docker build -t gcr.io/tradingagents-prod/chainlit-app:latest .

# Push to Google Container Registry
docker push gcr.io/tradingagents-prod/chainlit-app:latest
```

3. **Deploy to Cloud Run**:
```bash
gcloud run deploy tradingagents-web \
  --image gcr.io/tradingagents-prod/chainlit-app:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --set-env-vars OPENAI_API_KEY=your_key_here,ALPHA_VANTAGE_API_KEY=your_key_here
```

4. **Or use Secret Manager** (more secure):
```bash
# Create secrets
echo -n "your_openai_key" | gcloud secrets create openai-api-key --data-file=-

# Deploy with secrets
gcloud run deploy tradingagents-web \
  --image gcr.io/tradingagents-prod/chainlit-app:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest
```

5. **Get your URL**:
   - Cloud Run provides a URL like: `https://tradingagents-web-xyz123-uc.a.run.app`

---

## AWS ECS/Fargate

**Best for**: Production workloads, enterprise
**Cost**: $50-200/month (depending on instance size)
**Time**: 30-60 minutes

### Prerequisites
- AWS account
- AWS CLI installed and configured
- Docker installed

### Steps

1. **Create ECR repository**:
```bash
aws ecr create-repository --repository-name tradingagents-web --region us-east-1
```

2. **Build and push Docker image**:
```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t tradingagents-web .

# Tag image
docker tag tradingagents-web:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/tradingagents-web:latest

# Push image
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/tradingagents-web:latest
```

3. **Create ECS Task Definition**:

Create `ecs-task-definition.json`:
```json
{
  "family": "tradingagents-web",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "chainlit-app",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/tradingagents-web:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "CHAINLIT_HOST",
          "value": "0.0.0.0"
        },
        {
          "name": "CHAINLIT_PORT",
          "value": "8000"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/tradingagents-web",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

4. **Register task definition**:
```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

5. **Create ECS Service**:
```bash
aws ecs create-service \
  --cluster tradingagents-cluster \
  --service-name tradingagents-web-service \
  --task-definition tradingagents-web \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

6. **Set up Application Load Balancer** (optional but recommended):
   - Create ALB in AWS Console
   - Point to ECS service
   - Configure HTTPS with ACM certificate

---

## Docker Deployment (Any Platform)

**Best for**: Self-hosted, VPS, on-premise
**Cost**: VPS cost (~$5-50/month)
**Time**: 10 minutes

### Using Docker Compose (Recommended)

1. **Clone repository on server**:
```bash
git clone <your-repo-url>
cd TradingAgents
```

2. **Set up environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Build and run**:
```bash
docker-compose up -d
```

4. **Check logs**:
```bash
docker-compose logs -f
```

5. **Access the app**:
   - Local: `http://localhost:8000`
   - Public: Set up nginx reverse proxy (see below)

### Using Docker directly

```bash
# Build
docker build -t tradingagents-web .

# Run
docker run -d \
  --name tradingagents-web \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e ALPHA_VANTAGE_API_KEY=your_key \
  -v $(pwd)/results:/app/results \
  tradingagents-web
```

### Nginx Reverse Proxy (for production)

Create `/etc/nginx/sites-available/tradingagents`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart nginx:
```bash
sudo ln -s /etc/nginx/sites-available/tradingagents /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Set up SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

---

## Environment Variables Reference

### Required
```bash
# At least ONE LLM provider key required
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
OPENROUTER_API_KEY=sk-or-...
```

### Optional (but recommended)
```bash
# Data providers
ALPHA_VANTAGE_API_KEY=...

# Social media (for sentiment analysis)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...

# Chainlit configuration
CHAINLIT_HOST=0.0.0.0
CHAINLIT_PORT=8000
```

---

## Performance Tips

1. **Memory**: Allocate at least 2GB RAM (4GB recommended)
2. **CPU**: 2 vCPUs minimum for good performance
3. **Timeout**: Set to 3600s (1 hour) for long analyses
4. **Caching**: Enable data caching to reduce API calls
5. **Concurrent Users**: 1 GB RAM per concurrent user (approximate)

---

## Monitoring

### Health Check Endpoint
The app includes a `/health` endpoint for monitoring.

### Logging
- Logs are written to stdout/stderr
- Use your platform's log aggregation:
  - Railway: Built-in logs
  - Render: Built-in logs
  - Cloud Run: Cloud Logging
  - AWS: CloudWatch Logs

### Metrics to Monitor
- Response time
- Memory usage
- API rate limits (OpenAI, Alpha Vantage)
- Error rates

---

## Troubleshooting

### Cold Starts
- **Problem**: First request is slow
- **Solution**: Use Cloud Run min-instances or keep-alive pings

### Out of Memory
- **Problem**: Container crashes during analysis
- **Solution**: Increase memory allocation to 4GB+

### API Rate Limits
- **Problem**: Alpha Vantage 5 calls/minute limit
- **Solution**: Enable caching, use yfinance as fallback

### Timeout Errors
- **Problem**: Analysis takes too long
- **Solution**: Increase timeout to 3600s (1 hour)

---

## Cost Estimates

| Platform | Monthly Cost | Notes |
|----------|-------------|-------|
| Railway | $5-20 | Pay-per-use, generous free tier |
| Render | $7-25 | Fixed pricing, auto-scaling |
| Cloud Run | $10-50 | Pay-per-request, scales to zero |
| AWS Fargate | $50-200 | Always-on, production-grade |
| VPS (DigitalOcean) | $12-48 | Full control, manual setup |

**Note**: Costs don't include API usage (OpenAI, Alpha Vantage, etc.)

---

## Next Steps

1. Choose a deployment platform
2. Set up environment variables
3. Deploy using the guide above
4. Test with a sample stock analysis
5. Share the URL with users!

Need help? Check the [main README](README.md) or open an issue on GitHub.
