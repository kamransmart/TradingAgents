# TradingAgents Web Interface - Cloud Deployment Guide

This guide covers deploying your TradingAgents Chainlit web interface to various cloud platforms.

## Table of Contents
1. [Railway (Easiest - Recommended)](#railway)
2. [Render](#render)
3. [Fly.io](#flyio)
4. [Google Cloud Run](#google-cloud-run)
5. [AWS ECS/Fargate](#aws-ecsfargate)
6. [Azure Container Apps](#azure-container-apps)

---

## Prerequisites

All platforms require:
- A GitHub/GitLab account with your code pushed
- Your OpenAI API key
- (Optional) Alpha Vantage API key for additional data sources

---

## 1. Railway (Easiest - Recommended) ⭐

**Cost**: ~$5-10/month with $5 free credit
**Setup Time**: 5 minutes
**Best For**: Quick deployment, easy scaling

### Steps:

1. **Push your code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Deploy to Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your TradingAgents repository
   - Railway will auto-detect the Dockerfile

3. **Set Environment Variables**:
   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add these variables:
     ```
     OPENAI_API_KEY=sk-your-key-here
     ALPHA_VANTAGE_API_KEY=your-key-here (optional)
     PORT=8000
     ```

4. **Configure Port**:
   - Railway auto-detects port 8000 from Dockerfile
   - You'll get a URL like: `https://your-app.railway.app`

5. **Access Your App**:
   - Railway provides a public URL automatically
   - Your app will be available at the generated domain

### Railway CLI (Alternative Method):

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize and deploy
railway init
railway up
```

---

## 2. Render

**Cost**: Free tier available, paid starts at $7/month
**Setup Time**: 10 minutes
**Best For**: Simple apps, built-in CI/CD

### Steps:

1. **Create `render.yaml`** (already exists in your repo):
   ```yaml
   services:
     - type: web
       name: tradingagents-web
       env: docker
       dockerfilePath: ./Dockerfile
       envVars:
         - key: OPENAI_API_KEY
           sync: false
         - key: ALPHA_VANTAGE_API_KEY
           sync: false
         - key: PORT
           value: 8000
   ```

2. **Deploy**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will use the `render.yaml` file

3. **Set Environment Variables**:
   - In Render dashboard, add your API keys
   - They're encrypted and secure

4. **Custom Domain** (Optional):
   - Free: `your-app.onrender.com`
   - Custom: Add your domain in settings

---

## 3. Fly.io

**Cost**: Free tier includes 3 small VMs
**Setup Time**: 10 minutes
**Best For**: Global edge deployment, low latency

### Steps:

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and Initialize**:
   ```bash
   fly auth login
   fly launch
   ```

   Fly will detect your Dockerfile and create `fly.toml`

3. **Configure fly.toml**:
   ```toml
   app = "tradingagents-web"
   primary_region = "sjc"

   [env]
     PORT = "8000"

   [http_service]
     internal_port = 8000
     force_https = true
     auto_stop_machines = true
     auto_start_machines = true
     min_machines_running = 0

   [[vm]]
     cpu_kind = "shared"
     cpus = 1
     memory_mb = 512
   ```

4. **Set Secrets**:
   ```bash
   fly secrets set OPENAI_API_KEY=sk-your-key-here
   fly secrets set ALPHA_VANTAGE_API_KEY=your-key-here
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

6. **Open Your App**:
   ```bash
   fly open
   ```

---

## 4. Google Cloud Run

**Cost**: Pay per use, generous free tier
**Setup Time**: 15 minutes
**Best For**: Enterprise, auto-scaling to zero

### Steps:

1. **Install Google Cloud CLI**:
   ```bash
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   ```

2. **Build and Push Container**:
   ```bash
   # Set project and region
   export PROJECT_ID=your-project-id
   export REGION=us-central1

   # Build container
   gcloud builds submit --tag gcr.io/$PROJECT_ID/tradingagents-web
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy tradingagents-web \
     --image gcr.io/$PROJECT_ID/tradingagents-web \
     --platform managed \
     --region $REGION \
     --allow-unauthenticated \
     --port 8000 \
     --set-env-vars OPENAI_API_KEY=sk-your-key \
     --memory 1Gi \
     --timeout 900
   ```

4. **Get URL**:
   ```bash
   gcloud run services describe tradingagents-web --region $REGION --format 'value(status.url)'
   ```

---

## 5. AWS ECS/Fargate

**Cost**: ~$10-30/month
**Setup Time**: 20 minutes
**Best For**: AWS ecosystem integration

### Quick Deploy with Copilot CLI:

1. **Install AWS Copilot**:
   ```bash
   brew install aws/tap/copilot-cli
   ```

2. **Initialize and Deploy**:
   ```bash
   copilot init \
     --app tradingagents \
     --name web \
     --type "Load Balanced Web Service" \
     --dockerfile ./Dockerfile \
     --port 8000

   copilot deploy
   ```

3. **Set Secrets**:
   ```bash
   copilot secret init --name OPENAI_API_KEY
   copilot secret init --name ALPHA_VANTAGE_API_KEY
   ```

### Manual ECS Setup:

See full guide at: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started.html

---

## 6. Azure Container Apps

**Cost**: Pay per use, free tier available
**Setup Time**: 15 minutes
**Best For**: Microsoft ecosystem

### Steps:

1. **Install Azure CLI**:
   ```bash
   brew install azure-cli
   az login
   ```

2. **Create Resources**:
   ```bash
   # Set variables
   RESOURCE_GROUP="tradingagents-rg"
   LOCATION="eastus"
   CONTAINER_APP_NAME="tradingagents-web"

   # Create resource group
   az group create --name $RESOURCE_GROUP --location $LOCATION

   # Create Container App environment
   az containerapp env create \
     --name tradingagents-env \
     --resource-group $RESOURCE_GROUP \
     --location $LOCATION
   ```

3. **Deploy from Dockerfile**:
   ```bash
   az containerapp up \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --location $LOCATION \
     --source . \
     --target-port 8000 \
     --ingress external \
     --env-vars OPENAI_API_KEY=secretref:openai-key
   ```

4. **Set Secrets**:
   ```bash
   az containerapp secret set \
     --name $CONTAINER_APP_NAME \
     --resource-group $RESOURCE_GROUP \
     --secrets openai-key=sk-your-key-here
   ```

---

## Comparison Table

| Platform | Cost | Setup Time | Difficulty | Auto-Scale | Free Tier |
|----------|------|------------|------------|------------|-----------|
| Railway | $5-10/mo | 5 min | ⭐ Easy | ✅ Yes | $5 credit |
| Render | $7/mo | 10 min | ⭐ Easy | ✅ Yes | ✅ Yes |
| Fly.io | Free-$10/mo | 10 min | ⭐⭐ Medium | ✅ Yes | ✅ Yes (3 VMs) |
| Cloud Run | Pay-per-use | 15 min | ⭐⭐ Medium | ✅ Yes | ✅ Generous |
| AWS ECS | $10-30/mo | 20 min | ⭐⭐⭐ Hard | ✅ Yes | ✅ Limited |
| Azure | Pay-per-use | 15 min | ⭐⭐ Medium | ✅ Yes | ✅ Yes |

---

## Post-Deployment Checklist

After deploying to any platform:

### 1. Test Your Deployment
```bash
curl https://your-app-url.com
```

### 2. Monitor Logs
- Railway: Built-in logs viewer
- Render: Logs tab in dashboard
- Fly.io: `fly logs`
- Cloud Run: Cloud Console → Logs
- AWS: CloudWatch Logs
- Azure: Log Analytics

### 3. Set Up Custom Domain (Optional)
Most platforms support custom domains:
- Point your domain's CNAME to the platform URL
- Configure SSL (usually automatic)

### 4. Enable Auto-scaling (if needed)
Configure based on:
- CPU usage
- Memory usage
- Request count

### 5. Set Up Monitoring
Consider adding:
- Uptime monitoring (UptimeRobot, Pingdom)
- Error tracking (Sentry)
- Analytics (optional)

---

## Environment Variables Required

Make sure to set these on your chosen platform:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (for additional data sources)
ALPHA_VANTAGE_API_KEY=...

# Platform-specific
PORT=8000  # Usually auto-configured
```

---

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Use HTTPS** - All platforms provide this automatically
3. **Rate limiting** - Consider adding rate limits for public apps
4. **Authentication** - For production, add user authentication
5. **Secrets management** - Use platform-specific secret stores

---

## Troubleshooting

### App won't start
- Check logs for errors
- Verify environment variables are set
- Ensure port 8000 is exposed

### High costs
- Enable auto-scaling to zero when idle
- Use smaller instance sizes
- Consider usage-based pricing

### Slow performance
- Upgrade instance size
- Enable caching
- Use a CDN for static assets

### API rate limits
- Implement request queuing
- Add rate limiting middleware
- Consider batch processing

---

## Recommended: Railway Deployment

For most users, **Railway is the easiest and fastest option**:

```bash
# Quick deploy in 3 commands
git push origin main
# Then use Railway web UI to:
# 1. Connect GitHub repo
# 2. Add OPENAI_API_KEY
# 3. Deploy!
```

Your app will be live at `https://your-app.railway.app` in ~5 minutes.

---

## Need Help?

- Railway: https://docs.railway.app
- Render: https://render.com/docs
- Fly.io: https://fly.io/docs
- Cloud Run: https://cloud.google.com/run/docs
- AWS: https://aws.amazon.com/ecs/
- Azure: https://learn.microsoft.com/azure/container-apps/

---

## Next Steps

After deployment:
1. Share your app URL with users
2. Monitor usage and costs
3. Set up alerts for errors
4. Consider adding authentication
5. Enable custom domain (optional)

Enjoy your cloud-deployed TradingAgents! 🚀
