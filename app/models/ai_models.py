from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.ai_providers import AI_Providers
from app.models.soft_delete_mixin import SoftDeleteMixin
from app.models.timestamp_mixin import TimestampMixin


class AI_Models(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "ai_models"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("ai_providers.id"))
    provider: Mapped[AI_Providers] = relationship()
