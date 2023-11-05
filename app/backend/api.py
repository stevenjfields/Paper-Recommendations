from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import requests
import json

from backend.constants import BASE_WORKS_URL, WORKS_ID_FILTER
from backend.pydantic_models.article import Article, ArticleFactory
from backend.pydantic_models.weighted_edge import WeightedEdge
from backend.helpers import create_embeddings, get_similarities
from backend.utils.logger import AppLogger
from backend.utils.open_alex_client import OpenAlexClient
from backend.utils.milvus_client import MilvusClient

logger = AppLogger().get_logger()

app = FastAPI()
templates = Jinja2Templates(directory="frontend")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/", StaticFiles(directory="./frontend/resources/"), "static")


@app.get("/paper/{work_id}/")
async def get_paper(work_id: str) -> Article:
    open_alex_client = OpenAlexClient()
    milvus_client = MilvusClient()

    db_response = milvus_client.query_by_work_id(work_id)
    if db_response:
        return ArticleFactory.from_milvus_query(db_response)[0]

    paper = open_alex_client.get_work_by_id(work_id)
    return paper


@app.post("/references/")
async def get_references(parent: Article) -> Optional[List[Article]]:
    open_alex_client = OpenAlexClient()
    milvus_client = MilvusClient()

    references: List[Article] = []
    if parent.references:
        work_ids = parent.references
    else:
        work_ids = parent.related
    logger.info(f"Total References: {len(work_ids)}")

    db_response = milvus_client.query_by_work_ids(work_ids)
    references.extend(ArticleFactory.from_milvus_query(db_response))
    logger.info(f"Number previously embedded: {len(references)}")

    exclude_list = [ref.work_id for ref in references]
    work_ids = list(filter(lambda x: x not in exclude_list, work_ids))

    if work_ids:
        from_open_alex = open_alex_client.get_works_by_filter(work_ids)
        logger.info(f"Number received from open alex: {len(from_open_alex)}")
        references.extend(from_open_alex)

    return references


@app.post("/embeddings/")
async def embeddings(articles: List[Article]) -> dict:
    try:
        create_embeddings(articles)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}

    return {"status": "complete", "error": ""}


@app.post("/similarities/")
async def similarities(
    root: Article, target: Article, sources: List[Article]
) -> Optional[List[WeightedEdge]]:
    try:
        sims = await get_similarities(root, target, sources)
    except Exception as e:
        logger.exception(e)
        return {"status": "failed", "error": str(e)}
    return sims


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
