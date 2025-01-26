from typing import Optional, Annotated

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from .database import get_async_session
from ..config import auth_settings
from ..utils import get_user
from ..models.user import UserRead
from ..models.token import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user(
      token: Annotated[str, Depends(oauth2_scheme)], 
      session: Annotated[AsyncSession, Depends(get_async_session)]
) -> Optional[UserRead]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, auth_settings.signature_key, algorithms=[auth_settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[UserRead, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=403, detail="Inactive user.")
    return current_user


class Autorize:
  
  def __init__(self, allowed_roles):
    self.allowed_roles = allowed_roles

  def __call__(self, user: Annotated[UserRead, Depends(get_current_active_user)]):
    if user.role in self.allowed_roles:
      return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="You don't have enough permissions."
    )
