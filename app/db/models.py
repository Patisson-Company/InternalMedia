from db.base import Base
from sqlalchemy import Column, LargeBinary, String
from ulid import ULID


def ulid() -> str:
    return str(ULID())


class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, default=ulid)
    data = Column(LargeBinary, nullable=False)