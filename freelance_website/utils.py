import logging
import typing as t
import pickle

from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import auth_settings
from .models.user import User


logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(username: str, session: AsyncSession) -> t.Optional[User]:
    response = None
    try:
        user = await session.exec(select(User).where(User.username == username))
        response = user.first()
    except Exception as e:
        logger.exception(e)
    finally:
        return response


async def authenticate_user(username: str, password: str, *args, **kwargs) -> t.Optional[User]:
    user = await get_user(username, *args, **kwargs)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, auth_settings.signature_key, algorithm=auth_settings.algorithm)
    return encoded_jwt


def load_pickle(path: str):
    with open(path, 'rb') as file:
        return pickle.load(file)
