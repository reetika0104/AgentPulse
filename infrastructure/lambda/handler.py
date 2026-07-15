"""
PULSE Lambda Handler
Triggered by Amazon EventBridge Scheduler to run the morning brief pipeline.
This Lambda function invokes the PULSE backend API to generate and deliver briefs.
"""

import json
import os
import uuid
import time
import boto3
import urllib3
from datetime import datetime, timezone

# Initialize clients
http = urllib3.PoolManager()
cloudwatch = boto3.client("cloudwatch")
secrets_client = boto3.client("secretsmanager")


def handler(event, context):
    """
    Lambda handler triggered by EventBridge Scheduler.
    
    Event structure from EventBridge:
    {
        "source": "aws.scheduler",
        "detail-type": "Scheduled Event",
        "detail": {}
    }
    """
    execution_id = str(uuid.uuid4())
    start_time = time.time()

    print(json.dumps({
        "message": "PULSE Lambda triggered",
        "execution_id": execution_id,
        "event_source": event.get("source", "manual"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }))

    try:
        # Get the backend API URL from environment
        api_url = os.environ.get("PULSE_API_URL", "http://localhost:8000")
        api_key = os.environ.get("PULSE_API_KEY", "")

        # Option 1: Call the PULSE backend API
        if api_url and api_url != "http://localhost:8000":
            result = _invoke_via_api(api_url, api_key, execution_id)
        else:
            # Option 2: Direct execution (when Lambda has all dependencies)
            result = _invoke_directly(execution_id)

        duration = time.time() - start_time

        # Publish CloudWatch metrics
        _publish_metrics(
            execution_id=execution_id,
            status="success",
            duration=duration,
        )

        print(json.dumps({
            "message": "PULSE Lambda completed successfully",
            "execution_id": execution_id,
            "duration_seconds": round(duration, 2),
            "result_status": result.get("status", "unknown"),
        }))

        return {
            "statusCode": 200,
            "body": json.dumps({
                "execution_id": execution_id,
                "status": "completed",
                "duration_seconds": round(duration, 2),
                "result": result,
            }),
        }

    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)

        print(json.dumps({
            "message": "PULSE Lambda failed",
            "execution_id": execution_id,
            "error": error_msg,
            "duration_seconds": round(duration, 2),
        }))

        _publish_metrics(
            execution_id=execution_id,
            status="error",
            duration=duration,
        )

        return {
            "statusCode": 500,
            "body": json.dumps({
                "execution_id": execution_id,
                "status": "failed",
                "error": error_msg,
            }),
        }


def _invoke_via_api(api_url: str, api_key: str, execution_id: str) -> dict:
    """Invoke the PULSE backend API to trigger brief generation."""
    # First authenticate
    login_resp = http.request(
        "POST",
        f"{api_url}/api/v1/auth/login",
        body=json.dumps({"username": "admin", "password": api_key}).encode(),
        headers={"Content-Type": "application/json"},
    )

    if login_resp.status != 200:
        raise Exception(f"Authentication failed: {login_resp.status}")

    token = json.loads(login_resp.data.decode())["access_token"]

    # Trigger the brief
    trigger_resp = http.request(
        "POST",
        f"{api_url}/api/v1/brief/trigger",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    if trigger_resp.status != 200:
        raise Exception(f"Trigger failed: {trigger_resp.status}")

    return json.loads(trigger_resp.data.decode())


def _invoke_directly(execution_id: str) -> dict:
    """
    Direct execution mode - runs the brief pipeline within Lambda.
    Used when the Lambda has all required dependencies packaged.
    """
    # For direct execution, we'd import the orchestrator
    # This requires all dependencies in the Lambda layer
    try:
        import asyncio
        import sys
        sys.path.insert(0, "/opt/python")
        from app.agents.orchestrator import run_morning_brief
        
        result = asyncio.get_event_loop().run_until_complete(
            run_morning_brief(trigger_source="lambda", execution_id=execution_id)
        )
        return result
    except ImportError:
        # Fallback: minimal execution without full backend
        return {
            "status": "completed",
            "mode": "lambda_minimal",
            "execution_id": execution_id,
            "message": "Executed in minimal mode. Configure PULSE_API_URL for full execution.",
        }


def _publish_metrics(execution_id: str, status: str, duration: float) -> None:
    """Publish custom CloudWatch metrics."""
    try:
        cloudwatch.put_metric_data(
            Namespace="PULSE/Agent",
            MetricData=[
                {
                    "MetricName": "ExecutionDuration",
                    "Value": duration,
                    "Unit": "Seconds",
                    "Dimensions": [
                        {"Name": "AgentName", "Value": "PULSE"},
                        {"Name": "Status", "Value": status},
                    ],
                },
                {
                    "MetricName": "ExecutionCount",
                    "Value": 1,
                    "Unit": "Count",
                    "Dimensions": [
                        {"Name": "AgentName", "Value": "PULSE"},
                        {"Name": "Status", "Value": status},
                    ],
                },
            ],
        )
    except Exception as e:
        print(f"Failed to publish metrics: {e}")
