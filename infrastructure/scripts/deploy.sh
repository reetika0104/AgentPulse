#!/bin/bash
# ─── PULSE Deployment Script ──────────────────────────────────────────────────
# Deploys the complete PULSE infrastructure to AWS
# Usage: ./deploy.sh [environment]
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

ENVIRONMENT="${1:-production}"
PROJECT="pulse"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
STACK_NAME="pulse-stack-${ENVIRONMENT}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           PULSE - AI Digital Chief of Staff                 ║"
echo "║           AWS Deployment Script                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "Account: ${ACCOUNT_ID}"
echo ""

# ─── Step 1: Package Lambda ───────────────────────────────────────
echo "📦 Packaging Lambda function..."
cd ../lambda
rm -f lambda-package.zip
pip install -r requirements.txt -t package/ --quiet
cd package && zip -r ../lambda-package.zip . > /dev/null
cd .. && zip lambda-package.zip handler.py
echo "✅ Lambda packaged"

# ─── Step 2: Upload Lambda to S3 ─────────────────────────────────
DEPLOY_BUCKET="pulse-deploy-${ACCOUNT_ID}"
echo "📤 Uploading Lambda package to S3..."
aws s3 mb s3://${DEPLOY_BUCKET} --region ${REGION} 2>/dev/null || true
aws s3 cp lambda-package.zip s3://${DEPLOY_BUCKET}/lambda/pulse-lambda-${ENVIRONMENT}.zip
echo "✅ Lambda uploaded"

# ─── Step 3: Deploy CloudFormation ────────────────────────────────
echo "🏗️  Deploying CloudFormation stack..."
cd ../cloudformation
aws cloudformation deploy \
    --template-file pulse-stack.yaml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        Environment=${ENVIRONMENT} \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ${REGION} \
    --tags Project=PULSE Environment=${ENVIRONMENT}
echo "✅ CloudFormation deployed"

# ─── Step 4: Update Lambda Code ───────────────────────────────────
echo "🔄 Updating Lambda function code..."
LAMBDA_NAME="pulse-morning-brief-${ENVIRONMENT}"
aws lambda update-function-code \
    --function-name ${LAMBDA_NAME} \
    --s3-bucket ${DEPLOY_BUCKET} \
    --s3-key "lambda/pulse-lambda-${ENVIRONMENT}.zip" \
    --region ${REGION}
echo "✅ Lambda code updated"

# ─── Step 5: Verify Deployment ────────────────────────────────────
echo ""
echo "🔍 Verifying deployment..."
LAMBDA_ARN=$(aws lambda get-function --function-name ${LAMBDA_NAME} --query Configuration.FunctionArn --output text --region ${REGION})
echo "  Lambda ARN: ${LAMBDA_ARN}"

STACK_STATUS=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME} --query 'Stacks[0].StackStatus' --output text --region ${REGION})
echo "  Stack Status: ${STACK_STATUS}"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ PULSE Deployment Complete!                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Configure secrets: aws secretsmanager update-secret --secret-id pulse/api-keys ..."
echo "  2. Verify SES email: aws ses verify-email-identity --email-address your@email.com"
echo "  3. Deploy backend to App Runner (see deploy-apprunner.sh)"
echo "  4. Update Lambda PULSE_API_URL environment variable"
echo ""
