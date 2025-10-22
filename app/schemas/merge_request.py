from enum import Enum
from pydantic import BaseModel, constr

class MergeRequestInput(BaseModel):
    project_id: int
    origin_branch: constr(min_length=1)
    target_branch: constr(min_length=1) 
    title: constr(min_length=1) 
    description: constr(min_length=1)
    pat: constr(min_length=10)


class MergeRequestDataAiInput(BaseModel):
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

class CreatedMergeRequestResponse(BaseModel):
    merge_request_id: int
    message: str