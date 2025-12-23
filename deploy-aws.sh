#!/bin/bash

# TradingAgents AWS Deployment Script
# Quick deployment to AWS App Runner

set -e

echo "🚀 TradingAgents AWS Deployment"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="tradingagents-web"
REGION="${AWS_REGION:-us-east-1}"
SERVICE_NAME="tradingagents-web"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first:${NC}"
    echo "   brew install awscli  # macOS"
    echo "   or visit: https://aws.amazon.com/cli/"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured.${NC}"
    echo "   Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites checked${NC}"
echo ""

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📦 AWS Account: $ACCOUNT_ID"
echo "🌍 Region: $REGION"
echo ""

# Prompt for deployment method
echo "Select deployment method:"
echo "1) AWS App Runner (Easiest, ~$25/mo)"
echo "2) AWS ECS with Copilot CLI (~$30/mo)"
echo "3) AWS Lightsail (~$10-40/mo fixed)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🏃 Deploying to AWS App Runner..."
        echo ""

        # Check if ECR repository exists
        if ! aws ecr describe-repositories --repository-names $APP_NAME --region $REGION &> /dev/null; then
            echo "📦 Creating ECR repository..."
            aws ecr create-repository --repository-name $APP_NAME --region $REGION
        fi

        # Login to ECR
        echo "🔐 Logging into ECR..."
        aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

        # Build and push image
        echo "🔨 Building Docker image..."
        docker build -t $APP_NAME .

        echo "📤 Pushing to ECR..."
        docker tag $APP_NAME:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$APP_NAME:latest
        docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$APP_NAME:latest

        # Check if OpenAI API key is set
        if [ -z "$OPENAI_API_KEY" ]; then
            echo ""
            echo -e "${YELLOW}⚠️  OPENAI_API_KEY environment variable not set${NC}"
            read -p "Enter your OpenAI API key: " OPENAI_API_KEY
        fi

        # Check if App Runner service exists
        if aws apprunner list-services --region $REGION --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text | grep -q "arn:"; then
            echo "🔄 Updating existing App Runner service..."
            SERVICE_ARN=$(aws apprunner list-services --region $REGION --query "ServiceSummaryList[?ServiceName=='$SERVICE_NAME'].ServiceArn" --output text)
            aws apprunner start-deployment --service-arn $SERVICE_ARN --region $REGION
        else
            echo "🆕 Creating new App Runner service..."

            # Create service
            SERVICE_ARN=$(aws apprunner create-service \
                --service-name $SERVICE_NAME \
                --region $REGION \
                --source-configuration '{
                    "ImageRepository": {
                        "ImageIdentifier": "'$ACCOUNT_ID'.dkr.ecr.'$REGION'.amazonaws.com/'$APP_NAME':latest",
                        "ImageRepositoryType": "ECR",
                        "ImageConfiguration": {
                            "Port": "8000",
                            "RuntimeEnvironmentVariables": {
                                "OPENAI_API_KEY": "'$OPENAI_API_KEY'"
                            }
                        }
                    },
                    "AutoDeploymentsEnabled": true
                }' \
                --instance-configuration '{
                    "Cpu": "1024",
                    "Memory": "2048"
                }' \
                --query 'Service.ServiceArn' \
                --output text)
        fi

        echo ""
        echo "⏳ Waiting for service to be ready..."
        aws apprunner wait service-running --service-arn $SERVICE_ARN --region $REGION

        # Get service URL
        SERVICE_URL=$(aws apprunner describe-service --service-arn $SERVICE_ARN --region $REGION --query 'Service.ServiceUrl' --output text)

        echo ""
        echo -e "${GREEN}✅ Deployment complete!${NC}"
        echo ""
        echo "🌐 Your app is available at: https://$SERVICE_URL"
        echo "📊 View in console: https://console.aws.amazon.com/apprunner/home?region=$REGION#/services"
        ;;

    2)
        echo ""
        echo "🚢 Deploying with AWS Copilot..."
        echo ""

        if ! command -v copilot &> /dev/null; then
            echo -e "${YELLOW}⚠️  Copilot CLI not found. Installing...${NC}"
            brew install aws/tap/copilot-cli
        fi

        # Check if OpenAI API key is set
        if [ -z "$OPENAI_API_KEY" ]; then
            echo ""
            echo -e "${YELLOW}⚠️  OPENAI_API_KEY environment variable not set${NC}"
            read -p "Enter your OpenAI API key: " OPENAI_API_KEY
        fi

        # Initialize Copilot if needed
        if [ ! -f "copilot/.workspace" ]; then
            echo "🎬 Initializing Copilot..."
            copilot init \
                --app tradingagents \
                --name web \
                --type "Load Balanced Web Service" \
                --dockerfile ./Dockerfile \
                --port 8000
        fi

        # Set secrets
        echo "🔐 Setting secrets..."
        echo "$OPENAI_API_KEY" | copilot secret init --name OPENAI_API_KEY --overwrite

        # Deploy
        echo "🚀 Deploying..."
        copilot deploy --name web

        # Get URL
        copilot svc show --name web
        ;;

    3)
        echo ""
        echo "💡 Deploying to AWS Lightsail..."
        echo ""

        # Check if service exists
        if aws lightsail get-container-services --service-name $SERVICE_NAME &> /dev/null; then
            echo "🔄 Service exists. Updating..."
        else
            echo "🆕 Creating new Lightsail container service..."
            aws lightsail create-container-service \
                --service-name $SERVICE_NAME \
                --power small \
                --scale 1
        fi

        # Build and push
        echo "🔨 Building and pushing to Lightsail..."
        docker build -t $APP_NAME .
        aws lightsail push-container-image \
            --service-name $SERVICE_NAME \
            --label $APP_NAME \
            --image $APP_NAME:latest

        # Check if OpenAI API key is set
        if [ -z "$OPENAI_API_KEY" ]; then
            echo ""
            echo -e "${YELLOW}⚠️  OPENAI_API_KEY environment variable not set${NC}"
            read -p "Enter your OpenAI API key: " OPENAI_API_KEY
        fi

        # Create deployment JSON
        cat > lightsail-deployment.json <<EOF
{
  "serviceName": "$SERVICE_NAME",
  "containers": {
    "$APP_NAME": {
      "image": ":$APP_NAME.latest",
      "ports": {
        "8000": "HTTP"
      },
      "environment": {
        "OPENAI_API_KEY": "$OPENAI_API_KEY"
      }
    }
  },
  "publicEndpoint": {
    "containerName": "$APP_NAME",
    "containerPort": 8000,
    "healthCheck": {
      "path": "/",
      "intervalSeconds": 10
    }
  }
}
EOF

        # Deploy
        echo "🚀 Deploying container..."
        aws lightsail create-container-service-deployment --cli-input-json file://lightsail-deployment.json

        echo ""
        echo -e "${GREEN}✅ Deployment started!${NC}"
        echo "View status: https://lightsail.aws.amazon.com/"
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "📝 Next steps:"
echo "1. Visit your app URL"
echo "2. Monitor logs in AWS Console"
echo "3. Set up custom domain (optional)"
echo "4. Configure auto-scaling (optional)"
echo ""
echo -e "${GREEN}Happy trading! 📈${NC}"
