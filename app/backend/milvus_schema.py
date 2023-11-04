import os

from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection
)

from backend.constants import COLLECTION_NAME

def establish_connection():
  uri = os.getenv("MILVUS_ADDRESS")
  if uri:
    connections.connect(alias="default", uri=f"http://{uri}")
  else:
    connections.connect(
      alias="default", 
      host="localhost",
      port="19530"
    )

def create_collection():
  fields = [
      FieldSchema(name='work_id', dtype=DataType.VARCHAR, max_length=32, is_primary=True),
      FieldSchema(name='title', dtype=DataType.VARCHAR, max_length=512),
      FieldSchema(name='landing_page_url', dtype=DataType.VARCHAR, max_length=512),
      FieldSchema(name='authors', dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_length=128, max_capacity=32),
      FieldSchema(name='host_venue', dtype=DataType.VARCHAR, max_length=512),
      FieldSchema(name='concepts', dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_length=64, max_capacity=128),
      FieldSchema(name='references', dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_length=32, max_capacity=128),
      FieldSchema(name='related', dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_length=32, max_capacity=128),
      FieldSchema(name='embeddings', dtype=DataType.FLOAT_VECTOR, dim=768),
  ]

  schema = CollectionSchema(fields, "Works")
  paper_trail_collection = Collection(COLLECTION_NAME, schema)

  index_params = {
      "metric_type": "IP",
      "index_type": "IVF_FLAT",
      "params": {"nlist": 1}
  }

  paper_trail_collection.create_index(field_name="embeddings", index_params=index_params)

if __name__ == "__main__":
  establish_connection()
  create_collection()