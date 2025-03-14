from pydantic import BaseModel

from aegiscan.identifiers import TagID


class WorkflowTagCreate(BaseModel):
    tag_id: TagID
