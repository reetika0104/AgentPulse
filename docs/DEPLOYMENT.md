# PULSE — Complete AWS Deployment Guide

## Architecture Overview

PULSE uses 12+ AWS services in a production architecture:

```
EventBridge Scheduler (7 AM daily)
  └─▶ AWS Lambda (trigger)
        └─▶ App Runner (FastAPI backend)
              ├─▶ Secrets Manager (credentials)
              ├─▶ Amazon Bedrock Nova (AI generation)
              ├─▶ Amazon SES (email delivery)
              ├─▶ CloudWatch (metrics + logs)
              └─▶ S3 (brief archive)

CloudFront CDN ──▶ S3 (React frontend)
Route 53 ──▶ CloudFront
```

---

## Prerequisites

```bash
# Verify AWS CLI v2
aws --version
aws sts get-caller-identity

# Verify tools
python --version    # 3.12+
node --version      # 18+
docker --version    # For App Runner deployment
```

---

## Step 1: Deploy Infrastructure (CloudFormation)

```bash
cd infrastructure/scripts
chmod +x *.sh

# Deploy the complete stack
./deploy.sh production
```

**What this creates:**
- ✅ Lambda function (`pulse-morning-brief-production`)
- ✅ EventBridge Scheduler (daily at 7:00 AM Eastern)
- ✅ S3 bucket for brief storage
- ✅ IAM roles with least-privilege policies
- ✅ CloudWatch dashboard + alarms
- ✅ Secrets Manager secret (`pulse/api-keys`)
- ✅ SES configuration set

---

## Step 2: Configure Secrets

```bash
aws secretsmanager update-secret \
    --secret-id pulse/api-keys \
    --secret-string '{
        "github_token": "ghp_your_token_here",
        "weather_api_key": "your_openweathermap_key",
        "telegram_bot_token": "123456:ABC-DEF",
        "telegram_chat_id": "your_chat_id",
        "slack_webhook_url": "https://hooks.slack.com/services/T.../B.../xxx",
        "notion_api_key": "secret_xxx"
    }' \
    --region us-east-1
```

---

## Step 3: Configure Amazon SES

```bash
# Verify sender email
aws ses verify-email-identity \
    --email-address pulse@yourdomain.com \
    --region us-east-1

# Verify recipient (required in sandbox)
aws ses verify-email-identity \
    --email-address you@yourdomain.com \
    --region us-east-1
```

> **Note:** In SES sandbox mode, both sender and recipient must be verified.
> To exit sandbox: [Request production access](https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html)

---

## Step 4: Deploy Backend (App Runner)

```bash
./deploy-apprunner.sh production
```

**What this does:**
1. Creates ECR repository
2. Builds Docker image
3. Pushes to ECR
4. Creates/updates App Runner service
5. Configures health checks on `/api/v1/health`

---

## Step 5: Update Lambda with Backend URL

```bash
# Get the App Runner service URL
APP_URL=$(aws apprunner list-services \
    --query "ServiceSummaryList[?ServiceName=='pulse-backend-production'].ServiceUrl" \
    --output text --region us-east-1)

# Update Lambda environment variable
aws lambda update-function-configuration \
    --function-name pulse-morning-brief-production \
    --environment "Variables={
        PULSE_API_URL=https://${APP_URL},
        PULSE_API_KEY=pulse2026,
        AWS_REGION_NAME=us-east-1,
        BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
    }" \
    --region us-east-1
```

---

## Step 6: Deploy Frontend (CloudFront + S3)

```bash
./deploy-frontend.sh production
```

**What this does:**
1. Builds the React app (`npm run build`)
2. Creates S3 bucket with website hosting
3. Uploads with correct cache headers
4. Creates CloudFront distribution with HTTPS
5. Configures SPA routing (404 → index.html)

---

## Step 7: Route 53 (Optional)

```bash
# Create hosted zone
aws route53 create-hosted-zone \
    --name pulse.yourdomain.com \
    --caller-reference $(date +%s)

# Point to CloudFront (create CNAME or A-Alias record)
```

---

## Step 8: Verify Everything

```bash
# Test Lambda manually
aws lambda invoke \
    --function-name pulse-morning-brief-production \
    --payload '{"source": "aws.scheduler", "detail-type": "Scheduled Event"}' \
    /tmp/pulse-output.json --region us-east-1

cat /tmp/pulse-output.json

# Check CloudWatch logs
aws logs tail /aws/lambda/pulse-morning-brief-production --follow --region us-east-1

# Check CloudWatch metrics
aws cloudwatch list-metrics --namespace "PULSE/Agent" --region us-east-1

# Verify App Runner health
curl https://<your-app-runner-url>/api/v1/health
```

---

## Monitoring & Alerts

```bash
# View the PULSE CloudWatch dashboard
# Console: CloudWatch → Dashboards → PULSE-Agent-production

# Check alarm status
aws cloudwatch describe-alarms \
    --alarm-name-prefix "PULSE" \
    --region us-east-1
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Lambda timeout | Increase to 300s, check App Runner URL |
| SES bounce | Verify email addresses, check sandbox status |
| Bedrock access | Enable model access in Bedrock console |
| App Runner 502 | Check Docker build, verify health endpoint |
| EventBridge not firing | Verify schedule timezone, check state is ENABLED |

---

## Cost Optimization

- Use `amazon.nova-micro-v1:0` (cheapest Bedrock model)
- Lambda at 512MB is sufficient
- App Runner pauses when idle (pay per request)
- S3 lifecycle moves briefs to Glacier at 90 days
- CloudWatch retains logs for 30 days only
