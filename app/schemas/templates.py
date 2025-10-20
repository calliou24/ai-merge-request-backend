from datetime import datetime
from pydantic import BaseModel, constr


class TemplateBase(BaseModel):
    title: constr(min_length=1, max_length=255)
    template: constr(min_length=1)
    description: constr(min_length=1)


class TemplateCreate(TemplateBase):
    pass


class TemplateRead(TemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
