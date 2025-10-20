from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_409_CONFLICT
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.providers import CreateProviderInput, ProviderReader

from app.repositories import providers

router_providers = APIRouter(prefix="/ai-provider")


@router_providers.post("", response_model=ProviderReader, status_code=HTTP_201_CREATED)
async def create_provider(
    provider_input: CreateProviderInput, db: AsyncSession = Depends(get_db)
):
    provider = await providers.get_provider_by_name(db, provider_input)

    if provider is not None:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=f"Provider with name: {provider.name} and type: {provider.type.value} already exisst",
        )

    return await providers.create_provider(db, provider_input)


@router_providers.get("", response_model=list[ProviderReader], status_code=HTTP_200_OK)
async def get_all_providers(db: AsyncSession = Depends(get_db)):
    return await providers.get_all_providers(db)
