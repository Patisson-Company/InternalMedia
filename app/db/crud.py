from typing import Literal

from db.models import File
from patisson_request.errors import ErrorCode, ErrorSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


async def create_file(session: AsyncSession, file_data: bytes) -> (
                          tuple[Literal[True], File]
                          | tuple[Literal[False], ErrorSchema]
                      ):
    try:
        file = File(
            data=file_data
        )
        session.add(file)
        await session.commit()
        return True, file
        
    except SQLAlchemyError as e:
        await session.rollback()
        return False, ErrorSchema(
            error=ErrorCode.INVALID_PARAMETERS,
            extra=str(e)
        )