from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, Query, status
from sqlalchemy.ext.asyncio.session import AsyncSession

from ..controllers.user import (
    get_users_controller,
    get_user_by_id_controller,
    patch_user_controller,
    delete_user_controller,
)
from ..dependencies.auth import get_current_active_user, Autorized
from ..dependencies.database import get_async_session
from ..models.abstract import PaginatedResponse
from ..models.user import UserRead, UserRoles, UserPatch


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=PaginatedResponse[UserRead], summary="Get list of users")
async def get_users(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[UserRead, Depends(Autorized(allowed_roles=[UserRoles.admin,]))],
    limit: int = Query(10, ge=0),
    offset: int = Query(0, ge=0)
):
    users = await get_users_controller(limit=limit, offset=offset, session=session)
    return {
        "count": len(users),
        "items": users,
    }


@router.get("/me", response_model=UserRead, summary="Return current user")
async def read_users_me(current_user: Annotated[UserRead, Depends(get_current_active_user)]):
    return current_user


@router.get("/{user_id}", response_model=UserRead, summary="Get user by id")
async def get_user_by_id(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[UserRead, Depends(Autorized(allowed_roles=[UserRoles.admin,]))]
):
    return await get_user_by_id_controller(user_id=user_id, session=session)


@router.post("/{user_id}/disable", response_model=UserRead, summary="Block user")
async def disable_user(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[UserRead,  Depends(Autorized(allowed_roles=[UserRoles.admin,]))]
):
    if user_id == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot block yourself.",
        )
    
    user = await get_user_by_id_controller(user_id, session)
    if user.role == UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot block user with role {user.role}",
        )

    return await patch_user_controller(user=user, user_data=UserPatch(disabled=True), session=session)


@router.patch("/{user_id}", response_model=UserRead, summary="Update user")
async def patch_user(
    user_id: str,
    user_data: UserPatch,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[UserRead, Depends(Autorized(allowed_roles=[UserRoles.admin,]))]
):
    user = await get_user_by_id_controller(user_id, session)
    if user.role == UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot patch user with role {user.role}",
        )
    return await patch_user_controller(user=user, user_data=user_data, session=session)


@router.delete("/{user_id}", summary="Delete user")
async def delete_user(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[UserRead,  Depends(Autorized(allowed_roles=[UserRoles.admin,]))]
):
    if user_id == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself.",
        )
    
    user = await get_user_by_id_controller(user_id, session)
    if user.role == UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete user with role {user.role}",
        )
    
    await delete_user_controller(user, session)
    return Response(status_code=status.HTTP_200_OK)
