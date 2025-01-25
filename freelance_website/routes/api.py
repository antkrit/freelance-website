from fastapi import APIRouter
from ..routes import ping

api_router = APIRouter()

api_router.include_router(ping.router)
