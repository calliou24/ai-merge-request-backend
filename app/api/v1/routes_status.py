from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession  

from app.core.config import settings
from app.db.session import get_db

status_router = APIRouter()

@status_router.get("/status")
async def status(db:AsyncSession = Depends(get_db)):
    db_ok: bool

    try:
        result = await db.execute(text("SELECT 1"))
        db_ok = (result.scalar() == 1)
    except Exception: 
        db_ok = False

    return { 
        "app": settings.APP_NAME,
        "env": settings.ENV,
        "database": "ok" if db_ok else "error"
    }