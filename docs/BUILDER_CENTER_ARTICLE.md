# Weekend Agent Challenge: PULSE — Your Autonomous AI Chief of Staff

Every morning, before I check my phone, a brief is already waiting for me. It covers my meetings, flags urgent emails, surfaces GitHub PRs that need review, tells me the weather, and gives me a priority score for the day. I did not ask for it. I did not click anything. An autonomous agent running on AWS assembled it while I was asleep.

That agent is PULSE — a Personal Unified Life and Productivity Executive that runs entirely unattended, triggered by a schedule, powered by Amazon Bedrock.

## Vision and What the Agent Does

The problem is simple: every morning starts with the same friction. Open calendar. Check email. Scan GitHub. Look at tasks. Check weather. Read news. By the time you've assembled a mental picture of your day, twenty minutes have passed and your focus is already fragmented.

PULSE eliminates that friction. It is not a chatbot you interact with. It is not a dashboard you have to remember to open. It is an autonomous agent that wakes itself up at 7:00 AM via Amazon EventBridge Scheduler, collects data from six sources in parallel, reasons about urgency, generates a personalized intelligence brief through Amazon Bedrock (Nova), and delivers it through email, Telegram, and Slack — all without a single human action triggering it.

The key distinction: this is not a tool you use. It is an agent that works for you while you are not there.

## How I Built It

### Architecture Decisions

I wanted the system to be genuinely autonomous rather than just an API behind a button. That meant the trigger chain had to be fully event-driven:

1. **Amazon EventBridge Scheduler** fires a cron expression (`cron(0 7 * * ? *)`) every morning at 7:00 AM Eastern.
2. **AWS Lambda** receives the event and invokes the PULSE backend.
3. **The backend** (Python FastAPI running on AWS App Runner) executes a six-phase pipeline without any human interaction.

The pipeline phases are: Observe, Reason, Plan, Generate, Deliver, Learn. Each phase is timed independently for observability.

### The Observe Phase

Six data collectors run concurrently using `asyncio.gather`:

