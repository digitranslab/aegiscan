"""Aegiscan HTTP clients."""

import os
from typing import Any

import httpx

from aegiscan import config
from aegiscan.contexts import ctx_role
from aegiscan.types.auth import Role
from aegiscan.types.exceptions import AegiscanCredentialsError


class AuthenticatedServiceClient(httpx.AsyncClient):
    """An authenticated service client. Typically used by internal services.

    Role precedence
    ---------------
    1. Role passed to the client
    2. Role set in the session role context
    3. Default role Role(type="service", service_id="aegiscan-service")
    """

    def __init__(self, role: Role | None = None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        # Precedence: role > ctx_role > default role. Role is always set.
        # NOTE: Actually should we throw if no role?
        self.role = role or ctx_role.get(
            Role(type="service", service_id="aegiscan-service")
        )
        try:
            self.headers["x-aegiscan-service-key"] = os.environ["AEGISCAN__SERVICE_KEY"]
        except KeyError as e:
            raise AegiscanCredentialsError(
                "AEGISCAN__SERVICE_KEY environment variable not set"
            ) from e
        self.headers.update(self.role.to_headers())


class AuthenticatedAPIClient(AuthenticatedServiceClient):
    """An authenticated httpx client to hit main API endpoints.

     Role precedence
    ---------------
    1. Role passed to the client
    2. Role set in the session role context
    3. Default role Role(type="service", service_id="aegiscan-service")
    """

    def __init__(self, role: Role | None = None, *args: Any, **kwargs: Any):
        kwargs["role"] = role
        kwargs["base_url"] = config.AEGISCAN__API_URL
        super().__init__(*args, **kwargs)
