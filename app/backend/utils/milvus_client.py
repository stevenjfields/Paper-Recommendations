import os
from typing import *

from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)

from backend.pydantic_models.article import Article
from backend.utils.logger import AppLogger

logger = AppLogger().get_logger()


class MilvusClient:
    _collection_name = "Work_Embeddings"
    _collection = None
    collection_fields = None

    def __init__(self, collection_name=None):
        if collection_name:
            self._collection_name = collection_name

        self._establish_connection()
        if not utility.has_collection(self._collection_name):
            self._create_collection()

        self._collection = Collection(self._collection_name)
        self._collection.load()
        self.collection_fields = [
            field.name for field in self._collection.schema.fields
        ]

    def _establish_connection(self):
        uri = os.getenv("MILVUS_ADDRESS")
        if uri:
            connections.connect(alias="default", uri=f"http://{uri}")
        else:
            connections.connect(alias="default", host="localhost", port="19530")

    def _create_collection(self):
        fields = [
            FieldSchema(
                name="work_id", dtype=DataType.VARCHAR, max_length=32, is_primary=True
            ),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(
                name="landing_page_url", dtype=DataType.VARCHAR, max_length=512
            ),
            FieldSchema(
                name="authors",
                dtype=DataType.ARRAY,
                element_type=DataType.VARCHAR,
                max_length=128,
                max_capacity=64,
                default_value=[],
            ),
            FieldSchema(name="host_venue", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(
                name="affiliations",
                dtype=DataType.ARRAY,
                element_type=DataType.VARCHAR,
                max_length=256,
                max_capacity=64,
                default_value=[],
            ),
            FieldSchema(
                name="concepts",
                dtype=DataType.ARRAY,
                element_type=DataType.VARCHAR,
                max_length=64,
                max_capacity=256,
                default_value=[],
            ),
            FieldSchema(
                name="references",
                dtype=DataType.ARRAY,
                element_type=DataType.VARCHAR,
                max_length=32,
                max_capacity=256,
                default_value=[],
            ),
            FieldSchema(
                name="related",
                dtype=DataType.ARRAY,
                element_type=DataType.VARCHAR,
                max_length=32,
                max_capacity=256,
                default_value=[],
            ),
            FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=768),
        ]

        schema = CollectionSchema(fields)
        paper_trail_collection = Collection(self._collection_name, schema)

        index_params = {
            "metric_type": "IP",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1},
        }

        paper_trail_collection.create_index(
            field_name="embeddings", index_params=index_params
        )

    def _format_str_list_query(self, input_list: List[str]) -> str:
        str_list = str(input_list)
        return str_list.replace("'", '"')

    def query_by_work_id(
        self, work_id: str, fields: Optional[List[str]] = None
    ) -> dict:
        return self._collection.query(
            expr=f'work_id in ["{work_id}"]',
            output_fields=fields if fields else self.collection_fields,
        )

    def query_by_work_ids(
        self, work_ids: List[str], fields: Optional[List[str]] = None
    ) -> dict:
        work_ids_query = self._format_str_list_query(work_ids)
        return self._collection.query(
            expr=f"work_id in {work_ids_query}",
            output_fields=fields if fields else self.collection_fields,
        )

    def insert_embedded_articles(self, articles: List[Article], embeddings):
        logger.info(f"Inserting embeddings for {len(articles)} works.")
        work_ids = [article.work_id for article in articles]
        title = [article.title for article in articles]
        url = [article.landing_page_url for article in articles]
        authors = [article.authors for article in articles]
        host_venue = [article.host_venue for article in articles]
        affiliations = [article.affiliations for article in articles]
        concepts = [article.concepts for article in articles]
        references = [article.references for article in articles]
        related = [article.related for article in articles]
        try:
            self._collection.insert(
                [
                    work_ids,
                    title,
                    url,
                    authors,
                    host_venue,
                    affiliations,
                    concepts,
                    references,
                    related,
                    embeddings,
                ]
            )
        except Exception as e:
            logger.exception(e)
