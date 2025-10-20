from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_models import AI_Models
from app.schemas.models import CreateModelInput


async def create_model(db: AsyncSession, create_model: CreateModelInput) -> AI_Models:
    ai_model = AI_Models(**create_model.model_dump())

    db.add(ai_model)
    await db.commit()
    await db.refresh(ai_model)

    return ai_model


async def get_all_models(db: AsyncSession) -> list[AI_Models]:
    models = await db.execute(select(AI_Models).where(AI_Models.deleted_at.is_(None)))

    return models.scalars().all()
