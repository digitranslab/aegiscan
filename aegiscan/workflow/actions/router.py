import yaml
from fastapi import APIRouter, HTTPException, status
from pydantic_core import PydanticUndefined
from sqlalchemy.exc import NoResultFound
from sqlmodel import select

from aegiscan.auth.dependencies import WorkspaceUserRole
from aegiscan.db.dependencies import AsyncDBSession
from aegiscan.db.schemas import Action
from aegiscan.identifiers.action import ActionID
from aegiscan.identifiers.workflow import AnyWorkflowIDPath, WorkflowUUID
from aegiscan.registry.actions.service import RegistryActionsService
from aegiscan.workflow.actions.models import (
    ActionControlFlow,
    ActionCreate,
    ActionRead,
    ActionReadMinimal,
    ActionUpdate,
)

router = APIRouter(prefix="/actions")


@router.get("", tags=["actions"])
async def list_actions(
    role: WorkspaceUserRole,
    workflow_id: AnyWorkflowIDPath,
    session: AsyncDBSession,
) -> list[ActionReadMinimal]:
    """List all actions for a workflow."""
    statement = select(Action).where(
        Action.owner_id == role.workspace_id,
        Action.workflow_id == workflow_id,
    )
    results = await session.exec(statement)
    actions = results.all()
    response = [
        ActionReadMinimal(
            id=action.id,
            workflow_id=WorkflowUUID.new(action.workflow_id).short(),
            type=action.type,
            title=action.title,
            description=action.description,
            status=action.status,
        )
        for action in actions
    ]
    return response


@router.post("", tags=["actions"])
async def create_action(
    role: WorkspaceUserRole,
    params: ActionCreate,
    session: AsyncDBSession,
) -> ActionReadMinimal:
    """Create a new action for a workflow."""
    if role.workspace_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Workspace ID is required"
        )
    action = Action(
        owner_id=role.workspace_id,
        workflow_id=WorkflowUUID.new(params.workflow_id),
        type=params.type,
        title=params.title,
        description="",  # Default to empty string
    )
    # Check if a clashing action ref exists
    statement = select(Action).where(
        Action.owner_id == role.workspace_id,
        Action.workflow_id == action.workflow_id,
        Action.ref == action.ref,
    )
    result = await session.exec(statement)
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Action ref already exists in the workflow",
        )

    session.add(action)
    await session.commit()
    await session.refresh(action)

    action_metadata = ActionReadMinimal(
        id=action.id,
        workflow_id=WorkflowUUID.new(action.workflow_id).short(),
        type=action.type,
        title=action.title,
        description=action.description,
        status=action.status,
    )
    return action_metadata


@router.get("/{action_id}", tags=["actions"])
async def get_action(
    role: WorkspaceUserRole,
    action_id: ActionID,
    workflow_id: AnyWorkflowIDPath,
    session: AsyncDBSession,
) -> ActionRead:
    """Get an action."""
    statement = select(Action).where(
        Action.owner_id == role.workspace_id,
        Action.id == action_id,
        Action.workflow_id == workflow_id,
    )
    result = await session.exec(statement)
    try:
        action = result.one()
    except NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        ) from e

    # Add default value for input if it's empty
    if len(action.inputs) == 0:
        # Lookup action type in the registry
        ra_service = RegistryActionsService(session, role=role)
        reg_action = await ra_service.load_action_impl(action.type)
        # We want to construct a YAML string that contains the defaults
        prefilled_inputs = "\n".join(
            f"{field}: "
            for field, field_info in reg_action.args_cls.model_fields.items()
            if field_info.default is PydanticUndefined
        )
        action.inputs = prefilled_inputs

    return ActionRead(
        id=action.id,
        type=action.type,
        title=action.title,
        description=action.description,
        status=action.status,
        inputs=action.inputs,
        control_flow=ActionControlFlow(**action.control_flow),
    )


@router.post("/{action_id}", tags=["actions"])
async def update_action(
    role: WorkspaceUserRole,
    action_id: ActionID,
    params: ActionUpdate,
    session: AsyncDBSession,
) -> ActionRead:
    """Update an action."""
    # Fetch the action by id
    statement = select(Action).where(
        Action.owner_id == role.workspace_id,
        Action.id == action_id,
    )
    result = await session.exec(statement)
    try:
        action = result.one()
    except NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        ) from e

    if params.title is not None:
        action.title = params.title
    if params.description is not None:
        action.description = params.description
    if params.status is not None:
        action.status = params.status
    if params.inputs is not None:
        action.inputs = params.inputs
        # Validate that it's a valid YAML string
        try:
            yaml.safe_load(action.inputs)
        except yaml.YAMLError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action input contains invalid YAML",
            ) from e
    if params.control_flow is not None:
        action.control_flow = params.control_flow.model_dump(mode="json")

    session.add(action)
    await session.commit()
    await session.refresh(action)

    return ActionRead(
        id=action.id,
        type=action.type,
        title=action.title,
        description=action.description,
        status=action.status,
        inputs=action.inputs,
    )


@router.delete("/{action_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["actions"])
async def delete_action(
    role: WorkspaceUserRole,
    action_id: ActionID,
    session: AsyncDBSession,
) -> None:
    """Delete an action."""
    statement = select(Action).where(
        Action.owner_id == role.workspace_id,
        Action.id == action_id,
    )
    result = await session.exec(statement)
    try:
        action = result.one()
    except NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        ) from e
    # If the user doesn't own this workflow, they can't delete the action
    await session.delete(action)
    await session.commit()
