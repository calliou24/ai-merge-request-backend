

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from app.db.session import get_db
from app.schemas.defaults import SuccessResponse
from app.schemas.templates import TemplateCreate, TemplateRead

from app.repositories import templates


router_templates = APIRouter(prefix="/templates")

@router_templates.get('', response_model=list[TemplateRead], status_code=HTTP_200_OK)
async def getAllTemplates(db: AsyncSession = Depends(get_db)): 
    return await templates.getAllTemplates(db)

@router_templates.post("", response_model=TemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(template_input: TemplateCreate ,db: AsyncSession = Depends(get_db)): 
    return await templates.create_template(db, template_input)

@router_templates.delete("/{template_id}",  status_code=HTTP_200_OK ) 
async def delete_template(template_id: int, db:AsyncSession = Depends(get_db)): 
    get_template = await templates.get_template(db, template_id)

    if get_template is None: 
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, 
            detail=f"Template with id: {template_id} not found"
        )

    await templates.deleteTemplate(db, get_template)

    return SuccessResponse(
        success=True, 
        message="Template deleted successfully"
    ) 
