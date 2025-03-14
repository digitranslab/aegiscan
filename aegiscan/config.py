import os
import uuid
from typing import Literal

from aegiscan.auth.enums import AuthType

# === Internal Services === #
AEGISCAN__APP_ENV: Literal["development", "staging", "production"] = os.environ.get(
    "AEGISCAN__APP_ENV", "development"
)  # type: ignore
AEGISCAN__API_URL = os.environ.get("AEGISCAN__API_URL", "http://localhost:8000")
AEGISCAN__API_ROOT_PATH = os.environ.get("AEGISCAN__API_ROOT_PATH", "/api")
AEGISCAN__PUBLIC_API_URL = os.environ.get(
    "AEGISCAN__PUBLIC_API_URL", "http://localhost/api"
)
AEGISCAN__PUBLIC_APP_URL = os.environ.get(
    "AEGISCAN__PUBLIC_APP_URL", "http://localhost"
)

AEGISCAN__DB_URI = os.environ.get(
    "AEGISCAN__DB_URI",
    "postgresql+psycopg://postgres:postgres@postgres_db:5432/postgres",
)
AEGISCAN__EXECUTOR_URL = os.environ.get(
    "AEGISCAN__EXECUTOR_URL", "http://executor:8000"
)
AEGISCAN__EXECUTOR_CLIENT_TIMEOUT = float(
    os.environ.get("AEGISCAN__EXECUTOR_CLIENT_TIMEOUT", 120.0)
)
"""Timeout for the executor client in seconds (default 120s).

The `httpx.Client` default is 5s, which doesn't work for long-running actions.
"""
AEGISCAN__LOOP_MAX_BATCH_SIZE = int(os.environ.get("AEGISCAN__LOOP_MAX_BATCH_SIZE", 64))
"""Maximum number of parallel requests to the worker service."""

AEGISCAN__DB_NAME = os.environ.get("AEGISCAN__DB_NAME")
AEGISCAN__DB_USER = os.environ.get("AEGISCAN__DB_USER")
AEGISCAN__DB_PASS = os.environ.get("AEGISCAN__DB_PASS")
AEGISCAN__DB_PASS__ARN = os.environ.get("AEGISCAN__DB_PASS__ARN")
AEGISCAN__DB_ENDPOINT = os.environ.get("AEGISCAN__DB_ENDPOINT")
AEGISCAN__DB_PORT = os.environ.get("AEGISCAN__DB_PORT")

# TODO: Set this as an environment variable
AEGISCAN__SERVICE_ROLES_WHITELIST = [
    "aegiscan-runner",
    "aegiscan-api",
    "aegiscan-cli",
    "aegiscan-schedule-runner",
]
AEGISCAN__DEFAULT_USER_ID = uuid.UUID(int=0)
AEGISCAN__DEFAULT_ORG_ID = uuid.UUID(int=0)

# === DB Config === #
AEGISCAN__DB_URI = os.environ.get(
    "AEGISCAN__DB_URI",
    "postgresql+psycopg://postgres:postgres@postgres_db:5432/postgres",
)
AEGISCAN__DB_NAME = os.environ.get("AEGISCAN__DB_NAME")
AEGISCAN__DB_USER = os.environ.get("AEGISCAN__DB_USER")
AEGISCAN__DB_PASS = os.environ.get("AEGISCAN__DB_PASS")
AEGISCAN__DB_ENDPOINT = os.environ.get("AEGISCAN__DB_ENDPOINT")
AEGISCAN__DB_PORT = os.environ.get("AEGISCAN__DB_PORT")

# === Auth config === #
# Infrastructure config
AEGISCAN__AUTH_TYPES = {
    AuthType(t.lower())
    for t in os.environ.get("AEGISCAN__AUTH_TYPES", "basic,google_oauth").split(",")
}
"""The set of allowed auth types on the platform. If an auth type is not in this set,
it cannot be enabled."""

AEGISCAN__AUTH_REQUIRE_EMAIL_VERIFICATION = os.environ.get(
    "AEGISCAN__AUTH_REQUIRE_EMAIL_VERIFICATION", ""
).lower() in ("true", "1")  # Default to False
SESSION_EXPIRE_TIME_SECONDS = int(
    os.environ.get("SESSION_EXPIRE_TIME_SECONDS") or 86400 * 7
)  # 7 days
AEGISCAN__AUTH_ALLOWED_DOMAINS = set(
    ((domains := os.getenv("AEGISCAN__AUTH_ALLOWED_DOMAINS")) and domains.split(","))
    or []
)
"""Deprecated: This config has been moved into the settings service"""

AEGISCAN__AUTH_MIN_PASSWORD_LENGTH = int(
    os.environ.get("AEGISCAN__AUTH_MIN_PASSWORD_LENGTH") or 12
)


# OAuth Login Flow
# Used for both Google OAuth2 and OIDC flows
OAUTH_CLIENT_ID = (
    os.environ.get("OAUTH_CLIENT_ID") or os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or ""
)
OAUTH_CLIENT_SECRET = (
    os.environ.get("OAUTH_CLIENT_SECRET")
    or os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    or ""
)
USER_AUTH_SECRET = os.environ.get("USER_AUTH_SECRET", "")

# SAML SSO

SAML_PUBLIC_ACS_URL = f"{AEGISCAN__PUBLIC_APP_URL}/auth/saml/acs"

SAML_IDP_METADATA_URL = os.environ.get("SAML_IDP_METADATA_URL")
"""Deprecated: This config has been moved into the settings service"""

XMLSEC_BINARY_PATH = os.environ.get("XMLSEC_BINARY_PATH", "/usr/bin/xmlsec1")

