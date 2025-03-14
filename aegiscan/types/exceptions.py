"""Aegiscan exceptions

Note
----
This module contains exceptions that are user-facing, meaning they are
meant to be displayed to the user in a user-friendly way. We expose these
through FastAPI exception handlers, which match the exception type.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx
from pydantic_core import ValidationError

if TYPE_CHECKING:
    from aegiscan.executor.models import ExecutorActionErrorInfo
    from aegiscan.registry.actions.models import RegistryActionValidationErrorInfo


class AegiscanException(Exception):
    """Aegiscan generic user-facing exception"""

    def __init__(self, *args, detail: Any | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.detail = detail


class AegiscanValidationError(AegiscanException):
    """Aegiscan user-facing validation error"""


class AegiscanDSLError(AegiscanValidationError):
    """Aegiscan user-facing DSL error"""


class AegiscanExpressionError(AegiscanException):
    """Aegiscan user-facing expression error"""


class AegiscanCredentialsError(AegiscanException):
    """Aegiscan user-facing credentials error"""


class AegiscanAuthorizationError(AegiscanException):
    """Aegiscan user-facing authorization error"""


class AegiscanManagementError(AegiscanException):
    """Aegiscan user-facing management error"""


class AegiscanNotFoundError(AegiscanException):
    """Raised when a resource is not found in the Aegiscan database."""


class AegiscanServiceError(AegiscanException):
    """Aegiscan generic user-facing service error"""


class RegistryError(AegiscanException):
    """Generic exception raised when a registry error occurs."""


class RegistryActionError(RegistryError):
    """Exception raised when a registry action error occurs."""


class RegistryActionValidationError(AegiscanException):
    """Exception raised when a registry action validation error occurs."""

    def __init__(
        self,
        *args,
        detail: dict[str, list[RegistryActionValidationErrorInfo]],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.detail = detail


class RegistryValidationError(RegistryError):
    """Exception raised when a registry validation error occurs."""

    def __init__(
        self, *args, key: str | None = None, err: ValidationError | str | None = None
    ):
        super().__init__(*args)
        self.key = key
        self.err = err

    def __reduce__(self):
        return (self.__class__, (self.key, self.err))


class RegistryNotFound(RegistryError):
    """Exception raised when a registry is not found."""


class TaskUnreachable(AegiscanException):
    """Raised when a task is unreachable."""


class ExecutorClientError(AegiscanException):
    """Exception raised when an error occurs in the executor client."""


class ExecutionError(AegiscanException):
    """Exception raised when an error occurs during action execution.
    Use this to wrap errors from the executor so that we should reraise"""

    def __init__(self, info: ExecutorActionErrorInfo):
        self.info = info


class LoopExecutionError(AegiscanException):
    """Exception raised when an error occurs during loop execution."""

    def __init__(self, loop_errors: list[ExecutionError]):
        self.loop_errors = loop_errors


class AegiscanSettingsError(AegiscanException):
    """Exception raised when a setting error occurs."""


class AegiscanImportError(AegiscanException):
    """Exception raised when an import error occurs."""


class RateLimitExceeded(ExecutorClientError):
    """Exception raised when a request is rejected due to rate limiting."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        detail: Any = None,
        retry_after: int | None = None,
    ):
        """
        Initialize a rate limit exceeded error.

        Args:
            message: The error message
            detail: Additional error details
            retry_after: Suggested time in seconds to wait before retrying (if provided by the server)
        """
        super().__init__(message, detail)
        self.retry_after = retry_after

    @classmethod
    def from_response(
        cls, response: httpx.Response, detail: Any = None
    ) -> RateLimitExceeded:
        """
        Create a RateLimitExceededError from an HTTP response.

        Args:
            response: The HTTP response object
            detail: Additional error details

        Returns:
            A RateLimitExceededError instance
        """
        retry_after = None
        if "Retry-After" in response.headers:
            try:
                retry_after = int(response.headers["Retry-After"])
            except (ValueError, TypeError):
                pass

        message = "Rate limit exceeded. Please try again later."
        if retry_after:
            message += f" Server suggests waiting {retry_after} seconds."

        return cls(message, detail, retry_after)
