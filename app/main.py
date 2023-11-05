import os
from logging.config import dictConfig
import uvicorn

from backend.api import app
from backend.constants import COLLECTION_NAME, LOGGER_TITLE, SETTINGS
from backend.utils.milvus_client import MilvusClient
from backend.utils.logger import AppLogger

logger = AppLogger().get_logger()

if __name__ == "__main__":
    # Create Milvus Schema if it doesn't already exist
    MilvusClient()
    settings = SETTINGS[os.environ.get("APP_ENV", "dev")]

    uvicorn.run("main:app", **settings["server_settings"])
