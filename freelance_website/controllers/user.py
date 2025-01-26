from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from ..models.user import User, UserPatch


async def get_users_controller(limit: int, offset: int, session: AsyncSession) -> list[User]:
    return [user for user in await session.scalars(select(User).limit(limit).offset(offset))]


async def get_user_by_id_controller(user_id: str, session: AsyncSession) -> User:
    user = await session.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )

    return user


async def patch_user_controller(user: User, user_data: UserPatch, session: AsyncSession) -> User:
    patch_values = user_data.model_dump(exclude_unset=True)
    for k, v in patch_values.items():
        setattr(user, k, v)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def delete_user_controller(user: User, session: AsyncSession) -> None:
    await session.delete(user)
    await session.commit()

