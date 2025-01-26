from typing import Annotated

from fastapi import APIRouter, Depends

from ..dependencies.auth import get_current_active_user
from ..models.user import User, UserRead


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
