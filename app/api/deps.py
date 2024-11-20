from typing import Annotated

import config
from config import logger
from db.base import get_session
from fastapi import Depends, File, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from opentelemetry import trace
from patisson_request.depends import (dep_jaeger_service_decorator,
                                      verify_service_token_dep)
from patisson_request.errors import ErrorCode, ErrorSchema, InvalidJWT
from patisson_request.jwt_tokens import ServiceAccessTokenPayload
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()
tracer = trace.get_tracer(__name__)

@dep_jaeger_service_decorator(tracer)
async def verify_service_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> ServiceAccessTokenPayload:
    token = credentials.credentials
    try:
        payload = await verify_service_token_dep(
            self_service=config.SelfService, access_token=token)
    except InvalidJWT as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=[e.error_schema.model_dump()]
            )
    return payload

async def verify_serice__media_access__token(
    payload: ServiceAccessTokenPayload = Depends(verify_service_token)
    ) -> ServiceAccessTokenPayload:
    REQUIRED_PERM = [
        payload.role.permissions.media_access
    ]
    if not all(REQUIRED_PERM):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=[ErrorSchema(
                error=ErrorCode.ACCESS_ERROR
                ).model_dump()]
            )
    return payload

async def read_file(file: UploadFile = File(...)) -> bytes:
    data = await file.read()
    if len(data) > config.MAX_FILE_SIZE:
        logger.warning(f'the received file exceeds the limit')
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=[ErrorSchema(
                error=ErrorCode.INVALID_PARAMETERS,
                extra=f"File size exceeds the {config.MAX_FILE_SIZE}MB limit"
            ).model_dump()])
    return file


SessionDep = Annotated[AsyncSession, Depends(get_session)]

ServiceJWT = Annotated[ServiceAccessTokenPayload, Depends(verify_service_token)]
MediaAccess_ServiceJWT = Annotated[ServiceAccessTokenPayload, Depends(verify_serice__media_access__token)]

FileData = Annotated[bytes, Depends(read_file)]