- Google Calendar (today's meetings)
- Gmail (unread important emails)
- GitHub (notifications and PRs awaiting review)
- OpenWeatherMap (current conditions)
- Notion (tasks with priority and due dates)
- RSS feeds (tech news)

Each collector is designed to degrade gracefully. If a source is unavailable or unconfigured, it falls back to a structured demo response rather than failing the entire pipeline. This means the agent always produces output, regardless of how many integrations are active.

### The Reason and Plan Phases

Before calling Bedrock, the orchestrator performs a lightweight pre-analysis: it counts meetings, scores urgency based on email volume and critical tasks, and determines a suggested focus area. This reasoning context is passed to Bedrock alongside the raw source data, giving the model structured signals to work with rather than asking it to infer everything from scratch.

### The Generate Phase — Amazon Bedrock

The core generation uses the Bedrock Converse API with `amazon.nova-micro-v1:0`:

```python
response = client.converse(
    modelId="amazon.nova-micro-v1:0",
    messages=[{"role": "user", "content": [{"text": user_prompt}]}],
    system=[{"text": SYSTEM_PROMPT}],
    inferenceConfig={"maxTokens": 4096, "temperature": 0.7, "topP": 0.9},
)
```

The system prompt instructs the model to return structured JSON with a specific schema: priority score, executive summary, meeting prep notes, urgent items with recommended actions, weather advice, and productivity tips. The response parser handles both clean JSON and markdown-wrapped code blocks, since models sometimes wrap output in fences.

I chose Nova Micro for cost efficiency — at roughly 30 invocations per month, the Bedrock cost stays under a dollar.

### The Deliver Phase

Once the brief is generated, it is delivered in parallel through three channels:

- **Amazon SES** — a formatted HTML email with inline CSS
- **Telegram Bot API** — markdown-formatted message
- **Slack Webhook** — Block Kit formatted payload

Each delivery attempt is logged individually with status, timestamp, and any error message.

### The Learn Phase

Every execution records duration, token usage, source availability, and delivery outcomes into SQLite (with a clear migration path to DynamoDB). The Lambda function also publishes custom CloudWatch metrics under the `PULSE/Agent` namespace: `ExecutionDuration`, `ExecutionCount`, and `AgentInvocations`.

### The Frontend

I built a monitoring dashboard in React with Vite and Tailwind CSS, served through Amazon CloudFront backed by a private S3 bucket (via Origin Access Control, not public bucket hosting). The dashboard displays the latest brief, agent status, execution timeline, performance metrics, and AWS service health. It exists purely for observability — the agent does not require it to function.

### Challenges

The hardest part was not the AI. It was making the system genuinely autonomous end-to-end while keeping it deployable within Free Tier constraints. EventBridge Scheduler with a Lambda proxy into App Runner took some iteration to wire correctly — the Lambda needs to authenticate against the backend API, which means JWT handling inside the Lambda handler itself. I also had to be careful with IAM: the App Runner instance role needs scoped access to Bedrock, SES, Secrets Manager, S3, and CloudWatch without being overly broad.

## AWS Services Used / Architecture Overview

| Service | Role |
|---------|------|
| Amazon Bedrock | AI brief generation via Nova Micro (Converse API) |
| Amazon EventBridge Scheduler | Daily cron trigger at 7:00 AM — the autonomous entry point |
| AWS Lambda | Serverless execution bridge between EventBridge and the backend |
| AWS App Runner | Hosts the FastAPI backend container |
| Amazon CloudWatch | Structured logging, custom metrics (`PULSE/Agent` namespace), alarms |
| AWS Secrets Manager | Stores API keys and tokens (GitHub, weather, Telegram, Slack) |
| Amazon SES | Email delivery channel |
| Amazon S3 | Frontend hosting, brief archive storage |
| Amazon CloudFront | CDN with Origin Access Control for the React dashboard |
| Amazon ECR | Container image registry for the backend |
| AWS IAM | Least-privilege roles for Lambda, App Runner, and EventBridge |

The flow: EventBridge Scheduler fires daily, triggering a Lambda function. The Lambda authenticates against the App Runner backend and invokes the brief generation endpoint. The backend collects data, calls Bedrock, delivers through SES/Telegram/Slack, and logs metrics to CloudWatch. The entire infrastructure is defined in a CloudFormation template with parameterized configuration.

## What I Learned

**EventBridge Scheduler is the real enabler of autonomous agents.** Without it, you have an API. With it, you have an agent. The distinction is not about AI capability — it is about whether the system acts without being prompted. EventBridge's built-in retry policy (up to 3 attempts over an hour) also provides resilience I would have had to build manually otherwise.

**Bedrock's Converse API simplifies model interaction significantly.** I did not need to construct model-specific payloads or parse proprietary response formats. The unified interface meant I could test with Nova Micro and switch to Nova Pro later without changing application code.

**CloudWatch custom metrics are underrated for agent observability.** Being able to see execution duration trends, failure rates, and token consumption over time makes it straightforward to know whether the agent is healthy without checking logs manually.

**Designing for graceful degradation makes autonomous systems viable.** An agent that fails because one of six data sources is down is not autonomous — it is fragile. Building each collector with independent error handling and fallback data made the difference between a demo and something I actually rely on.

**Production deployment on Free Tier is achievable.** The combination of Lambda (30 invocations/month), Bedrock Nova Micro (minimal token cost), App Runner (scales to zero with pause), and S3+CloudFront delivers a production-grade deployment for under six dollars a month.

## Link to Repository and Deployment

- **GitHub Repository:** [https://github.com/reetika0104/AgentPulse](https://github.com/reetika0104/AgentPulse)
- **Live Dashboard:** [https://d2p1umgv2ynihx.cloudfront.net](https://d2p1umgv2ynihx.cloudfront.net)
- **Backend API:** [https://fvitseikim.us-east-1.awsapprunner.com/api/v1/health](https://fvitseikim.us-east-1.awsapprunner.com/api/v1/health)

---

PULSE is not a chatbot. It is not a tool you interact with. It is an autonomous agent that runs on a schedule, reasons about your day, and delivers actionable intelligence before you wake up. That is what "always-on" means.
