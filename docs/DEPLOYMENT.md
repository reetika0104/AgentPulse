# PULSE Deployment Guide

## Complete AWS Deployment

### Step 1: Prerequisites

```bash
# Verify AWS CLI
aws sts get-caller-identity

# Verify Docker
docker --version

# Verify Node.js
node --version
npm --version
```

### Step 2: Deploy Infrastructure (CloudFormation)

```bash
cd infrastructure/scripts
chmod +x *.sh

# Deploy the full CloudFormation stack
./deploy.sh production
```

This creates:
- Lambda function
- EventBridge Scheduler (daily at 7 AM)
- S3 bucket for brief storage
- IAM roles and policies
- CloudWatch dashboard and alarms
- Secrets Manager secrets
- SES configuration set

### Step 3: Configure Secrets

```bash
aws secretsmanager update-secret \
    --secret-id pulse/api-keys \
    --secret-string '{
        "github_token": "ghp_your_token",
        "weather_api_key": "your_openweather_key",
        "telegram_bot_token": "your_bot_token",
        "telegram_chat_id": "your_chat_id",
        "slack_webhook_url": "https://hooks.slack.com/...",
        "notion_api_key": "secret_..."
    }'
```

### Step 4: Configure SES

```bash
./setup-ses.sh sender@yourdomain.com recipient@yourdomain.com
```

### Step 5: Deploy Backend (App Runner)

```bash
./deploy-apprunner.sh production
```

### Step 6: Deploy Frontend (S3 + CloudFront)

```bash
./deploy-frontend.sh production
```

### Step 7: Update Lambda with Backend URL

```bash
# Get App Runner URL
APP_RUNNER_URL=$(aws apprunner list-services \
    --query "ServiceSummaryList[?ServiceName=='pulse-backend-production'].ServiceUrl" \
    --output text)

# Update Lambda environment
aws lambda update-function-configuration \
    --function-name pulse-morning-brief-production \
    --environment "Variables={PULSE_API_URL=https://${APP_RUNNER_URL},PULSE_API_KEY=pulse2026}"
```

### Step 8: Verify

```bash
# Test Lambda manually
aws lambda invoke \
    --function-name pulse-morning-brief-production \
    --payload '{"source": "manual-test"}' \
    /tmp/pulse-response.json

cat /tmp/pulse-response.json

# Check CloudWatch logs
aws logs tail /aws/lambda/pulse-morning-brief-production --follow
```

---

## Route 53 (Optional)

```bash
# Create hosted zone
aws route53 create-hosted-zone --name pulse.yourdomain.com --caller-reference $(date +%s)

# Point to CloudFront distribution
# Add CNAME record pointing to your CloudFront domain
```

---

## Monitoring

```bash
# View CloudWatch dashboard
# Console: CloudWatch > Dashboards > PULSE-Agent-production

# View execution metrics
aws cloudwatch get-metric-statistics \
    --namespace "PULSE/Agent" \
    --metric-name "ExecutionCount" \
    --dimensions Name=AgentName,Value=PULSE Name=Status,Value=success \
    --start-time $(date -d '7 days ago' --iso-8601=seconds) \
    --end-time $(date --iso-8601=seconds) \
    --period 86400 \
    --statistics Sum
```
