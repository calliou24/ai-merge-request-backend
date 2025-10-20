from enum import Enum
from pydantic import BaseModel


class MergeRequestInput(BaseModel):
    project_id: int
    origin_branch: str
    target_branch: str
    context_ai: str
    pat: str
    template_id: int

    provider_id: int
    model: str


class MergeRequestInfoResponse(BaseModel):
    title: str
    description: str
