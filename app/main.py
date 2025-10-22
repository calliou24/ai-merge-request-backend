from fastapi import FastAPI
from app.api.v1.routes_merge_request import router_merge
from app.api.v1.routes_models import router_models
from app.api.v1.routes_providers import router_providers
from app.api.v1.routes_status import status_router
from app.api.v1.routes_template import router_templates
from app.core.config import settings

# cors
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title=settings.APP_NAME)

routers_v1 = [
    status_router,
    router_templates,
    router_merge,
    router_providers,
    router_models,
]

for router in routers_v1:
    app.include_router(router, prefix="/api/v1")

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello worlds"}
