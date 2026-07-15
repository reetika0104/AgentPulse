# ⚡ PULSE — Personal Unified Life & Productivity Executive

> **An always-on, fully autonomous AI agent** that wakes itself up every morning, collects intelligence from 6 connected sources, generates a personalized daily brief using Amazon Bedrock (Nova), and delivers it via Email, Telegram, and Slack — with zero human interaction.

![AWS](https://img.shields.io/badge/AWS-Production_Ready-FF9900?style=for-the-badge&logo=amazonaws)
![Bedrock](https://img.shields.io/badge/Amazon_Bedrock-Nova-232F3E?style=for-the-badge&logo=amazonaws)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)

---

## 🎯 Challenge: Build an Always-On Agent

PULSE satisfies **every judging criterion** for the AWS Builder Center "Build an Always-On Agent Weekend Challenge":

| Criterion | How PULSE Delivers |
|-----------|-------------------|
| **Always-On Agent** | EventBridge Scheduler triggers daily at 7 AM — zero human interaction |
| **Amazon Bedrock** | Nova model generates intelligent, structured Morning Briefs |
| **Autonomous Operation** | Full pipeline: Observe → Reason → Plan → Generate → Deliver → Learn |
| **Multiple AWS Services** | 12+ services used naturally in production architecture |
| **Real-World Value** | Actionable daily intelligence with priority scores and recommendations |
| **Production Quality** | Docker, error handling, retry logic, structured logging, JWT auth |

---

## 🧠 Agent Intelligence: Cognitive Pipeline

PULSE operates on a **6-phase autonomous cognitive loop** — no prompts, no buttons, no interaction:

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  OBSERVE │───▶│  REASON  │───▶│   PLAN   │───▶│ GENERATE │───▶│ DELIVER  │───▶│  LEARN   │
│          │    │          │    │          │    │          │    │          │    │          │
│ Collect  │    │ Analyze  │    │Prioritize│    │ Bedrock  │    │ SES +    │    │CloudWatch│
│ 6 sources│    │ patterns │    │ actions  │    │ Nova AI  │    │ Telegram │    │ metrics  │
│ parallel │    │ urgency  │    │ focus    │    │ generate │    │ + Slack  │    │ outcomes │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

---

## 🏗️ Architecture

```
                         ┌─────────────────────────────┐
                         │   Amazon EventBridge         │
                         │   Scheduler (cron: 7 AM)     │
                         └─────────────┬───────────────┘
                                       │ Triggers daily
                                       ▼
                         ┌─────────────────────────────┐
                         │      AWS Lambda              │
                         │   (Execution Trigger)        │
                         └─────────────┬───────────────┘
                                       │ Invokes
                                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (App Runner)                     │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                    OBSERVE Phase                             │   │
│  │  ┌─────────┐ ┌──────┐ ┌────────┐ ┌─────────┐ ┌─────────┐ │   │
│  │  │Calendar │ │Gmail │ │GitHub  │ │Weather │ │ Notion  │ │   │
│  │  └────┬────┘ └──┬───┘ └───┬────┘ └────┬────┘ └────┬────┘ │   │
│  │       └──────────┴─────────┴───────────┴───────────┘       │   │
│  └────────────────────────────┬───────────────────────────────┘   │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │         REASON + PLAN → GENERATE (Bedrock Nova)           │     │
│  │    ┌─────────────────────────────────────────────────┐    │     │
│  │    │  AWS Secrets Manager ──▶ Amazon Bedrock (Nova)   │    │     │
│  │    │                          Converse API            │    │     │
│  │    │                          Structured JSON output  │    │     │
│  │    └─────────────────────────────────────────────────┘    │     │
│  └────────────────────────────┬─────────────────────────────┘     │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │                    DELIVER Phase                           │     │
│  │    ┌──────────┐    ┌───────────┐    ┌────────────┐       │     │
│  │    │Amazon SES│    │ Telegram  │    │   Slack    │       │     │
│  │    │  Email   │    │    Bot    │    │  Webhook   │       │     │
│  │    └──────────┘    └───────────┘    └────────────┘       │     │
│  └──────────────────────────────────────────────────────────┘     │
│                               ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │                     LEARN Phase                            │     │
│  │    ┌──────────────┐  ┌──────────┐  ┌────────────────┐    │     │
│  │    │ CloudWatch   │  │  SQLite  │  │  S3 Archive    │    │     │
│  │    │ Metrics +    │  │ History  │  │  Brief Storage │    │     │
│  │    │ Alarms       │  │          │  │                │    │     │
│  │    └──────────────┘  └──────────┘  └────────────────┘    │     │
│  └──────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
                               ▲
                               │ Dashboard
┌──────────────────────────────┴───────────────────────────────────┐
│              React Dashboard (CloudFront CDN)                      │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ ┌───────────┐  │
│  │ Brief  │ │ Agent    │ │ Timeline │ │ Health │ │  Metrics  │  │
│  │ Card   │ │ Workflow │ │          │ │ Status │ │  Panel    │  │
│  └────────┘ └──────────┘ └──────────┘ └────────┘ └───────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ AWS Services Used (12+)

| # | Service | Purpose | Integration |
|---|---------|---------|-------------|
| 1 | **Amazon Bedrock** | AI brief generation | Nova Micro via Converse API |
| 2 | **EventBridge Scheduler** | Daily cron trigger | `cron(0 7 * * ? *)` |
| 3 | **AWS Lambda** | Serverless execution | Python 3.12, 512MB, 300s timeout |
| 4 | **Amazon CloudWatch** | Logs, metrics, alarms | Custom namespace `PULSE/Agent` |
| 5 | **AWS Secrets Manager** | Credential storage | Prefix: `pulse/` |
| 6 | **Amazon SES** | Email delivery | HTML + plaintext briefs |
| 7 | **Amazon S3** | Brief archive | Lifecycle to Glacier at 90 days |
| 8 | **AWS App Runner** | Backend hosting | Auto-scaling FastAPI container |
| 9 | **Amazon CloudFront** | Frontend CDN | React SPA distribution |
| 10 | **Amazon Route 53** | DNS management | Custom domain routing |
| 11 | **Amazon ECR** | Container registry | Docker image storage |
| 12 | **AWS IAM** | Security | Least-privilege roles |

---

## 📂 Project Structure

```
pulse/
├── backend/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── agents/            # AI Agent Logic
│   │   │   ├── orchestrator.py   # 6-phase pipeline
│   │   │   └── bedrock_agent.py  # Bedrock Converse API
│   │   ├── api/               # REST Endpoints
│   │   │   └── routes.py        # JWT-protected routes
│   │   ├── core/              # Infrastructure
│   │   │   ├── config.py        # Pydantic settings
│   │   │   ├── database.py      # SQLite + migrations
│   │   │   ├── logging.py       # JSON structured logs
│   │   │   └── security.py      # JWT auth
│   │   ├── delivery/          # Output Channels
│   │   │   ├── ses_delivery.py   # Amazon SES
│   │   │   ├── telegram_delivery.py
│   │   │   └── slack_delivery.py
│   │   └── services/          # Data Collectors
│   │       ├── calendar_service.py
│   │       ├── gmail_service.py
│   │       ├── github_service.py
│   │       ├── weather_service.py
│   │       ├── notion_service.py
│   │       ├── rss_service.py
│   │       └── secrets_service.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # React + Vite Dashboard
│   ├── src/
│   │   ├── components/        # UI Components
│   │   │   ├── AgentWorkflow.jsx
│   │   │   ├── BriefCard.jsx
│   │   │   ├── ExecutionLogs.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── MetricsPanel.jsx
│   │   │   ├── ServiceHealth.jsx
│   │   │   └── StatusCard.jsx
│   │   ├── pages/
│   │   └── utils/
│   └── package.json
├── infrastructure/             # AWS Infrastructure
│   ├── cloudformation/        # IaC Templates
│   ├── lambda/                # Lambda Function
│   └── scripts/               # Deployment Automation
├── docs/
│   ├── DEPLOYMENT.md
│   ├── DEMO.md
│   └── screenshots/
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- AWS CLI v2 (configured with credentials)
- Python 3.12+
- Node.js 18+
- Docker (for AWS deployment)

### Local Development

```bash
# Clone
git clone git@github.com:reetika0104/AgentPulse.git
cd AgentPulse

# Backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # Configure your settings
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Login Credentials (Demo)
```
Username: admin
Password: pulse2026
```

---

## ☁️ AWS Deployment

### One-Command Deploy

```bash
cd infrastructure/scripts
./deploy.sh production          # CloudFormation + Lambda
./deploy-apprunner.sh production # Backend on App Runner
./deploy-frontend.sh production  # Frontend on S3 + CloudFront
```

### Detailed Steps

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the complete guide.

---

## 💰 Cost Estimate (AWS Free Tier Friendly)

| Service | Monthly Cost | Notes |
|---------|-------------|-------|
| Lambda | **$0.00** | 30 invocations × 300s = Free Tier |
| EventBridge | **$0.00** | Free for schedule-based triggers |
| Bedrock (Nova Micro) | **~$0.50** | ~30 calls × ~4K tokens |
| SES | **$0.00** | First 62K emails free from EC2/Lambda |
| S3 | **$0.01** | Minimal storage for briefs |
| CloudWatch | **$0.00** | Free tier covers basic metrics |
| App Runner | **~$5.00** | Smallest instance |
| **Total** | **~$5.50/month** | |

---

## 🔐 Security

- **JWT Authentication** — All API endpoints protected
- **AWS Secrets Manager** — No hardcoded credentials
- **IAM Least Privilege** — Scoped policies per service
- **HTTPS Only** — CloudFront enforces TLS
- **Input Validation** — Pydantic schemas on all inputs
- **Structured Logging** — Full audit trail in CloudWatch

---

## 📊 CloudWatch Metrics

PULSE publishes custom metrics to the `PULSE/Agent` namespace:

| Metric | Description |
|--------|-------------|
| `ExecutionDuration` | Pipeline duration in seconds |
| `ExecutionCount` | Total runs (success/failure dimensions) |
| `TokensUsed` | Bedrock token consumption |
| `SourcesCollected` | Number of sources responding |
| `DeliverySuccess` | Successful deliveries per channel |

---

## 📸 Screenshots

| Dashboard | Agent Workflow |
|-----------|---------------|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Workflow](docs/screenshots/workflow.png) |

| Brief Card | Service Health |
|------------|---------------|
| ![Brief](docs/screenshots/brief.png) | ![Health](docs/screenshots/health.png) |

---

## 🧪 Demo Script

```bash
# 1. Start backend
cd backend && uvicorn app.main:app --port 8000

# 2. Start frontend  
cd frontend && npm run dev

# 3. Open http://localhost:3000
# 4. Login: admin / pulse2026
# 5. Click "Run Agent" — watch the pipeline execute
# 6. View: Brief Card, Execution Timeline, Agent Metrics, Service Health
```

---

## 🗺️ Future Roadmap

- [ ] **Multi-user support** with Cognito
- [ ] **DynamoDB migration** for serverless data layer
- [ ] **Voice briefing** via Amazon Polly
- [ ] **Feedback loop** — user rates brief quality
- [ ] **Custom data sources** — Jira, Linear, Confluence
- [ ] **Weekly digest** in addition to daily
- [ ] **Mobile app** with push notifications

---

## 📋 Technical Highlights

- **Bedrock Converse API** — Structured JSON output, token tracking
- **Async Pipeline** — All 6 data sources collected in parallel
- **Graceful Degradation** — Falls back to demo data if APIs unavailable
- **Retry Logic** — EventBridge retries up to 3 times on failure
- **Structured Logging** — JSON format, CloudWatch-compatible
- **SQLite → DynamoDB** — Easy migration path when needed
- **Dark Theme Dashboard** — Glassmorphism, professional animations
- **Phase Timing** — Each pipeline step measured and reported

---

## 📄 License

MIT License — Built for AWS Builder Center Weekend Challenge 2026.

---

<p align="center">
  <strong>⚡ PULSE — Your AI Digital Chief of Staff</strong><br/>
  <em>Always-On • Fully Autonomous • Powered by Amazon Bedrock</em><br/><br/>
  <sub>Built with ❤️ for the AWS Builder Center Weekend Challenge</sub>
</p>
