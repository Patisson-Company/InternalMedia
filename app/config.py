import logging
import os

from dotenv import load_dotenv
from patisson_request.core import SelfAsyncService
from patisson_request.services import Service

root_path = os.path.join(os.path.dirname(__file__), '..')

load_dotenv(dotenv_path=os.path.join(root_path, '.env'))

SERVICE_NAME: str = Service.INTERNAL_MEDIA.value
SERVICE_HOST: str = os.getenv("SERVICE_HOST")  # type: ignore[reportArgumentType]

DATABASE_URL: str = os.getenv("DATABASE_URL")  # type: ignore[reportArgumentType]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

EXTERNAL_SERVICES: list[Service] = [Service.AUTHENTICATION]


file_handler = logging.FileHandler(os.path.join(root_path, f'{SERVICE_NAME}.log'))
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    "%(levelname)s | %(asctime)s | %(module)s | %(funcName)s | %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
))

logger = logging.getLogger(SERVICE_NAME)
logger.addHandler(file_handler)

SelfService = SelfAsyncService(
    self_service=Service(SERVICE_NAME),
    login=os.getenv("LOGIN"),  # type: ignore[reportArgumentType]
    password=os.getenv("PASSWORD"),  # type: ignore[reportArgumentType]
    external_services=EXTERNAL_SERVICES,
    logger_object=logger
)