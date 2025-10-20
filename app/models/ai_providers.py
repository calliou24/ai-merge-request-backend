from enum import Enum
from sqlalchemy import Integer, String, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.soft_delete_mixin import SoftDeleteMixin
from app.models.timestamp_mixin import TimestampMixin


class ProvidersTypes(str, Enum):
    open_router = "OPEN_ROUTER"
    cerebras = "CEREBRAS"


class AI_Providers(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "ai_providers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    type: Mapped[ProvidersTypes] = mapped_column(
        SqlEnum(ProvidersTypes, name="provider_type"), nullable=False, index=True
    )
