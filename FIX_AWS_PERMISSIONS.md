# Fix AWS Permissions Error

You're getting an `AccessDeniedException` because your IAM user doesn't have the necessary permissions.

## Quick Fix (2 methods)

### Method 1: Add Policy via AWS Console (Easiest)

1. **Go to IAM Console**
   - Visit: https://console.aws.amazon.com/iam/
   - Click **Users** → **tradingagents**

2. **Add Permissions**
   - Click **"Add permissions"** → **"Attach policies directly"**
   - Search and select these AWS managed policies:
     - ✅ **AmazonEC2ContainerRegistryFullAccess**
     - ✅ **AWSAppRunnerFullAccess**
     - ✅ **CloudWatchLogsFullAccess**

3. **Click "Add permissions"**

4. **Done!** Try deploying again:
   ```bash
   ./deploy-aws.sh
   ```

---

### Method 2: Create Custom Policy (More Secure)

1. **Go to IAM Console**
   - Visit: https://console.aws.amazon.com/iam/
   - Click **Policies** → **Create policy**

2. **Switch to JSON tab**
   - Copy content from [aws-iam-policy.json](./aws-iam-policy.json)
   - Paste into the editor

3. **Name the policy**
   - Name: `TradingAgentsDeploymentPolicy`
   - Description: `Permissions for deploying TradingAgents to AWS`

4. **Create policy**
   - Click **"Create policy"**

5. **Attach to your user**
   - Go to **Users** → **tradingagents**
   - Click **"Add permissions"** → **"Attach policies directly"**
   - Search for `TradingAgentsDeploymentPolicy`
   - Select it and click **"Add permissions"**

6. **Done!** Try deploying again

---

### Method 3: Use AWS CLI (Fastest)

```bash
# Attach managed policies
aws iam attach-user-policy \
  --user-name tradingagents \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess

aws iam attach-user-policy \
  --user-name tradingagents \
  --policy-arn arn:aws:iam::aws:policy/AWSAppRunnerFullAccess

aws iam attach-user-policy \
  --user-name tradingagents \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

# Verify permissions
aws iam list-attached-user-policies --user-name tradingagents
```

---

## Alternative: Use IAM Role Instead

If you don't want to give your user all these permissions, you can create an IAM role and assume it:

### Step 1: Create Role

```bash
# Create trust policy
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::185327115759:user/tradingagents"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name TradingAgentsDeploymentRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies to role
aws iam attach-role-policy \
  --role-name TradingAgentsDeploymentRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess

aws iam attach-role-policy \
  --role-name TradingAgentsDeploymentRole \
  --policy-arn arn:aws:iam::aws:policy/AWSAppRunnerFullAccess
```

### Step 2: Assume Role When Deploying

```bash
# Get temporary credentials
aws sts assume-role \
  --role-arn arn:aws:iam::185327115759:role/TradingAgentsDeploymentRole \
  --role-session-name deployment-session

# Use the temporary credentials
export AWS_ACCESS_KEY_ID=<AccessKeyId from output>
export AWS_SECRET_ACCESS_KEY=<SecretAccessKey from output>
export AWS_SESSION_TOKEN=<SessionToken from output>

# Now deploy
./deploy-aws.sh
```

---

## Minimum Required Permissions

If you want the least-privilege approach, here are the exact permissions needed:

### For ECR (Container Registry):
- `ecr:CreateRepository`
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:PutImage`
- `ecr:InitiateLayerUpload`
- `ecr:UploadLayerPart`
- `ecr:CompleteLayerUpload`

### For App Runner:
- `apprunner:CreateService`
- `apprunner:DescribeService`
- `apprunner:ListServices`
- `apprunner:StartDeployment`
- `apprunner:UpdateService`

### For IAM (if App Runner needs to access ECR):
- `iam:CreateServiceLinkedRole`
- `iam:PassRole` (for App Runner service role)

---

## Quick Fix Command

If you have admin access or someone who does, run this:

```bash
# Give tradingagents user the necessary permissions
aws iam put-user-policy \
  --user-name tradingagents \
  --policy-name TradingAgentsDeployment \
  --policy-document file://aws-iam-policy.json
```

---

## Verify Your Permissions

After adding permissions, verify they work:

```bash
# Test ECR access
aws ecr describe-repositories --region us-east-1

# Test App Runner access
aws apprunner list-services --region us-east-1

# If no errors, you're good to go!
```

---

## Deploy Again

Once permissions are fixed:

```bash
./deploy-aws.sh
```

Or manually:

```bash
# Create ECR repository
aws ecr create-repository --repository-name tradingagents-web

# Build and push
docker build -t tradingagents-web .
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag tradingagents-web:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/tradingagents-web:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/tradingagents-web:latest
```

---

## Still Having Issues?

### Check Your IAM User Policies

```bash
# List current policies
aws iam list-attached-user-policies --user-name tradingagents
aws iam list-user-policies --user-name tradingagents

# Get current user
aws sts get-caller-identity
```

### Contact Your AWS Administrator

If you're in an organization, you may need to request permissions from your AWS administrator. Send them this list:

**Policies Needed:**
- `AmazonEC2ContainerRegistryFullAccess` (for Docker image storage)
- `AWSAppRunnerFullAccess` (for deploying web app)
- `CloudWatchLogsFullAccess` (for viewing logs)

Or share the [aws-iam-policy.json](./aws-iam-policy.json) file with them.

---

## Alternative Deployment Methods

If you can't get the permissions, try these alternatives:

### 1. Deploy via AWS Console (No CLI permissions needed)

Just needs console access:
1. Go to [App Runner Console](https://console.aws.amazon.com/apprunner)
2. Click "Create service"
3. Connect GitHub (no ECR needed)
4. Deploy!

### 2. Use Railway, Render, or Fly.io

These platforms don't require AWS permissions:
- **Railway**: [railway.app](https://railway.app) - $5/mo
- **Render**: [render.com](https://render.com) - Free tier
- **Fly.io**: [fly.io](https://fly.io) - Free tier

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for instructions.

---

## Summary

**Fastest Fix:**
1. Go to IAM Console: https://console.aws.amazon.com/iam/
2. Users → tradingagents → Add permissions
3. Attach: `AmazonEC2ContainerRegistryFullAccess` + `AWSAppRunnerFullAccess`
4. Run `./deploy-aws.sh` again

**Done!** 🎉
