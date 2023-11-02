
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

logger = AppLogger().get_logger()

app = FastAPI()
templates = Jinja2Templates(directory="frontend")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"] ,
)

app.mount("/static/", StaticFiles(directory="./frontend/resources/"), "static")

@app.get("/paper/{work_id}/")
async def get_paper(work_id: str) -> Article:
    client = OpenAlexClient()
    paper = client.get_work_by_id(work_id)
    article = ArticleFactory.from_open_alex_response(paper)
    return article

@app.post("/references/")
async def get_references(parent: Article) -> Optional[List[Article]]:
    client = OpenAlexClient()
    references = []
    if parent.references:
        queries = parent.fetch_references_queries()
    else:
        queries = parent.fetch_related_queries()
            
    for query in queries:
        papers = client.get_works_by_filter(query)
        refs = [ArticleFactory.from_open_alex_response(paper) for paper in papers["results"]]
        references.extend(refs)
    return references

@app.post("/embeddings/")
async def embeddings(articles: List[Article]) -> dict:
    try:
        create_embeddings(articles)
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
    
    return {
        "status": "complete",
        "error": ""
    }

@app.post("/similarities/")
async def similarities(root: Article, target: Article, sources: List[Article]) -> Optional[List[WeightedEdge]]:
    try:
        sims = await get_similarities(root, target, sources)
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
    return sims

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})