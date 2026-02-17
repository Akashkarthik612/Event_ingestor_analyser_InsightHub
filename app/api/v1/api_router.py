from fastapi import APIRouter
from app.api.v1.routers import events, health, analytics

api_router = APIRouter()

api_router.include_router(events.router)
api_router.include_router(health.router)
api_router.include_router(analytics.router)
