import uvicorn
from pymilvus import utility

from app.api import app
from app.constants import COLLECTION_NAME
from app.milvus_schema import establish_connection, create_collection

if __name__ == '__main__':
    # Create Milvus Schema if it doesn't already exist
    establish_connection()
    if not utility.has_collection(COLLECTION_NAME):
        create_collection()

    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level='info', reload=True)