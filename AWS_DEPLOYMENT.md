# TradingAgents - AWS Deployment Guide

Complete guide to deploying your TradingAgents web interface on AWS.

## Table of Contents
1. [AWS App Runner (Easiest)](#aws-app-runner-easiest)
2. [AWS Elastic Container Service (ECS) with Fargate](#aws-ecs-fargate)
3. [AWS Lightsail (Budget-Friendly)](#aws-lightsail)
4. [AWS Elastic Beanstalk](#aws-elastic-beanstalk)
5. [Cost Comparison](#cost-comparison)

---

## Prerequisites

Before deploying to AWS:

```bash
# Install AWS CLI
brew install awscli  # macOS
# or
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

Get AWS credentials:
1. Go to [AWS Console](https://console.aws.amazon.com)
2. IAM → Users → Your User → Security Credentials
3. Create Access Key

---

## 1. AWS App Runner (Easiest) ⭐

**Best for**: Simplest deployment, auto-scaling, fully managed
**Cost**: ~$15-30/month
**Setup Time**: 10 minutes

### Option A: Deploy from GitHub (Recommended)

#### Step 1: Push code to GitHub
```bash
git add .
git commit -m "Prepare for AWS App Runner"
git push origin main
```

#### Step 2: Create App Runner Service via Console

1. Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner)
2. Click **"Create service"**
3. **Repository**:
   - Source: GitHub
   - Connect to GitHub (authenticate)
   - Repository: Select your repo
   - Branch: main
   - Deployment trigger: Automatic

4. **Build settings**:
   - Configuration: Use Dockerfile
   - Dockerfile path: `Dockerfile`
   - Port: `8000`

5. **Service settings**:
   - Service name: `tradingagents-web`
   - CPU: 1 vCPU
   - Memory: 2 GB
   - Environment variables:
     - `OPENAI_API_KEY` = `sk-your-key`
     - `ALPHA_VANTAGE_API_KEY` = `your-key` (optional)

6. Click **"Create & Deploy"**

#### Step 3: Access Your App
- App Runner provides a URL: `https://xxxxx.us-east-1.awsapprunner.com`
- Deployment takes ~5-10 minutes

### Option B: Deploy from ECR (Container Registry)

```bash
# 1. Build and tag image
docker build -t tradingagents-web .

# 2. Create ECR repository
aws ecr create-repository --repository-name tradingagents-web

# 3. Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# 4. Tag and push
docker tag tradingagents-web:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/tradingagents-web:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/tradingagents-web:latest

# 5. Create App Runner service from ECR
aws apprunner create-service \
  --service-name tradingagents-web \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/tradingagents-web:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "OPENAI_API_KEY": "sk-your-key"
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1024",
    "Memory": "2048"
  }'
```

---

## 2. AWS ECS Fargate

**Best for**: More control, AWS ecosystem integration
**Cost**: ~$20-40/month
**Setup Time**: 20 minutes

### Option A: Using Copilot CLI (Easiest for ECS)

```bash
# 1. Install Copilot CLI
brew install aws/tap/copilot-cli

# 2. Initialize application
copilot init \
  --app tradingagents \
  --name web \
  --type "Load Balanced Web Service" \
  --dockerfile ./Dockerfile \
  --port 8000

# 3. Deploy
copilot deploy --name web

# 4. Set secrets
copilot secret init --name OPENAI_API_KEY
copilot secret init --name ALPHA_VANTAGE_API_KEY

# 5. Get service URL
copilot svc show --name web
```

### Option B: Manual ECS Setup

#### Step 1: Build and Push to ECR
```bash
# Create ECR repository
aws ecr create-repository --repository-name tradingagents-web --region us-east-1

# Get your account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build and push
docker build -t tradingagents-web .
docker tag tradingagents-web:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/tradingagents-web:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/tradingagents-web:latest
```

#### Step 2: Create ECS Task Definition

Create `ecs-task-definition.json`:
```json
{
  "family": "tradingagents-web",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "tradingagents-web",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/tradingagents-web:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "PORT",
          "value": "8000"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:openai-api-key"
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

#### Step 3: Store Secrets in AWS Secrets Manager
```bash
aws secretsmanager create-secret \
  --name openai-api-key \
  --secret-string "sk-your-openai-key" \
  --region us-east-1
```

#### Step 4: Create ECS Cluster and Service
```bash
# Create cluster
aws ecs create-cluster --cluster-name tradingagents-cluster --region us-east-1

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service (you'll need VPC, subnets, and security group IDs)
aws ecs create-service \
  --cluster tradingagents-cluster \
  --service-name tradingagents-web \
  --task-definition tradingagents-web \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=tradingagents-web,containerPort=8000"
```

#### Step 5: Create Application Load Balancer
```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name tradingagents-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-xxx

# Create target group
aws elbv2 create-target-group \
  --name tradingagents-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxx \
  --target-type ip \
  --health-check-path /

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

---

## 3. AWS Lightsail (Budget-Friendly)

**Best for**: Simple deployment, predictable pricing
**Cost**: $10-40/month (fixed price)
**Setup Time**: 15 minutes

### Step 1: Create Container Service
```bash
# Install Lightsail CLI plugin
aws lightsail help

# Create container service
aws lightsail create-container-service \
  --service-name tradingagents-web \
  --power small \
  --scale 1
```

### Step 2: Push Container to Lightsail
```bash
# Push image to Lightsail
aws lightsail push-container-image \
  --service-name tradingagents-web \
  --label tradingagents-web \
  --image tradingagents-web:latest
```

### Step 3: Deploy Container
Create `lightsail-deployment.json`:
```json
{
  "serviceName": "tradingagents-web",
  "containers": {
    "tradingagents-web": {
      "image": ":tradingagents-web.latest",
      "ports": {
        "8000": "HTTP"
      },
      "environment": {
        "OPENAI_API_KEY": "sk-your-key"
      }
    }
  },
  "publicEndpoint": {
    "containerName": "tradingagents-web",
    "containerPort": 8000,
    "healthCheck": {
      "path": "/",
      "intervalSeconds": 10
    }
  }
}
```

Deploy:
```bash
aws lightsail create-container-service-deployment \
  --cli-input-json file://lightsail-deployment.json
```

### Via Console:
1. Go to [Lightsail Console](https://lightsail.aws.amazon.com/)
2. Create → Container service
3. Upload your Docker image
4. Configure port 8000
5. Add environment variables
6. Deploy

---

## 4. AWS Elastic Beanstalk

**Best for**: Traditional PaaS experience
**Cost**: ~$20-40/month
**Setup Time**: 15 minutes

### Step 1: Create `Dockerrun.aws.json`
```json
{
  "AWSEBDockerrunVersion": "1",
  "Image": {
    "Name": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/tradingagents-web:latest",
    "Update": "true"
  },
  "Ports": [
    {
      "ContainerPort": 8000,
      "HostPort": 8000
    }
  ]
}
```

### Step 2: Deploy with EB CLI
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker tradingagents-web --region us-east-1

# Create environment
eb create tradingagents-env \
  --instance-type t3.small \
  --single

# Set environment variables
eb setenv OPENAI_API_KEY=sk-your-key

# Deploy
eb deploy

# Open in browser
eb open
```

---

## Cost Comparison

| Service | Monthly Cost | Setup | Auto-Scale | Best For |
|---------|-------------|-------|------------|----------|
| **App Runner** | $15-30 | ⭐ Easy | ✅ Yes | Quick start |
| **ECS Fargate** | $20-40 | ⭐⭐ Medium | ✅ Yes | Production |
| **Lightsail** | $10-40 (fixed) | ⭐ Easy | ⚠️ Manual | Predictable cost |
| **Elastic Beanstalk** | $20-40 | ⭐⭐ Medium | ✅ Yes | Traditional PaaS |

### Detailed Cost Breakdown (App Runner):
- **App Runner Service**: ~$0.007/vCPU-hour + $0.0008/GB-hour
- **Example**: 1 vCPU, 2 GB RAM running 24/7 = ~$25/month
- **Network**: Data transfer out (first 100 GB free)

---

## Security Best Practices

### 1. Use AWS Secrets Manager for API Keys
```bash
# Store secret
aws secretsmanager create-secret \
  --name tradingagents/openai-key \
  --secret-string "sk-your-key"

# Grant access to ECS task
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

### 2. Enable HTTPS
- Use AWS Certificate Manager (ACM) for free SSL certificates
- Attach certificate to Load Balancer

### 3. Set Up WAF (Web Application Firewall)
```bash
aws wafv2 create-web-acl \
  --name tradingagents-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-rules.json
```

### 4. Configure VPC Security Groups
```bash
# Allow only HTTPS traffic
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

---

## Monitoring and Logging

### CloudWatch Logs
```bash
# View logs
aws logs tail /ecs/tradingagents-web --follow

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name tradingagents-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

### X-Ray for Tracing (Optional)
Add to Dockerfile:
```dockerfile
RUN pip install aws-xray-sdk
```

---

## CI/CD Pipeline with GitHub Actions

Create `.github/workflows/deploy-aws.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build and push Docker image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: tradingagents-web
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

    - name: Deploy to App Runner
      run: |
        aws apprunner start-deployment --service-arn arn:aws:apprunner:...
```

---

## Troubleshooting

### Container Fails to Start
```bash
# Check ECS task logs
aws logs tail /ecs/tradingagents-web --follow

# Check App Runner logs
aws apprunner list-operations --service-arn arn:aws:apprunner:...
```

### High Costs
- **Enable auto-scaling**: Scale down to 0 instances during idle times
- **Use Fargate Spot**: Save up to 70% on compute costs
- **Right-size resources**: Start with smaller instances

### Slow Performance
- **Increase memory**: Try 4 GB RAM
- **Add more CPU**: Upgrade to 2 vCPU
- **Enable caching**: Use CloudFront CDN

---

## Custom Domain Setup

### 1. Get Domain from Route 53 (or use existing)
```bash
aws route53domains register-domain --domain-name tradingagents.com
```

### 2. Get SSL Certificate
```bash
aws acm request-certificate \
  --domain-name tradingagents.com \
  --validation-method DNS
```

### 3. Create Route 53 Record
```bash
# Point to Load Balancer or App Runner
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456 \
  --change-batch file://dns-record.json
```

---

## Recommended: App Runner Quick Start

For most users, App Runner is the best choice:

```bash
# 1. Push to GitHub
git push origin main

# 2. Go to AWS Console → App Runner
# 3. Click "Create service" from GitHub
# 4. Add OPENAI_API_KEY environment variable
# 5. Deploy!

# Your app will be live at:
# https://xxxxx.us-east-1.awsapprunner.com
```

**Total Time**: 10 minutes
**Cost**: ~$25/month
**Auto-scaling**: Yes
**HTTPS**: Included

---

## Next Steps

1. **Set up monitoring**: CloudWatch dashboards
2. **Enable auto-scaling**: Based on CPU/memory
3. **Add custom domain**: Route 53 + ACM
4. **Set up CI/CD**: GitHub Actions
5. **Configure backups**: S3 for results folder

---

## Support Resources

- [AWS App Runner Docs](https://docs.aws.amazon.com/apprunner/)
- [AWS ECS Docs](https://docs.aws.amazon.com/ecs/)
- [AWS Copilot CLI](https://aws.github.io/copilot-cli/)
- [AWS Lightsail Docs](https://lightsail.aws.amazon.com/ls/docs/)

---

**Need help?** Check the main [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) or AWS support.

Happy deploying! 🚀
