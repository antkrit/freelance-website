from fastapi import APIRouter
from ..routes import auth, job, ping, user

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(job.router)
api_router.include_router(ping.router)
api_router.include_router(user.router)
