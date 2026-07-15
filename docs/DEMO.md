# PULSE Demo Script

## Quick Demo (2 minutes)

### 1. Show Architecture
Open the README.md and explain the architecture diagram showing the autonomous flow:
- EventBridge → Lambda → Backend → Bedrock → Delivery

### 2. Start Local Demo

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

### 3. Dashboard Walkthrough

1. Open http://localhost:3000
2. Login: `admin` / `pulse2026`
3. Show the dashboard cards:
   - Agent Status (Active with pulse animation)
   - Next Scheduled Run (7:00 AM cron)
   - Last Execution status
   - AI Model (Nova Micro)
4. Show the Service Health panel
5. Click **"Run Now"** to trigger a brief

### 4. Show the Generated Brief

After clicking Run Now:
- Priority Score with color coding
- Executive Summary
- Meeting preparation notes
- Urgent items
- Weather recommendation
- Productivity tips
- Delivery status (Email/Telegram/Slack)

### 5. Show AWS Infrastructure

```bash
# Show the CloudFormation stack
aws cloudformation describe-stacks --stack-name pulse-stack-production

# Show the EventBridge schedule
aws scheduler get-schedule --name pulse-daily-brief-production

# Show Lambda function
aws lambda get-function --function-name pulse-morning-brief-production

# Show CloudWatch metrics
aws cloudwatch get-metric-data ...
```

### 6. Key Technical Points

- **Zero interaction**: EventBridge fires → Lambda runs → Brief delivered
- **Amazon Bedrock Nova**: Generates intelligent, personalized briefs
- **6 data sources**: Calendar, Gmail, GitHub, Weather, Notion, RSS
- **3 delivery channels**: SES Email, Telegram, Slack
- **Production-ready**: Error handling, retries, structured logging, JWT auth
- **12+ AWS services**: All used naturally in the architecture

### 7. Explain the "Always-On" Nature

> "Once deployed, PULSE never stops. Every morning at 7 AM, without any human
> touching a button, it wakes up, gathers intelligence, thinks using AI, and
> delivers a comprehensive brief. The user wakes up to their brief already
> waiting in their inbox, Telegram, and Slack."

---

## API Demo

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"pulse2026"}' | jq -r .access_token)

# Trigger brief
curl -X POST http://localhost:8000/api/v1/brief/trigger \
  -H "Authorization: Bearer $TOKEN"

# Get latest brief
curl http://localhost:8000/api/v1/brief/latest \
  -H "Authorization: Bearer $TOKEN"

# Get agent status
curl http://localhost:8000/api/v1/status \
  -H "Authorization: Bearer $TOKEN"
```
