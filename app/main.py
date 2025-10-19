

from fastapi import  FastAPI
from app.api.v1.routes_status import status_router
from app.api.v1.routes_template import router_templates
from app.core.config import settings


app= FastAPI(title=settings.APP_NAME)

routers_v1 = [status_router, router_templates]

for router in routers_v1: 
    app.include_router(router, prefix='/api/v1')

@app.get("/")
def root(): 
    return {"message": "Hello worlds"}

