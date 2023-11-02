from requests import Session, Response
import json
from http import HTTPStatus

class OpenAlexClient:
    _base_url = "https://api.openalex.org"
    _works_id_filter = "?filter=openalex_id:"

    def __init__(self):
        self._session = Session()

    def get_work_by_id(self, work_id: str) -> dict:
        get_work_url = f"{self._base_url}/works/{work_id}"
        response = self._session.get(get_work_url)
        return self._handle_response(response)
    
    def get_works_by_filter(self, query: str):
        works_filter_url = f"{self._base_url}/works{self._works_id_filter}{query}"
        response = self._session.get(works_filter_url)
        return self._handle_response(response)


    def _handle_response(self, response: Response) -> dict:
        # TODO: better error handling
        match response.status_code:
            case HTTPStatus.OK:
                return response.json()
            case _:
                raise Exception(response.status_code)
