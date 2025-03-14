from enum import StrEnum

from pydantic import BaseModel

from aegiscan.identifiers import UserID, WorkspaceID


class OwnerType(StrEnum):
    USER = "user"
    WORKSPACE = "workspace"
    ORGANIZATION = "organization"


# === Memberships === #


# Params
class CreateMembershipParams(BaseModel):
    user_id: UserID
    workspace_id: WorkspaceID


# Responses
class MembershipResponse(BaseModel):
    user_id: UserID
    workspace_id: WorkspaceID
