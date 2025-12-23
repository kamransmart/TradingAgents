#!/bin/bash

echo "🔧 AWS Credentials Configuration Helper"
echo "========================================"
echo ""

# Check current identity
echo "Current AWS Identity:"
aws sts get-caller-identity
echo ""

CURRENT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
TARGET_ACCOUNT="185327115759"

if [ "$CURRENT_ACCOUNT" != "$TARGET_ACCOUNT" ]; then
    echo "⚠️  Account Mismatch Detected!"
    echo "   Current account: $CURRENT_ACCOUNT"
    echo "   Target account:  $TARGET_ACCOUNT"
    echo ""
    echo "You need to switch to the correct AWS credentials."
    echo ""
    echo "Options to fix:"
    echo ""
    echo "1️⃣  Set AWS CLI profile for tradingagents user:"
    echo "   aws configure --profile tradingagents"
    echo "   # Enter your Access Key ID and Secret Key for account $TARGET_ACCOUNT"
    echo ""
    echo "   Then use it:"
    echo "   export AWS_PROFILE=tradingagents"
    echo "   aws sts get-caller-identity  # Should show account $TARGET_ACCOUNT"
    echo ""
    echo "2️⃣  Or reconfigure default profile:"
    echo "   aws configure"
    echo "   # Enter credentials for account $TARGET_ACCOUNT"
    echo ""
    echo "3️⃣  Or set credentials as environment variables:"
    echo "   export AWS_ACCESS_KEY_ID=<your-key-for-$TARGET_ACCOUNT>"
    echo "   export AWS_SECRET_ACCESS_KEY=<your-secret-for-$TARGET_ACCOUNT>"
    echo "   export AWS_DEFAULT_REGION=us-east-1"
    echo ""
else
    echo "✅ Using correct AWS account: $CURRENT_ACCOUNT"
    echo ""
    echo "Now testing permissions..."
    echo ""

    # Test ECR
    echo "Testing ECR access..."
    if aws ecr describe-repositories --region us-east-1 2>&1 | grep -q "AccessDeniedException"; then
        echo "❌ ECR: No permission"
        echo ""
        echo "You added the IAM policies, but they may not be applied yet."
        echo ""
        echo "Solutions:"
        echo "1. Wait 1-2 minutes for IAM changes to propagate"
        echo "2. Generate new access keys:"
        echo "   - Go to: https://console.aws.amazon.com/iam/"
        echo "   - Users → tradingagents → Security credentials"
        echo "   - Create new access key"
        echo "   - Run: aws configure"
        echo "   - Enter the NEW access key"
    else
        echo "✅ ECR: OK"
    fi

    # Test App Runner
    echo "Testing App Runner access..."
    if aws apprunner list-services --region us-east-1 2>&1 | grep -q "AccessDeniedException"; then
        echo "❌ App Runner: No permission"
    else
        echo "✅ App Runner: OK"
    fi
fi

echo ""
echo "---"
echo "After fixing credentials, run:"
echo "  ./deploy-aws.sh"
