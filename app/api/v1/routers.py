from api.deps import FileData, MediaAccess_ServiceJWT, MimeFile, SessionDep
from config import logger
from db.crud import create_file
from fastapi import APIRouter, HTTPException, status
from patisson_request.service_responses import IntertnalMediaResponse

router = APIRouter()

@router.post('/upload')
async def upload_route(service: MediaAccess_ServiceJWT, 
                       session: SessionDep, file: FileData,
                       mime_type: MimeFile
                       ) -> IntertnalMediaResponse.FileID:
    async with session as session_: 
        is_valid, body = await create_file(
            session=session_, 
            file_data=file,
            mime_type=mime_type
            )
    if is_valid:
        logger.info(f'service {service.sub} uploaded file {body.id}')  # type: ignore[reportAttributeAccessIssue]
        return IntertnalMediaResponse.FileID(id=body.id)  # type: ignore[reportAttributeAccessIssue]
    else:
        logger.info(str(body) + f'service initiator {service.sub}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=[body.model_dump()]
            )