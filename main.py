from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from freelance_website.config import api_settings
from freelance_website.dependencies.database import async_engine, get_async_session
from freelance_website.routes import api, docs
from freelance_website.models.user import User, UserRoles
from freelance_website.utils import get_password_hash

origins = ["http://localhost", "http://localhost:3000"]


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create superuser if not exists
    async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        admin_user = await session.exec(select(User).where(User.username=="admin"))
        if not admin_user.first():
            admin_user = User(username="admin", role=UserRoles.admin, hashed_password=get_password_hash("root"))

            await session.add(admin_user)
            await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start up
    await init_db()

    yield

    # shut down


app: FastAPI = FastAPI(lifespan=lifespan, **api_settings.model_dump(exclude={"prefix": True}))

app.include_router(api.api_router, prefix=api_settings.prefix)
app.include_router(docs.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
