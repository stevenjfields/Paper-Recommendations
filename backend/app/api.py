
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import requests
import json
from logging.config import dictConfig
import logging

from .constants import BASE_WORKS_URL, WORKS_ID_FILTER
from .models import Article, WeightedEdge
from .helpers import parse_article, create_embeddings, get_similarities
from .utils.logger import AppLogger

logger = AppLogger.__call__().get_logger()

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
    logger.info("info")
    logger.debug("debug")
    logger.warning("warning")
    logger.error("error")
    req = requests.get(BASE_WORKS_URL + f"/{work_id}")
    res = json.loads(req.content)
    article = parse_article(res)
    return article

@app.post("/references/")
async def get_references(parent: Article) -> Optional[List[Article]]:
    references = []
    if len(parent.references) > 0:
        queries = parent.fetch_references_queries()
    else:
        queries = parent.fetch_related_queries()
            
    for query in queries:
        req = requests.get(BASE_WORKS_URL + WORKS_ID_FILTER + query)
        res = json.loads(req.content)
        
        refs = [parse_article(result) for result in res["results"]]
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