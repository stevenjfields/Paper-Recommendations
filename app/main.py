import os
from logging.config import dictConfig
import uvicorn
from pymilvus import utility

from backend.api import app
from backend.constants import COLLECTION_NAME, LOGGER_TITLE, SETTINGS
from backend.milvus_schema import establish_connection, create_collection
from backend.utils.logger import AppLogger

logger = AppLogger().get_logger()

if __name__ == '__main__':
    # Create Milvus Schema if it doesn't already exist
    establish_connection()
    if not utility.has_collection(COLLECTION_NAME):
        create_collection()

    settings = SETTINGS[os.environ.get("APP_ENV", "dev")]


    uvicorn.run("main:app", **settings["server_settings"])