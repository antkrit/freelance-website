from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from ..config import db_settings


async_engine = create_async_engine(
   db_settings.connection_string,
   echo=True,
   future=True
)


async def get_async_session():
   async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
   async with async_session() as session:
      yield session
