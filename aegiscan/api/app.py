from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from httpx_oauth.clients.google import GoogleOAuth2
from pydantic import BaseModel
from pydantic_core import to_jsonable_python
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from aegiscan import config
from aegiscan.api.common import (
    bootstrap_role,
    custom_generate_unique_id,
    generic_exception_handler,
    aegiscan_exception_handler,
)
from aegiscan.auth.dependencies import require_auth_type_enabled
from aegiscan.auth.enums import AuthType
from aegiscan.auth.models import UserCreate, UserRead, UserUpdate
from aegiscan.auth.router import router as users_router
from aegiscan.auth.saml import router as saml_router
from aegiscan.auth.users import (
    FastAPIUsersException,
    InvalidDomainException,
    auth_backend,
    fastapi_users,
)
from aegiscan.contexts import ctx_role
from aegiscan.db.dependencies import AsyncDBSession
from aegiscan.db.engine import get_async_session_context_manager
from aegiscan.editor.router import router as editor_router
from aegiscan.logger import logger
from aegiscan.middleware import RequestLoggingMiddleware
from aegiscan.middleware.security import SecurityHeadersMiddleware
from aegiscan.organization.router import router as org_router
from aegiscan.registry.actions.router import router as registry_actions_router
from aegiscan.registry.common import reload_registry
from aegiscan.registry.repositories.router import router as registry_repos_router
from aegiscan.secrets.router import org_router as org_secrets_router
from aegiscan.secrets.router import router as secrets_router
from aegiscan.settings.router import router as org_settings_router
from aegiscan.settings.service import SettingsService, get_setting_override
from aegiscan.tables.router import router as tables_router
from aegiscan.tags.router import router as tags_router
from aegiscan.types.auth import Role
from aegiscan.types.exceptions import AegiscanException
from aegiscan.webhooks.router import router as webhook_router
from aegiscan.workflow.actions.router import router as workflow_actions_router
from aegiscan.workflow.executions.router import router as workflow_executions_router
from aegiscan.workflow.management.router import router as workflow_management_router
from aegiscan.workflow.schedules.router import router as schedules_router
from aegiscan.workflow.tags.router import router as workflow_tags_router
from aegiscan.workspaces.router import router as workspaces_router
from aegiscan.workspaces.service import WorkspaceService


@asynccontextmanager
async def lifespan(app: FastAPI):
    role = bootstrap_role()
    async with get_async_session_context_manager() as session:
        # Org
        await setup_org_settings(session, role)
        await reload_registry(session, role)
        await setup_workspace_defaults(session, role)
    yield


async def setup_org_settings(session: AsyncSession, admin_role: Role):
    settings_service = SettingsService(session, role=admin_role)
    await settings_service.init_default_settings()


async def setup_workspace_defaults(session: AsyncSession, admin_role: Role):
    ws_service = WorkspaceService(session, role=admin_role)
    workspaces = await ws_service.admin_list_workspaces()
    n_workspaces = len(workspaces)
    logger.info(f"{n_workspaces} workspaces found")
    if n_workspaces == 0:
        # Create default workspace if there are no workspaces
        try:
            default_workspace = await ws_service.create_workspace("Default Workspace")
            logger.info("Default workspace created", workspace=default_workspace)
        except IntegrityError:
            logger.info("Default workspace already exists, skipping")


