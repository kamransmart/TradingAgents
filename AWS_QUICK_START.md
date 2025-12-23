# AWS Deployment - Quick Start Guide

Deploy your TradingAgents web interface to AWS in minutes!

## 🚀 Fastest Method: Automated Script

```bash
# Make sure you have AWS CLI configured
aws configure

# Run the deployment script
./deploy-aws.sh
```

The script will guide you through:
1. **App Runner** (Easiest, $25/mo)
2. **ECS with Copilot** (More control, $30/mo)
3. **Lightsail** (Budget, $10-40/mo)

---

## ⚡ Manual Quick Deploy - App Runner (5 minutes)

### Prerequisites
```bash
# Install AWS CLI
brew install awscli  # macOS
aws configure        # Enter your AWS credentials
```

### Deploy Steps

```bash
# 1. Set variables
export AWS_REGION=us-east-1
export APP_NAME=tradingagents-web
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 2. Create ECR repository
aws ecr create-repository --repository-name $APP_NAME --region $AWS_REGION

# 3. Build and push Docker image
docker build -t $APP_NAME .
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker tag $APP_NAME:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$APP_NAME:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$APP_NAME:latest

# 4. Create App Runner service
aws apprunner create-service \
  --service-name $APP_NAME \
  --region $AWS_REGION \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ACCOUNT_ID'.dkr.ecr.'$AWS_REGION'.amazonaws.com/'$APP_NAME':latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "OPENAI_API_KEY": "sk-your-openai-key-here"
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1024",
    "Memory": "2048"
  }'

# 5. Get your app URL
aws apprunner list-services --region $AWS_REGION
```

**Done!** Your app will be live in 5-10 minutes at `https://xxxxx.us-east-1.awsapprunner.com`

---

## 🖱️ Deploy via AWS Console (No CLI needed)

### Method 1: App Runner (Easiest)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to AWS"
   git push origin main
   ```

2. **Go to AWS Console**
   - Visit: https://console.aws.amazon.com/apprunner
   - Click "Create service"

3. **Configure Source**
   - Source: GitHub
   - Connect to GitHub
   - Select repository: your-repo
   - Branch: main
   - Build: Dockerfile

4. **Configure Service**
   - Service name: `tradingagents-web`
   - Port: `8000`
   - CPU: 1 vCPU
   - Memory: 2 GB

5. **Add Environment Variables**
   - Click "Add environment variable"
   - Name: `OPENAI_API_KEY`
   - Value: `sk-your-key`

6. **Create & Deploy**
   - Click "Create & Deploy"
   - Wait 5-10 minutes

7. **Access Your App**
   - Copy the provided URL
   - Open in browser

### Method 2: Lightsail (Budget-Friendly)

1. **Go to Lightsail Console**
   - Visit: https://lightsail.aws.amazon.com/
   - Click "Create" → "Container service"

2. **Upload Container**
   - Build locally: `docker build -t tradingagents-web .`
   - Upload image to Lightsail

3. **Configure**
   - Port: 8000
   - Memory: 1 GB
   - Environment variable: `OPENAI_API_KEY`

4. **Deploy**
   - Click "Create container service"
   - Get your URL from dashboard

---

## 💰 Cost Comparison

| Method | Monthly Cost | Setup Time | Difficulty |
|--------|-------------|------------|------------|
| **App Runner** | $15-30 | 5-10 min | ⭐ Easy |
| **ECS Copilot** | $20-40 | 10-15 min | ⭐⭐ Medium |
| **Lightsail** | $10-40 (fixed) | 10 min | ⭐ Easy |

### Cost Breakdown (App Runner):
- **Compute**: $0.007/vCPU-hour + $0.0008/GB-hour
- **Example**: 1 vCPU, 2 GB, 24/7 = ~$25/month
- **Free tier**: None, but very affordable

---

## 🔐 Environment Variables Needed

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key

# Optional
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
```

Get your keys:
- OpenAI: https://platform.openai.com/api-keys
- Alpha Vantage: https://www.alphavantage.co/support/#api-key

---

## 📊 Monitor Your Deployment

### App Runner
```bash
# View logs
aws logs tail /aws/apprunner/$APP_NAME --follow

# Check service status
aws apprunner describe-service --service-arn <your-service-arn>
```

### Via Console
- App Runner: https://console.aws.amazon.com/apprunner
- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups

---

## 🔄 Update Your Deployment

### Automatic (GitHub)
```bash
# Just push to main branch
git push origin main

# App Runner will auto-deploy
```

### Manual
```bash
# Rebuild and push
docker build -t tradingagents-web .
docker tag tradingagents-web:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/tradingagents-web:latest
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/tradingagents-web:latest

# Trigger deployment
aws apprunner start-deployment --service-arn <your-service-arn>
```

---

## 🌐 Add Custom Domain

1. **Get SSL Certificate**
   ```bash
   aws acm request-certificate \
     --domain-name yourdomain.com \
     --validation-method DNS
   ```

2. **Add to App Runner**
   - Console → Your service → Custom domains
   - Add domain
   - Update DNS records

3. **Configure Route 53** (if using)
   - Create A record pointing to App Runner

---

## ❌ Troubleshooting

### "Service fails to start"
```bash
# Check logs
aws logs tail /aws/apprunner/$APP_NAME --follow

# Common issues:
# - Missing OPENAI_API_KEY
# - Wrong port (should be 8000)
# - Docker build failed
```

### "Cannot access app URL"
- Wait 5-10 minutes for initial deployment
- Check service status in console
- Verify service is "Running"

### "High costs"
```bash
# Enable auto-pause (App Runner)
aws apprunner update-service \
  --service-arn <arn> \
  --auto-scaling-configuration-arn <arn-with-min-0>

# Or use smaller instance
--instance-configuration '{"Cpu": "256", "Memory": "512"}'
```

---

## 🎯 Next Steps After Deployment

1. ✅ **Test your app** - Visit the URL
2. ✅ **Set up monitoring** - CloudWatch alarms
3. ✅ **Configure auto-scaling** - Based on traffic
4. ✅ **Add custom domain** - Professional URL
5. ✅ **Set up CI/CD** - GitHub Actions

---

## 📚 Full Documentation

For detailed instructions, see:
- [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md) - Complete AWS guide
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - All platforms

---

## 🆘 Need Help?

- **AWS Support**: https://aws.amazon.com/support/
- **App Runner Docs**: https://docs.aws.amazon.com/apprunner/
- **GitHub Issues**: Create an issue in your repo

---

## 🎉 Quick Summary

**Easiest way to deploy:**

```bash
./deploy-aws.sh
```

**Or via Console:**
1. Go to App Runner Console
2. Connect GitHub
3. Add OPENAI_API_KEY
4. Deploy!

**Your app will be live in 10 minutes!** 🚀

---

Cost: ~$25/month | Auto-scaling: Yes | HTTPS: Included ✅
