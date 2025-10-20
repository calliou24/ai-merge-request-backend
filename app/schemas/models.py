from datetime import datetime

from pydantic import BaseModel


class ModelBase(BaseModel):
    provider_id: int
    name: str


class CreateModelInput(ModelBase):
    pass


class ReadModel(ModelBase):
    id: int
    created_at: datetime
    updated_at: datetime
