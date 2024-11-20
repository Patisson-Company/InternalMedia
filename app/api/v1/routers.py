from api.deps import MediaAccess_ServiceJWT, SessionDep, FileData
from config import logger
from db.crud import create_file
from fastapi import APIRouter, HTTPException, status
from patisson_request.service_responses import SuccessResponse

router = APIRouter()

@router.post('/upload')
async def upload_route(service: MediaAccess_ServiceJWT, 
                       session: SessionDep, file: FileData
                       ) -> SuccessResponse:
    async with session as session_: 
        is_valid, body = await create_file(
            session=session_, 
            file_data=file
            )
    if is_valid:
        logger.info(f'service {service.sub} uploaded file {body.id}')
        return SuccessResponse()
    else:
        logger.info(str(body) + f'service initiator {service.sub}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=[body.model_dump()]
            )