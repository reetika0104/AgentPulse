#!/bin/bash
# ─── PULSE App Runner Deployment ─────────────────────────────────────────────
# Deploys the PULSE backend to AWS App Runner
# Usage: ./deploy-apprunner.sh [environment]
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

ENVIRONMENT="${1:-production}"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="pulse-backend"
IMAGE_TAG="${ENVIRONMENT}-$(date +%Y%m%d%H%M%S)"
SERVICE_NAME="pulse-backend-${ENVIRONMENT}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           PULSE - App Runner Deployment                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ─── Step 1: Create ECR Repository ────────────────────────────────
echo "📦 Setting up ECR repository..."
aws ecr create-repository \
    --repository-name ${ECR_REPO} \
    --region ${REGION} 2>/dev/null || echo "  Repository already exists"

ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}"

# ─── Step 2: Build and Push Docker Image ─────────────────────────
echo "🐳 Building Docker image..."
cd ../../backend
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}
docker build -t ${ECR_REPO}:${IMAGE_TAG} .
docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}
docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_URI}:latest

echo "📤 Pushing to ECR..."
docker push ${ECR_URI}:${IMAGE_TAG}
docker push ${ECR_URI}:latest
echo "✅ Image pushed: ${ECR_URI}:${IMAGE_TAG}"

# ─── Step 3: Create/Update App Runner Service ─────────────────────
echo "🚀 Deploying to App Runner..."

# Create App Runner access role for ECR
cat > /tmp/apprunner-trust.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "build.apprunner.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
    --role-name pulse-apprunner-ecr-role \
    --assume-role-policy-document file:///tmp/apprunner-trust.json 2>/dev/null || true

aws iam attach-role-policy \
    --role-name pulse-apprunner-ecr-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess 2>/dev/null || true

ACCESS_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/pulse-apprunner-ecr-role"

# Check if service exists
SERVICE_EXISTS=$(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='${SERVICE_NAME}'].ServiceArn" --output text --region ${REGION})

if [ -z "${SERVICE_EXISTS}" ]; then
    echo "  Creating new App Runner service..."
    aws apprunner create-service \
        --service-name ${SERVICE_NAME} \
        --source-configuration "{
            \"AuthenticationConfiguration\": {
                \"AccessRoleArn\": \"${ACCESS_ROLE_ARN}\"
            },
            \"ImageRepository\": {
                \"ImageIdentifier\": \"${ECR_URI}:${IMAGE_TAG}\",
                \"ImageRepositoryType\": \"ECR\",
                \"ImageConfiguration\": {
                    \"Port\": \"8000\",
                    \"RuntimeEnvironmentVariables\": {
                        \"ENVIRONMENT\": \"${ENVIRONMENT}\",
                        \"AWS_REGION\": \"${REGION}\"
                    }
                }
            },
            \"AutoDeploymentsEnabled\": true
        }" \
        --instance-configuration "{
            \"Cpu\": \"1024\",
            \"Memory\": \"2048\"
        }" \
        --health-check-configuration "{
            \"Protocol\": \"HTTP\",
            \"Path\": \"/api/v1/health\",
            \"Interval\": 10,
            \"Timeout\": 5,
            \"HealthyThreshold\": 1,
            \"UnhealthyThreshold\": 5
        }" \
        --region ${REGION} \
        --tags Key=Project,Value=PULSE Key=Environment,Value=${ENVIRONMENT}
else
    echo "  Updating existing App Runner service..."
    aws apprunner update-service \
        --service-arn ${SERVICE_EXISTS} \
        --source-configuration "{
            \"AuthenticationConfiguration\": {
                \"AccessRoleArn\": \"${ACCESS_ROLE_ARN}\"
            },
            \"ImageRepository\": {
                \"ImageIdentifier\": \"${ECR_URI}:${IMAGE_TAG}\",
                \"ImageRepositoryType\": \"ECR\",
                \"ImageConfiguration\": {
                    \"Port\": \"8000\"
                }
            }
        }" \
        --region ${REGION}
fi

echo ""
echo "✅ App Runner deployment initiated!"
echo ""
echo "Check status:"
echo "  aws apprunner list-services --region ${REGION}"
echo ""
