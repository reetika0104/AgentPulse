# PULSE Screenshots

## Dashboard Overview
The main dashboard showing agent status, cognitive pipeline, AI-generated brief, execution timeline, metrics, and AWS service health.

![Dashboard](dashboard.png)

## Agent Cognitive Pipeline
The 6-phase autonomous workflow: Observe → Reason → Plan → Generate → Deliver → Learn. Runs automatically every morning at 7:00 AM without human interaction.

![Workflow](workflow.png)

## Morning Brief Card
AI-generated intelligence brief with priority score, executive summary, urgent items, meeting prep, weather, and productivity tips — all powered by Amazon Bedrock Nova.

![Brief](brief.png)

## Service Health Panel
Real-time status of all 12+ AWS services used in the PULSE architecture.

![Health](health.png)

## Login Page
Secure JWT-authenticated access with professional dark glassmorphism design.

![Login](login.png)

---

## How to Capture Screenshots

```bash
# 1. Start the app
cd backend && uvicorn app.main:app --port 8000 &
cd frontend && npm run dev &

# 2. Open http://localhost:3000
# 3. Login with admin / pulse2026
# 4. Click "Run Agent" to generate a brief
# 5. Use browser DevTools device toolbar for consistent sizing
# 6. Capture at 1400x900 for dashboard, 400x600 for mobile
```
