"""
PULSE AWS Secrets Manager Service
Securely retrieves secrets from AWS Secrets Manager.
"""

import json
import boto3
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("secrets_service")
settings = get_settings()


def get_secrets_client():
    """Get boto3 Secrets Manager client."""
    return boto3.client(
        "secretsmanager",
        region_name=settings.AWS_REGION,
    )


def get_secret(secret_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a secret from AWS Secrets Manager.
    
    Args:
        secret_name: Name of the secret (will be prefixed with settings.SECRETS_MANAGER_PREFIX)
    
    Returns:
        Parsed JSON secret or None if not found
    """
    full_name = f"{settings.SECRETS_MANAGER_PREFIX}{secret_name}"
    try:
        client = get_secrets_client()
        response = client.get_secret_value(SecretId=full_name)
        secret_string = response.get("SecretString")
        
        if secret_string:
            try:
                return json.loads(secret_string)
            except json.JSONDecodeError:
                return {"value": secret_string}

        return None

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ResourceNotFoundException":
            logger.warning(f"Secret not found: {full_name}")
        elif error_code == "AccessDeniedException":
            logger.error(f"Access denied to secret: {full_name}")
        else:
            logger.error(f"Error retrieving secret {full_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error retrieving secret: {e}")
        return None


def create_secret(secret_name: str, secret_value: Dict[str, Any]) -> bool:
    """
    Create or update a secret in AWS Secrets Manager.
    
    Args:
        secret_name: Name of the secret
        secret_value: Dictionary to store as JSON
    
    Returns:
        True if successful
    """
    full_name = f"{settings.SECRETS_MANAGER_PREFIX}{secret_name}"
    try:
        client = get_secrets_client()
        secret_string = json.dumps(secret_value)

        try:
            client.create_secret(
                Name=full_name,
                SecretString=secret_string,
                Description=f"PULSE Agent secret: {secret_name}",
            )
            logger.info(f"Secret created: {full_name}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceExistsException":
                client.update_secret(
                    SecretId=full_name,
                    SecretString=secret_string,
                )
                logger.info(f"Secret updated: {full_name}")
            else:
                raise

        return True

    except Exception as e:
        logger.error(f"Error creating secret {full_name}: {e}")
        return False
