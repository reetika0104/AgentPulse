# ⚡ PULSE — AI Digital Chief of Staff

> An always-on AI agent that runs autonomously every morning, collects intelligence from multiple sources, generates a personalized daily brief using Amazon Bedrock (Nova), and delivers it through email, Telegram, and Slack — with zero human interaction required.

![AWS](https://img.shields.io/badge/AWS-Powered-FF9900?style=flat-square&logo=amazonaws)
![Bedrock](https://img.shields.io/badge/Amazon_Bedrock-Nova-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🎯 What is PULSE?

PULSE is a **production-quality Always-On AI Agent** built for the AWS Builder Center Weekend Challenge. It wakes itself up every morning at 7:00 AM, gathers intelligence from 6+ connected sources, processes everything through Amazon Bedrock (Nova), and delivers a comprehensive Morning Brief automatically.

**No buttons to press. No prompts to write. No interaction needed.**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PULSE Architecture                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐     ┌──────────────────┐                         │
│  │ Amazon EventBridge│────▶│   AWS Lambda      │                         │
│  │    Scheduler      │     │  (Trigger Agent)  │                         │
│  │  (Cron: 7AM)     │     └────────┬─────────┘                         │
│  └──────────────────┘              │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │              PULSE Backend (FastAPI on App Runner)            │       │
│  │                                                              │       │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐    │       │
│  │  │  Collectors  │  │ AI Agent     │  │   Delivery      │    │       │
│  │  │             │  │  (Bedrock)   │  │                 │    │       │
│  │  │ • Calendar  │──▶│ • Nova Model │──▶│ • Amazon SES   │    │       │
│  │  │ • Gmail     │  │ • Prompts   │  │ • Telegram     │    │       │
│  │  │ • GitHub    │  │ • Analysis  │  │ • Slack        │    │       │
│  │  │ • Weather   │  │             │  │                 │    │       │
│  │  │ • Notion    │  └──────────────┘  └─────────────────┘    │       │
│  │  │ • RSS News  │                                            │       │
│  │  └─────────────┘                                            │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  ┌──────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐       │
│  │ CloudWatch   │  │  Secrets   │  │   S3       │  │ CloudFront│       │
│  │ (Logs/Alarm) │  │  Manager   │  │ (Storage)  │  │ (CDN)     │       │
│  └──────────────┘  └────────────┘  └────────────┘  └──────────┘       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │           Frontend Dashboard (React + Vite)                  │       │
│  │  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌───────────────┐    │       │
│  │  │  Brief   │ │   Logs   │ │ Health │ │ Service Status│    │       │
│  │  │  Card    │ │  Panel   │ │ Cards  │ │    Panel      │    │       │
│  │  └──────────┘ └──────────┘ └────────┘ └───────────────┘    │       │
│  └─────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ AWS Services Used

| Service | Purpose |
|---------|---------|
| **Amazon Bedrock** | AI brief generation using Nova model |
| **Amazon EventBridge Scheduler** | Cron-based daily trigger (7:00 AM) |
| **AWS Lambda** | Serverless execution trigger |
| **Amazon CloudWatch** | Logging, metrics, alarms, dashboard |
| **AWS Secrets Manager** | Secure credential storage |
| **Amazon SES** | Email delivery |
| **Amazon S3** | Brief archive storage |
| **AWS App Runner** | Backend hosting (FastAPI) |
| **Amazon CloudFront** | Frontend CDN distribution |
| **Amazon Route 53** | DNS management |
| **Amazon ECR** | Container registry |
| **AWS IAM** | Roles and permissions |

---

## 📂 Project Structure

```
pulse/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent logic (Bedrock orchestration)
│   │   ├── api/             # FastAPI REST endpoints
│   │   ├── core/            # Config, security, database, logging
│   │   ├── delivery/        # SES, Telegram, Slack delivery
│   │   ├── models/          # Data models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Data collectors (GitHub, Gmail, etc.)
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/      # React UI components
│   │   ├── pages/           # Dashboard & Login pages
│   │   ├── hooks/           # React hooks
│   │   └── utils/           # API client
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── infrastructure/
│   ├── cloudformation/      # CloudFormation templates
│   ├── lambda/              # Lambda function code
│   └── scripts/             # Deployment scripts
├── docs/
│   └── screenshots/
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.12+
- Node.js 18+
- Docker (for deployment)

### 1. Clone & Setup

```bash
git clone git@github.com:reetika0104/AgentPulse.git
cd AgentPulse
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Deploy to AWS

```bash
cd infrastructure/scripts
chmod +x deploy.sh deploy-apprunner.sh
./deploy.sh production
./deploy-apprunner.sh production
```

---

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AWS_REGION` | AWS region | Yes |
| `BEDROCK_MODEL_ID` | Bedrock model (default: amazon.nova-micro-v1:0) | Yes |
| `SES_SENDER_EMAIL` | Verified SES sender email | No |
| `SES_RECIPIENT_EMAIL` | Email recipient | No |
| `GITHUB_TOKEN` | GitHub personal access token | No |
| `WEATHER_API_KEY` | OpenWeatherMap API key | No |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | No |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | No |
| `NOTION_API_KEY` | Notion integration key | No |
| `SECRET_KEY` | JWT signing key | Yes |

---

## 🤖 How It Works

1. **⏰ EventBridge Scheduler** fires at 7:00 AM every day
2. **🔄 Lambda Function** is invoked, triggers the PULSE backend
3. **📡 Data Collectors** gather information from 6 sources in parallel
4. **🧠 Amazon Bedrock (Nova)** analyzes all data and generates the Morning Brief
5. **📬 Delivery Channels** send the brief via Email, Telegram, and Slack
6. **📊 CloudWatch** logs metrics and monitors execution health

---

## 📸 Screenshots

> Screenshots are stored in `docs/screenshots/`

- Dashboard Overview
- Morning Brief Card
- Execution Logs
- Service Health Panel
- Login Page

---

## 🧪 Demo Script

```bash
# 1. Start the backend
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. Start the frontend
cd frontend && npm run dev

# 3. Login with demo credentials
# Username: admin
# Password: pulse2026

# 4. Click "Run Now" to trigger a brief manually

# 5. View the generated brief in the dashboard
```

---

## 📋 AWS Deployment Commands

```bash
# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file infrastructure/cloudformation/pulse-stack.yaml \
  --stack-name pulse-stack-production \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Update Lambda code
aws lambda update-function-code \
  --function-name pulse-morning-brief-production \
  --zip-file fileb://infrastructure/lambda/lambda-package.zip

# Verify SES email
aws ses verify-email-identity --email-address your@email.com

# Create secrets
aws secretsmanager create-secret \
  --name pulse/api-keys \
  --secret-string '{"github_token":"...","weather_api_key":"..."}'

# Check CloudWatch logs
aws logs tail /aws/lambda/pulse-morning-brief-production --follow
```

---

## 🏆 Challenge Criteria Satisfaction

| Criterion | How PULSE Satisfies It |
|-----------|----------------------|
| Always-On Agent | Runs daily via EventBridge Scheduler — zero interaction |
| Amazon Bedrock | Nova model generates personalized Morning Briefs |
| AWS Services | 12+ AWS services used naturally in architecture |
| Production Quality | Docker, CI/CD, error handling, retry, structured logging |
| No User Interaction | Fully autonomous — scheduled, collected, generated, delivered |
| Multiple Data Sources | 6 sources: Calendar, Gmail, GitHub, Weather, Notion, RSS |
| Useful Output | Actionable daily brief with priorities, urgency scores, tips |

---

## 📄 License

MIT License — Built for the AWS Builder Center Weekend Challenge 2026.

---

<p align="center">
  <strong>⚡ PULSE — Your AI Digital Chief of Staff</strong><br/>
  <em>Powered by Amazon Bedrock | Built on AWS</em>
</p>
