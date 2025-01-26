import enum
from typing import Optional

from sqlalchemy import Column, Enum
from sqlmodel import Field, SQLModel
from pydantic import BaseModel

from .abstract import UUIDModel, TimedModel


class LoginRequest(BaseModel):
   username: str
   password: str


class RegisterRequest(BaseModel):
   username: str
   password: str


class UserRoles(enum.StrEnum):
   admin = "admin"
   user = "user"


class UserBase(SQLModel):
   username: str = Field(max_length=255, nullable=False, unique=True)
   role: UserRoles = Field(
        sa_column=Column(
            "role",
            Enum(UserRoles),
            default=UserRoles.user
        )
   )
   disabled: bool = Field(default=False)


class User(
   UUIDModel,
   TimedModel,
   UserBase,
   table=True
):
   __tablename__ = f"users"

   hashed_password: str = Field(nullable=False)


class UserRead(UUIDModel, UserBase):
   ...


class UserPatch(UserBase):
   username: Optional[str] = Field(max_length=255)
