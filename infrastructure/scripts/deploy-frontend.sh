#!/bin/bash
# ─── PULSE Frontend Deployment (S3 + CloudFront) ─────────────────────────────
# Deploys the React frontend to S3 with CloudFront CDN
# Usage: ./deploy-frontend.sh [environment]
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

ENVIRONMENT="${1:-production}"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="pulse-frontend-${ACCOUNT_ID}-${ENVIRONMENT}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          PULSE - Frontend Deployment                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ─── Step 1: Build Frontend ───────────────────────────────────────
echo "🔨 Building frontend..."
cd ../../frontend
npm ci
npm run build
echo "✅ Frontend built"

# ─── Step 2: Create S3 Bucket ────────────────────────────────────
echo "📦 Setting up S3 bucket..."
aws s3 mb s3://${BUCKET_NAME} --region ${REGION} 2>/dev/null || echo "  Bucket exists"

# Enable static website hosting
aws s3 website s3://${BUCKET_NAME} \
    --index-document index.html \
    --error-document index.html

echo "✅ S3 configured for static hosting"

# ─── Step 3: Upload Build ────────────────────────────────────────
echo "📤 Uploading frontend assets..."
aws s3 sync dist/ s3://${BUCKET_NAME} \
    --delete \
    --cache-control "public,max-age=31536000,immutable" \
    --exclude "index.html"

# Upload index.html with no-cache
aws s3 cp dist/index.html s3://${BUCKET_NAME}/index.html \
    --cache-control "no-cache,no-store,must-revalidate"

echo "✅ Frontend uploaded"

# ─── Step 4: Create CloudFront Distribution ───────────────────────
echo "🌐 Setting up CloudFront..."

DISTRIBUTION_EXISTS=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?Comment=='PULSE Frontend ${ENVIRONMENT}'].Id" \
    --output text 2>/dev/null)

if [ -z "${DISTRIBUTION_EXISTS}" ]; then
    cat > /tmp/cf-config.json << EOF
{
    "CallerReference": "pulse-${ENVIRONMENT}-$(date +%s)",
    "Comment": "PULSE Frontend ${ENVIRONMENT}",
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-${BUCKET_NAME}",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
        "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
        "ForwardedValues": {"QueryString": false, "Cookies": {"Forward": "none"}},
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000,
        "Compress": true
    },
    "Origins": {
        "Quantity": 1,
        "Items": [{
            "Id": "S3-${BUCKET_NAME}",
            "DomainName": "${BUCKET_NAME}.s3.amazonaws.com",
            "S3OriginConfig": {"OriginAccessIdentity": ""}
        }]
    },
    "Enabled": true,
    "DefaultRootObject": "index.html",
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [{
            "ErrorCode": 404,
            "ResponseCode": "200",
            "ResponsePagePath": "/index.html",
            "ErrorCachingMinTTL": 300
        }]
    }
}
EOF

    aws cloudfront create-distribution \
        --distribution-config file:///tmp/cf-config.json
    echo "✅ CloudFront distribution created"
else
    echo "  CloudFront distribution already exists: ${DISTRIBUTION_EXISTS}"
    aws cloudfront create-invalidation \
        --distribution-id ${DISTRIBUTION_EXISTS} \
        --paths "/*"
    echo "✅ CloudFront cache invalidated"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Frontend Deployment Complete!                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "S3 Bucket: ${BUCKET_NAME}"
echo "Website URL: http://${BUCKET_NAME}.s3-website-${REGION}.amazonaws.com"
echo ""
