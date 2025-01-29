import uuid
from typing import Optional

from pydantic import BaseModel, NonNegativeFloat
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, CheckConstraint
from sqlalchemy.dialects.postgresql import TEXT

from .abstract import UUIDModel, TimedModel


class JobRequestBase(SQLModel):
   title: str = Field(max_length=120, nullable=False)
   description: str = Field(sa_column=Column(TEXT, nullable=False))
   country: str = Field(max_length=120, nullable=False)
   budget: float = Field(sa_column_args=[CheckConstraint('budget>0')], nullable=False)


class JobRequest(
   UUIDModel,
   TimedModel,
   JobRequestBase,
   table=True
):
   __tablename__ = "job_requests"

   user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)


class JobRequestPatch(BaseModel):
   title: Optional[str] = None
   description: Optional[str] = None
   country: Optional[str] = None
   budget: Optional[NonNegativeFloat] = None
