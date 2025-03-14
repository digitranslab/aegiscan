"""
How to test:

1. Create a temporary directory with a python package in it.
2. Add this as a local repository
3. Load the package
4. Run an action
5. Check that the action ran successfully
6. Make an edit to the package
7. Run the action again
8. Check that the action ran successfully
"""

from pathlib import Path
from textwrap import dedent

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from aegiscan import config
from aegiscan.registry.constants import DEFAULT_LOCAL_REGISTRY_ORIGIN
from aegiscan.registry.repositories.models import RegistryRepositoryCreate
from aegiscan.registry.repositories.service import RegistryReposService
from aegiscan.registry.repository import Repository
from aegiscan.types.auth import Role

pytestmark = pytest.mark.usefixtures("db")


@pytest.fixture
def sample_package_content() -> str:
    """Sample package content with a basic UDF."""
    return dedent(
        """
        from aegiscan_registry import registry

        @registry.register(
            default_title="Add two numbers",
            namespace="test",
            description="A test action that adds two numbers",
        )
        def add_numbers(a: int, b: int) -> int:
            return a + b
        """
    )


@pytest.fixture
async def local_package_path(tmp_path: Path, sample_package_content: str) -> Path:
    """Create a temporary package directory with a sample UDF."""
    package_dir = tmp_path / "test_package"
    package_dir.mkdir()

    # Create test_actions as a proper Python package
    test_actions_dir = package_dir / "test_actions"
    test_actions_dir.mkdir()

    # Create package files
    init_file = test_actions_dir / "__init__.py"
    init_file.write_text("")

    actions_file = test_actions_dir / "actions.py"
    actions_file.write_text(sample_package_content)

    return package_dir


@pytest.mark.anyio
async def test_local_registry(
    svc_role: Role,
    local_package_path: Path,
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test loading and running actions from a local registry."""
    # Add the parent directory to Python path so test_actions can be imported
    monkeypatch.syspath_prepend(str(local_package_path))

    # The rest of your test remains the same
    monkeypatch.setattr(config, "AEGISCAN__LOCAL_REPOSITORY_ENABLED", True)
    monkeypatch.setattr(
        config,
        "AEGISCAN__LOCAL_REPOSITORY_CONTAINER_PATH",
        str(local_package_path),
    )

    # Create repository service and add local repository
    repo_service = RegistryReposService(session, role=svc_role)
    await repo_service.create_repository(
        RegistryRepositoryCreate(origin=DEFAULT_LOCAL_REGISTRY_ORIGIN)
    )

    # Initialize repository
    repository = Repository(origin=DEFAULT_LOCAL_REGISTRY_ORIGIN, role=svc_role)

    repo_path = Path(config.AEGISCAN__LOCAL_REPOSITORY_CONTAINER_PATH)

    assert repo_path.exists()

    await repository._load_repository(repo_path.as_posix(), "test_actions")

    # Verify the action was loaded
    assert "test.add_numbers" in repository

    # Run the action
    action = repository["test.add_numbers"]
    result = action.fn(1, 2)
    assert result == 3

    # Modify the action
    actions_file = local_package_path / "test_actions" / "actions.py"
    actions_file.write_text(
        dedent(
            """
            from aegiscan_registry import registry

            @registry.register(
                default_title="Add two numbers and adds 1",
                namespace="test",
                description="A test action that adds two numbers and adds 1",
            )
            def add_numbers(a: int, b: int) -> int:
                return a + b + 1
            """
        )
    )

    # Reload and verify changes
    await repository._load_repository(repo_path.as_posix(), "test_actions")
    action = repository["test.add_numbers"]
    result = action.fn(1, 2)
    assert result == 4


@pytest.mark.anyio
async def test_local_registry_invalid_package(
    svc_role: Role,
    tmp_path: Path,
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test handling of invalid local package."""
    invalid_path = tmp_path / "nonexistent_package"
    monkeypatch.setenv("AEGISCAN__LOCAL_REPOSITORY_CONTAINER_PATH", str(invalid_path))

    repo_service = RegistryReposService(session, role=svc_role)
    await repo_service.create_repository(
        RegistryRepositoryCreate(origin=DEFAULT_LOCAL_REGISTRY_ORIGIN)
    )

    repository = Repository(origin=DEFAULT_LOCAL_REGISTRY_ORIGIN, role=svc_role)

    with pytest.raises(
        Exception,
        match="Local repository is not enabled on this instance."
        " Please set AEGISCAN__LOCAL_REPOSITORY_ENABLED=true and ensure"
        " AEGISCAN__LOCAL_REPOSITORY_PATH points to a valid Python package.",
    ):
        await repository.load_from_origin()
