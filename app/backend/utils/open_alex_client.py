from requests import Session, Response
import json
from http import HTTPStatus
from typing import *
from backend.pydantic_models.article import Article, ArticleFactory


class OpenAlexClient:
    _base_url = "https://api.openalex.org"
    _works_id_filter = "?filter=openalex_id:"

    def __init__(self):
        self._session = Session()

    def get_work_by_id(self, work_id: str) -> Article:
        get_work_url = f"{self._base_url}/works/{work_id}"
        response = self._session.get(get_work_url)
        response = self._handle_response_codes(response)
        return ArticleFactory.from_open_alex_response(response)

    def get_works_by_filter(self, work_ids: List[str]) -> List[Article]:
        queries = list()
        for i in range(0, len(work_ids), 50):
            queries.append("|".join(work_ids[i : i + 50]))

        works = list()
        for query in queries:
            works_filter_url = f"{self._base_url}/works{self._works_id_filter}{query}"
            response = self._session.get(works_filter_url)
            response = self._handle_response_codes(response)
            works.extend(ArticleFactory.from_open_alex_query(response))

        return works

    def _handle_response_codes(self, response: Response) -> dict:
        # TODO: better error handling
        match response.status_code:
            case HTTPStatus.OK:
                return response.json()
            case _:
                raise Exception(response.status_code)
