from enum import Enum
from pydantic import BaseModel


class MergeRequestInput(BaseModel):
    project_id: int
    origin_branch: str
    target_branch: str
    context_ai: str
    pat: str
    template_id: int


class MergeRequestInfoResponse(BaseModel):
    title: str
    description: str
