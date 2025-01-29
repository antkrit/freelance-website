from typing import Annotated

from catboost import CatBoostRegressor
from fastapi import APIRouter, Depends, HTTPException, Response, Query, status
from sqlalchemy.ext.asyncio.session import AsyncSession
from sklearn.feature_extraction.text import TfidfVectorizer

from ..controllers.job import (
    get_job_requests_controller,
    get_job_requests_by_user_id_controller,
    get_job_request_by_id_controller,
    create_job_request_controller,
    patch_job_request_controller,
    suggest_price_for_job_request_controller,
    delete_job_request_controller,
)
from ..dependencies.ai import Model, Vectorizer
from ..dependencies.auth import get_current_active_user
from ..dependencies.database import get_async_session
from ..models.abstract import PaginatedResponse
from ..models.job import JobRequest, JobRequestBase, JobRequestPatch
from ..models.user import UserRoles, UserRead


router = APIRouter(prefix="/jobs", tags=["Job Requests"])


@router.get("/", response_model=PaginatedResponse[JobRequest], summary="Get list of job requests")
async def get_job_requests(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[UserRead, Depends(get_current_active_user)],
    limit: int = Query(10, ge=0),
    offset: int = Query(0, ge=0)
):
    requests = await get_job_requests_controller(limit=limit, offset=offset, session=session)
    return {
        "count": len(requests),
        "items": requests,
    }


@router.post("/", response_model=JobRequest, summary="Create job request")
async def create_job_request(
    request_data: JobRequestBase,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[UserRead, Depends(get_current_active_user)],
):
    request_data = request_data.model_dump()
    request_data["user_id"] = current_user.id
    return await create_job_request_controller(request_data=request_data, session=session)


@router.get("/user/{user_id}", response_model=PaginatedResponse[JobRequest], summary="Get list of job requests by user id")
async def get_job_requests(
    user_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[UserRead, Depends(get_current_active_user)],
    limit: int = Query(10, ge=0),
    offset: int = Query(0, ge=0)
):
    requests = await get_job_requests_by_user_id_controller(user_id, limit=limit, offset=offset, session=session)
    return {
        "count": len(requests),
        "items": requests,
    }


@router.get("/{request_id}", response_model=JobRequest, summary="Return job request by id")
async def get_job_request_by_id(
    request_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[UserRead, Depends(get_current_active_user)],
):
    return await get_job_request_by_id_controller(request_id=request_id, session=session)


@router.post("/{request_id}/suggest-budget", summary="Suggest budget for job request")
async def suggest_budget_job_request(
    request_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    model: Annotated[CatBoostRegressor, Depends(Model("price_suggestion"))],
    vectorizer: Annotated[TfidfVectorizer, Depends(Vectorizer("price_suggestion"))],
    current_user: Annotated[UserRead, Depends(get_current_active_user)],
):
    job_request = await get_job_request_by_id_controller(request_id, session)
    if job_request.user_id != current_user.id and current_user.role != UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot patch this job request.",
        )
    suggested_budget = await suggest_price_for_job_request_controller(job_request=job_request, model=model, vectorizer=vectorizer)
    return {"budget": suggested_budget}


@router.patch("/{request_id}", response_model=JobRequest, summary="Update job request")
async def patch_job_request(
    request_id: str,
    request_data: JobRequestPatch,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[UserRead, Depends(get_current_active_user)],
):
    job_request = await get_job_request_by_id_controller(request_id, session)
    if job_request.user_id != current_user.id and current_user.role != UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot patch this job request.",
        )
    return await patch_job_request_controller(job_request=job_request, request_data=request_data, session=session)


@router.delete("/{request_id}", summary="Delete job request")
async def delete_job_request(
    request_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: Annotated[UserRead, Depends(get_current_active_user)]
):
    job_request = await get_job_request_by_id_controller(request_id, session)
    if job_request.user_id != current_user.id and current_user.role != UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot delete this job request.",
        )
    
    await delete_job_request_controller(job_request, session)
    return Response(status_code=status.HTTP_200_OK)
