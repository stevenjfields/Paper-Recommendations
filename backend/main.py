import logging
from logging.config import dictConfig
import uvicorn
from pymilvus import utility

from app.api import app
from app.constants import COLLECTION_NAME, LOGGER_TITLE
from app.milvus_schema import establish_connection, create_collection
from app.log_config import LogConfig

if __name__ == '__main__':
    # Create Milvus Schema if it doesn't already exist
    establish_connection()
    if not utility.has_collection(COLLECTION_NAME):
        create_collection()

    dictConfig(LogConfig().dict()) # dict is deprecated need to look into alternative later
    logger = logging.getLogger(LOGGER_TITLE)

    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level='info', workers=1)