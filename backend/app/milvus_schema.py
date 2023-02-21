
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection
)

from .constants import COLLECTION_NAME

def establish_connection():
  connections.connect(
    alias="default", 
    host='localhost', 
    port='19530'
  )

def create_collection():
  fields = [
      FieldSchema(name='work_id', dtype=DataType.VARCHAR, max_length=32, is_primary=True),
      FieldSchema(name='embeddings', dtype=DataType.FLOAT_VECTOR, dim=768)
  ]

  schema = CollectionSchema(fields, "Testing")
  paper_trail_collection = Collection(COLLECTION_NAME, schema)

  index_params = {
      "metric_type": "IP",
      "index_type": "IVF_FLAT",
      "params": {"nlist": 128}
  }

  paper_trail_collection.create_index(field_name="embeddings", index_params=index_params)

if __name__ == "__main__":
  establish_connection()
  create_collection()