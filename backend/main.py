import os
import logging
from logging.config import dictConfig
import uvicorn
from pymilvus import utility

from app.api import app
from app.constants import COLLECTION_NAME, LOGGER_NAME, SETTINGS
from app.milvus_schema import establish_connection, create_collection
from app.log_config import LogConfig

if __name__ == '__main__':
    # Create Milvus Schema if it doesn't already exist
    establish_connection()
    if not utility.has_collection(COLLECTION_NAME):
        create_collection()

    settings = SETTINGS[os.environ.get("APP_ENV", "dev")]

    dictConfig(LogConfig().dict())
    logger = logging.getLogger(LOGGER_NAME)

    uvicorn.run("main:app", **settings["server_settings"])