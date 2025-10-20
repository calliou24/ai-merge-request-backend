from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_providers import AI_Providers
from app.schemas.providers import CreateProviderInput


async def create_provider(
    db: AsyncSession, provider_input: CreateProviderInput
) -> AI_Providers:
    provider = AI_Providers(**provider_input.model_dump())

    db.add(provider)
    await db.commit()
    await db.refresh(provider)

    return provider


async def get_provider_by_name(
    db: AsyncSession, provider_input: CreateProviderInput
) -> AI_Providers | None:
    provider = await db.execute(
        select(AI_Providers).where(
            AI_Providers.name == provider_input.name,
            AI_Providers.deleted_at.is_(None),
        )
    )

    return provider.scalar_one_or_none()


async def get_provider_by_id(db: AsyncSession, provider_id: int) -> AI_Providers:
    provider = await db.execute(
        select(AI_Providers).where(
            AI_Providers.id == provider_id, AI_Providers.deleted_at.is_(None)
        )
    )

    return provider.scalar_one_or_none()


async def get_all_providers(db: AsyncSession) -> list[AI_Providers]:
    providers = await db.execute(
        select(AI_Providers).where(AI_Providers.deleted_at.is_(None))
    )

    return providers.scalars().all()
