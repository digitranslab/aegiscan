from fastapi import Request, status
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute

from aegiscan import config
from aegiscan.contexts import ctx_role
from aegiscan.logger import logger
from aegiscan.types.auth import AccessLevel, Role
from aegiscan.types.exceptions import AegiscanException


def generic_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unexpected error",
        exc=exc,
        role=ctx_role.get(),
        params=request.query_params,
        path=request.url.path,
    )
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred. Please try again later."},
    )


def bootstrap_role():
    """Role to bootstrap Aegiscan services."""
    return Role(
        type="service",
        access_level=AccessLevel.ADMIN,
        service_id="aegiscan-bootstrap",
    )


def aegiscan_exception_handler(request: Request, exc: AegiscanException):
    """Generic exception handler for Aegiscan exceptions.

    We can customize exceptions to expose only what should be user facing.
    """
    msg = str(exc)
    logger.error(
        msg,
        role=ctx_role.get(),
        params=request.query_params,
        path=request.url.path,
        detail=exc.detail,
    )
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"type": type(exc).__name__, "message": msg, "detail": exc.detail},
    )


def custom_generate_unique_id(route: APIRoute):
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


async def setup_oss_models():
    if not (preload_models := config.AEGISCAN__PRELOAD_OSS_MODELS):
        return
    from aegiscan.llm import preload_ollama_models

    logger.info(
        f"Preloading {len(preload_models)} models",
        models=preload_models,
    )
    await preload_ollama_models(preload_models)
    logger.info("Preloaded models", models=preload_models)
