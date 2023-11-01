from requests import Session, Response
import json
from http import HTTPStatus

class OpenAlexClient:
    def __init__(self):
        self._session = Session()
        self._base_url = "https://api.openalex.org"
        self._works_id_filter = "?filter=openalex_id:"

    def get_work(self, work_id: str) -> dict:
        get_work_url = f"{self._base_url}/works/{work_id}"
        response = self._session.get(get_work_url)


    def _handle_response(response: Response) -> dict:
        match response.status_code:
            case HTTPStatus.OK:
                return response.json()
            case _:
                raise Exception("Uh Oh")
