from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from aegiscan import config
from aegiscan.api.common import (
    custom_generate_unique_id,
    generic_exception_handler,
    setup_oss_models,
    aegiscan_exception_handler,
)
from aegiscan.executor.engine import setup_ray
from aegiscan.executor.router import router as executor_router
from aegiscan.logger import logger
from aegiscan.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from aegiscan.types.exceptions import AegiscanException


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await setup_oss_models()
    except Exception as e:
        logger.error("Failed to preload OSS models", error=e)
    with setup_ray():
        yield


def create_app(**kwargs) -> FastAPI:
    if config.AEGISCAN__ALLOW_ORIGINS is not None:
        allow_origins = config.AEGISCAN__ALLOW_ORIGINS.split(",")
    else:
        allow_origins = ["*"]
    app = FastAPI(
        title="Aegiscan Executor",
        description="Action executor for Aegiscan.",
        summary="Aegiscan Executor",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        generate_unique_id_function=custom_generate_unique_id,
        root_path="/api/executor",
        **kwargs,
    )
    app.logger = logger  # type: ignore

    # Routers
    app.include_router(executor_router)

    # Exception handlers
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(AegiscanException, aegiscan_exception_handler)  # type: ignore

    # Middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Add rate limiting middleware if enabled
    if config.AEGISCAN__RATE_LIMIT_ENABLED:
        logger.info(
            "Adding rate limiting middleware",
            rate=config.AEGISCAN__RATE_LIMIT_RATE,
            capacity=config.AEGISCAN__RATE_LIMIT_CAPACITY,
            window_size=config.AEGISCAN__RATE_LIMIT_WINDOW_SIZE,
            by_ip=config.AEGISCAN__RATE_LIMIT_BY_IP,
            by_endpoint=config.AEGISCAN__RATE_LIMIT_BY_ENDPOINT,
        )
        app.add_middleware(
            RateLimitMiddleware,
            rate=config.AEGISCAN__RATE_LIMIT_RATE,
            capacity=config.AEGISCAN__RATE_LIMIT_CAPACITY,
            window_size=config.AEGISCAN__RATE_LIMIT_WINDOW_SIZE,
            by_ip=config.AEGISCAN__RATE_LIMIT_BY_IP,
            by_endpoint=config.AEGISCAN__RATE_LIMIT_BY_ENDPOINT,
        )

    app.add_middleware(
        CORSMiddleware,
        # XXX(security): We should be more restrictive here
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info(
        "Executor service started",
        env=config.AEGISCAN__APP_ENV,
        origins=allow_origins,
        rate_limiting=config.AEGISCAN__RATE_LIMIT_ENABLED,
    )

    return app


app = create_app()


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "Hello world. I am the executor."}
