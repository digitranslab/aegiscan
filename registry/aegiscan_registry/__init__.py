"""Aegiscan managed actions and integrations registry."""

__version__ = "0.1.0"


try:
    import aegiscan  # noqa: F401
except ImportError:
    raise ImportError(
        "Could not import aegiscan. Please install `aegiscan` to use the registry."
    ) from None

from aegiscan_registry._internal import exceptions, registry, secrets
from aegiscan_registry._internal.exceptions import (
    ActionIsInterfaceError,
    RegistryActionError,
)
from aegiscan_registry._internal.logger import logger
from aegiscan_registry._internal.models import RegistrySecret

__all__ = [
    "registry",
    "RegistrySecret",
    "logger",
    "secrets",
    "exceptions",
    "RegistryActionError",
    "ActionIsInterfaceError",
]
