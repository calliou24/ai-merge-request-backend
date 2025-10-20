from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_409_CONFLICT

from app.db.session import get_db

from app.repositories import models
from app.schemas.models import CreateModelInput, ReadModel


router_models = APIRouter(prefix="/ai-model")


@router_models.post("", response_model=ReadModel, status_code=HTTP_201_CREATED)
async def create_model(
    model_input: CreateModelInput, db: AsyncSession = Depends(get_db)
):

    model = await models.get_model(db, model_input)
    if model is not None:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail=f"Model with the name: {model_input.name} already exist",
        )

    return await models.create_model(db, model_input)


@router_models.get("", response_model=list[ReadModel], status_code=HTTP_200_OK)
async def get_all_models(db: AsyncSession = Depends(get_db)):
    return await models.get_all_models(db)
