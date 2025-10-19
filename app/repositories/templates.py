

from sqlalchemy import select
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.templates import Templates
from app.schemas.templates import TemplateCreate


async def create_template(db: AsyncSession, template_input: TemplateCreate) -> Templates:
    template = Templates(**template_input.model_dump())

    db.add(template)
    await db.commit()
    await db.refresh(template)

    return template

async def get_template(db: AsyncSession, template_id: int) -> Templates | None :
    result = await db.execute(
        select(Templates).where(
            Templates.id == template_id,
            Templates.deleted_at.is_(None)
        )
    )

    return result.scalar_one_or_none()

async def deleteTemplate(db: AsyncSession, template: Templates): 
    template.soft_delete()
    await db.commit()
