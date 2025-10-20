from datetime import datetime
from pydantic import BaseModel

from app.models.ai_providers import ProvidersTypes


class ProviderBase(BaseModel):
    name: str
    type: ProvidersTypes


class CreateProviderInput(ProviderBase):
    pass


class ProviderReader(ProviderBase):
    id: int
    created_at: datetime
    updated_at: datetime
