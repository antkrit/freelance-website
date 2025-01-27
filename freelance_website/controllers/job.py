from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from ..models.job import JobRequest, JobRequestPatch


async def get_job_requests_controller(limit: int, offset: int, session: AsyncSession) -> list[JobRequest]:
    return [request for request in await session.scalars(select(JobRequest).limit(limit).offset(offset))]


async def get_job_requests_by_user_id_controller(user_id: str, limit: int, offset: int, session: AsyncSession) -> list[JobRequest]:
    return [
        request 
        for request in await session.scalars(
            select(JobRequest)
            .where(JobRequest.user_id==user_id)
            .limit(limit)
            .offset(offset)
        )
    ]

async def get_job_request_by_id_controller(request_id: str, session: AsyncSession) -> JobRequest:
    user = await session.execute(select(JobRequest).where(JobRequest.id == request_id))
    user = user.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job request with id {request_id} not found."
        )

    return user


async def create_job_request_controller(request_data: dict, session: AsyncSession) -> JobRequest:
    try:
        request = JobRequest(**request_data)

        session.add(request)
        await session.commit()
        await session.refresh(request)

        return request
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create job request with such parameters."
        )
    

async def patch_job_request_controller(job_request: JobRequest, request_data: JobRequestPatch, session: AsyncSession) -> JobRequest:
    patch_values = request_data.model_dump(exclude_unset=True)
    for k, v in patch_values.items():
        setattr(job_request, k, v)

    session.add(job_request)
    await session.commit()
    await session.refresh(job_request)

    return job_request


async def delete_job_request_controller(job_request: JobRequest, session: AsyncSession) -> None:
    await session.delete(job_request)
    await session.commit()
