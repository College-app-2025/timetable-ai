from fastapi import APIRouter
from src.routes.auth_routes import router as auth_router

api_routes = APIRouter()
api_routes.include_router(auth_router)

__all__ = ["api_routes"]