# === CORS config === #
# NOTE: If you are using Aegiscan self-hosted, please replace with your
# own domain by setting the comma separated AEGISCAN__ALLOW_ORIGINS env var.
AEGISCAN__ALLOW_ORIGINS = os.environ.get("AEGISCAN__ALLOW_ORIGINS")

# === Temporal config === #
TEMPORAL__CONNECT_RETRIES = int(os.environ.get("TEMPORAL__CONNECT_RETRIES", 10))
TEMPORAL__CLUSTER_URL = os.environ.get(
    "TEMPORAL__CLUSTER_URL", "http://localhost:7233"
)  # AKA TEMPORAL_HOST_URL
TEMPORAL__CLUSTER_NAMESPACE = os.environ.get(
    "TEMPORAL__CLUSTER_NAMESPACE", "default"
)  # AKA TEMPORAL_NAMESPACE
TEMPORAL__CLUSTER_QUEUE = os.environ.get(
    "TEMPORAL__CLUSTER_QUEUE", "aegiscan-task-queue"
)
TEMPORAL__API_KEY__ARN = os.environ.get("TEMPORAL__API_KEY__ARN")
TEMPORAL__API_KEY = os.environ.get("TEMPORAL__API_KEY")
TEMPORAL__MTLS_ENABLED = os.environ.get("TEMPORAL__MTLS_ENABLED", "").lower() in (
    "1",
    "true",
)
TEMPORAL__MTLS_CERT__ARN = os.environ.get("TEMPORAL__MTLS_CERT__ARN")
TEMPORAL__CLIENT_RPC_TIMEOUT = os.environ.get("TEMPORAL__CLIENT_RPC_TIMEOUT")
"""RPC timeout for Temporal workflows in seconds."""

TEMPORAL__TASK_TIMEOUT = os.environ.get("TEMPORAL__TASK_TIMEOUT")
"""Temporal workflow task timeout in seconds (default 10 seconds)."""

# Secrets manager config
AEGISCAN__UNSAFE_DISABLE_SM_MASKING = os.environ.get(
    "AEGISCAN__UNSAFE_DISABLE_SM_MASKING",
    "0",  # Default to False
).lower() in ("1", "true")
"""Disable masking of secrets in the secrets manager.
    WARNING: This is only be used for testing and debugging purposes during
    development and should never be enabled in production.
"""

# === M2M config === #
AEGISCAN__SERVICE_KEY = os.environ.get("AEGISCAN__SERVICE_KEY")

# === Remote registry === #
AEGISCAN__ALLOWED_GIT_DOMAINS = set(
    os.environ.get(
        "AEGISCAN__ALLOWED_GIT_DOMAINS", "github.com,gitlab.com,bitbucket.org"
    ).split(",")
)
"""Deprecated: This config has been moved into the settings service"""
# If you wish to use a remote registry, set the URL here
# If the url is unset, this will be set to None
AEGISCAN__REMOTE_REPOSITORY_URL = (
    os.environ.get("AEGISCAN__REMOTE_REPOSITORY_URL") or None
)
"""Deprecated: This config has been moved into the settings service"""
AEGISCAN__REMOTE_REPOSITORY_PACKAGE_NAME = os.getenv(
    "AEGISCAN__REMOTE_REPOSITORY_PACKAGE_NAME"
)
"""If not provided, the package name will be inferred from the git remote URL.

Deprecated: This config has been moved into the settings service
"""

# === Email settings === #
AEGISCAN__ALLOWED_EMAIL_ATTRIBUTES = os.environ.get(
    "AEGISCAN__ALLOWED_EMAIL_ATTRIBUTES"
)
# === AI settings === #
AEGISCAN__PRELOAD_OSS_MODELS = (
    (models := os.getenv("AEGISCAN__PRELOAD_OSS_MODELS")) and models.split(",")
) or []

OLLAMA__API_URL = os.environ.get("OLLAMA__API_URL", "http://ollama:11434")

# === Local registry === #
AEGISCAN__LOCAL_REPOSITORY_ENABLED = os.getenv(
    "AEGISCAN__LOCAL_REPOSITORY_ENABLED", "0"
).lower() in ("1", "true")
AEGISCAN__LOCAL_REPOSITORY_PATH = os.getenv("AEGISCAN__LOCAL_REPOSITORY_PATH")
AEGISCAN__LOCAL_REPOSITORY_CONTAINER_PATH = "/app/local_registry"

# === Rate Limiting === #
AEGISCAN__RATE_LIMIT_ENABLED = (
    os.environ.get("AEGISCAN__RATE_LIMIT_ENABLED", "true").lower() == "true"
)
"""Whether rate limiting is enabled for the executor service."""

AEGISCAN__RATE_LIMIT_RATE = float(os.environ.get("AEGISCAN__RATE_LIMIT_RATE", 40.0))
"""The rate at which tokens are added to the bucket (tokens per second)."""

AEGISCAN__RATE_LIMIT_CAPACITY = float(
    os.environ.get("AEGISCAN__RATE_LIMIT_CAPACITY", 80.0)
)
"""The maximum number of tokens the bucket can hold."""

AEGISCAN__RATE_LIMIT_WINDOW_SIZE = int(
    os.environ.get("AEGISCAN__RATE_LIMIT_WINDOW_SIZE", 60)
)
"""The time window in seconds for rate limiting."""

AEGISCAN__RATE_LIMIT_BY_IP = (
    os.environ.get("AEGISCAN__RATE_LIMIT_BY_IP", "true").lower() == "true"
)
"""Whether to rate limit by client IP."""

AEGISCAN__RATE_LIMIT_BY_ENDPOINT = (
    os.environ.get("AEGISCAN__RATE_LIMIT_BY_ENDPOINT", "true").lower() == "true"
)
"""Whether to rate limit by endpoint."""
