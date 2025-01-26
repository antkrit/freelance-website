from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from ..controllers.auth import login_controller, register_controller
from ..dependencies.database import get_async_session
from ..models.user import LoginRequest, RegisterRequest, UserRead
from ..models.token import Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login_for_access_token(request: LoginRequest, session: Annotated[AsyncSession, Depends(get_async_session)]):
    form_data = OAuth2PasswordRequestForm(username=request.username, password=request.password)
    return await login_controller(form_data, session=session)


@router.post("/register", response_model=UserRead)
async def register_user(request: RegisterRequest, session: Annotated[AsyncSession, Depends(get_async_session)]):
    return await register_controller(request, session=session)


@router.post(
    "/token",
    description="This endpoint is used for the Swagger UI authorization",
    response_model=Token,
    include_in_schema=False
)
async def login_for_access_token_swagger_ui(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    return await login_controller(form_data, session=session)
