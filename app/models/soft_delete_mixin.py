import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

class SoftDeleteMixin():
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, index=True) 

    def soft_delete(self):
        self.deleted_at = func.now()
        