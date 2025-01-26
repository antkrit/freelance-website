from datetime import timedelta
from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..utils import authenticate_user, create_access_token, get_user, get_password_hash
from ..config import auth_settings
from ..models.user import RegisterRequest, User


async def login_controller(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], *args, **kwargs):
    user = await authenticate_user(form_data.username, form_data.password, *args, **kwargs)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=float(auth_settings.expiration_time_minutes))
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


async def register_controller(user_data: RegisterRequest, session: AsyncSession):
    user = await get_user(user_data.username, session=session)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"User {user_data.username} already exists."
        )

    user = User(username=user_data.username, hashed_password=get_password_hash(user_data.password))
    session.add(user)
    session.commit()

    return user