# Catch-all exception handler to prevent stack traces from leaking
def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Improves visiblity of 422 errors."""
    errors = exc.errors()
    ser_errors = to_jsonable_python(errors, fallback=str)
    logger.error(
        "API Model Validation error",
        request=request,
        errors=ser_errors,
    )
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": ser_errors},
    )


def fastapi_users_auth_exception_handler(request: Request, exc: FastAPIUsersException):
    msg = str(exc)
    logger.warning(
        "Handling FastAPI Users exception",
        msg=msg,
        role=ctx_role.get(),
        params=request.query_params,
        path=request.url.path,
    )
    match exc:
        case InvalidDomainException():
            status_code = status.HTTP_400_BAD_REQUEST
        case _:
            status_code = status.HTTP_401_UNAUTHORIZED
    return ORJSONResponse(status_code=status_code, content={"detail": msg})


def create_app(**kwargs) -> FastAPI:
    if config.AEGISCAN__ALLOW_ORIGINS is not None:
        allow_origins = config.AEGISCAN__ALLOW_ORIGINS.split(",")
    else:
        allow_origins = ["*"]
    app = FastAPI(
        title="Aegiscan API",
        description=(
            "Aegiscan is the open source Tines / Splunk SOAR alternative."
            " You can operate Aegiscan in headless mode by using the API to create, manage, and run workflows."
        ),
        summary="Aegiscan API",
        version="1",
        terms_of_service="https://docs.google.com/document/d/e/2PACX-1vQvDe3SoVAPoQc51MgfGCP71IqFYX_rMVEde8zC4qmBCec5f8PLKQRdxa6tsUABT8gWAR9J-EVs2CrQ/pub",
        contact={"name": "Aegiscan Founders", "email": "founders@digi-trans.org"},
        license_info={
            "name": "AGPL-3.0",
            "url": "https://www.gnu.org/licenses/agpl-3.0.html",
        },
        openapi_tags=[
            {"name": "public", "description": "Public facing endpoints"},
            {"name": "workflows", "description": "Workflow management"},
            {"name": "actions", "description": "Action management"},
            {"name": "triggers", "description": "Workflow triggers"},
            {"name": "secrets", "description": "Secret management"},
        ],
        generate_unique_id_function=custom_generate_unique_id,
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        root_path=config.AEGISCAN__API_ROOT_PATH,
        **kwargs,
    )
    app.logger = logger  # type: ignore

    # Routers
    app.include_router(webhook_router)
    app.include_router(workspaces_router)
    app.include_router(workflow_management_router)
    app.include_router(workflow_executions_router)
    app.include_router(workflow_actions_router)
    app.include_router(workflow_tags_router)
    app.include_router(secrets_router)
    app.include_router(schedules_router)
    app.include_router(tags_router)
    app.include_router(users_router)
    app.include_router(org_router)
    app.include_router(editor_router)
    app.include_router(registry_repos_router)
    app.include_router(registry_actions_router)
    app.include_router(org_settings_router)
    app.include_router(org_secrets_router)
    app.include_router(tables_router)
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )

    if AuthType.BASIC in config.AEGISCAN__AUTH_TYPES:
        app.include_router(
            fastapi_users.get_auth_router(auth_backend),
            prefix="/auth",
            tags=["auth"],
        )
        app.include_router(
            fastapi_users.get_register_router(UserRead, UserCreate),
            prefix="/auth",
            tags=["auth"],
        )
        app.include_router(
            fastapi_users.get_reset_password_router(),
            prefix="/auth",
            tags=["auth"],
        )
        app.include_router(
            fastapi_users.get_verify_router(UserRead),
            prefix="/auth",
            tags=["auth"],
        )

    oauth_client = GoogleOAuth2(
        client_id=config.OAUTH_CLIENT_ID, client_secret=config.OAUTH_CLIENT_SECRET
    )
    # This is the frontend URL that the user will be redirected to after authenticating
    redirect_url = f"{config.AEGISCAN__PUBLIC_APP_URL}/auth/oauth/callback"
    logger.info("OAuth redirect URL", url=redirect_url)
    app.include_router(
        fastapi_users.get_oauth_router(
            oauth_client,
            auth_backend,
            config.USER_AUTH_SECRET,
            # XXX(security): See https://fastapi-users.github.io/fastapi-users/13.0/configuration/oauth/#existing-account-association
            associate_by_email=True,
            is_verified_by_default=True,
            # Points the user back to the login page
            redirect_url=redirect_url,
        ),
        prefix="/auth/oauth",
        tags=["auth"],
        dependencies=[require_auth_type_enabled(AuthType.GOOGLE_OAUTH)],
    )
    app.include_router(
        saml_router,
        dependencies=[require_auth_type_enabled(AuthType.SAML)],
    )

    if AuthType.BASIC not in config.AEGISCAN__AUTH_TYPES:
        # Need basic auth router for `logout` endpoint
        app.include_router(
            fastapi_users.get_logout_router(auth_backend),
            prefix="/auth",
            tags=["auth"],
        )

    # Exception handlers
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(AegiscanException, aegiscan_exception_handler)  # type: ignore  # type: ignore
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(
        FastAPIUsersException,
        fastapi_users_auth_exception_handler,  # type: ignore
    )

    # Middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info(
        "App started",
        env=config.AEGISCAN__APP_ENV,
        origins=allow_origins,
        auth_types=config.AEGISCAN__AUTH_TYPES,
    )
    return app


app = create_app()


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "Hello world. I am the API."}


class AppInfo(BaseModel):
    public_app_url: str
    auth_allowed_types: list[AuthType]
    auth_basic_enabled: bool
    oauth_google_enabled: bool
    saml_enabled: bool


@app.get("/info", include_in_schema=False)
async def info(session: AsyncDBSession) -> AppInfo:
    """Non-sensitive information about the platform, for frontend configuration."""

    keys = {"auth_basic_enabled", "oauth_google_enabled", "saml_enabled"}

    service = SettingsService(session, role=bootstrap_role())
    settings = await service.list_org_settings(keys=keys)
    keyvalues = {s.key: service.get_value(s) for s in settings}
    for key in keys:
        keyvalues[key] = get_setting_override(key) or keyvalues[key]
    return AppInfo(
        public_app_url=config.AEGISCAN__PUBLIC_APP_URL,
        auth_allowed_types=list(config.AEGISCAN__AUTH_TYPES),
        auth_basic_enabled=keyvalues["auth_basic_enabled"],
        oauth_google_enabled=keyvalues["oauth_google_enabled"],
        saml_enabled=keyvalues["saml_enabled"],
    )


@app.get("/health", tags=["public"])
def check_health() -> dict[str, str]:
    return {"message": "Hello world. I am the API. This is the health endpoint."}
