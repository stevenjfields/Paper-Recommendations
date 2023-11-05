from pydantic import BaseModel, Field
from typing import *
from backend.utils.logger import AppLogger

logger = AppLogger().get_logger()


class Article(BaseModel):
    work_id: str
    title: str = ""
    landing_page_url: str = ""
    inverted_abstract: Optional[Dict[str, List[int]]] = None
    authors: List[str] = []
    host_venue: str = ""
    affiliations: List[str] = []
    concepts: List[str] = []
    references: List[str] = []
    related: List[str] = []

    def get_abstract(self) -> str:
        if not self.inverted_abstract:
            return ""

        abstract = dict()
        for k, v in self.inverted_abstract.items():
            for i in v:
                abstract[i] = k

        final = ""
        for i in sorted(abstract.keys()):
            final += abstract[i] + " "
        return final

    def __str__(self):
        return f"{self.work_id}: {self.title}\n{self.get_abstract()}"


class ArticleFactory:
    @staticmethod
    def from_open_alex_response(result: dict) -> Article:
        work_id = result["id"].split("/")[-1]
        title = result["title"]
        landing_page_url = (
            result["primary_location"]["landing_page_url"]
            if result["primary_location"]
            else None
        )
        inverted_abstract = result["abstract_inverted_index"]
        authors = []
        host_venue = ""
        institutions = []

        for authorship in result["authorships"]:
            author = authorship.get("author", None)
            institutes = authorship.get("institutions", None)
            if author:
                name = author.get("display_name", None)
                if name:
                    authors.append(name)
            if institutes:
                for institute in institutes:
                    institution = institute.get("display_name", None)
                    if institution:
                        institutions.append(institution)

        concepts = [
            concept["display_name"]
            for concept in result["concepts"]
            if float(concept["score"]) > 0.5
        ]
        referenced_works = [work.split("/")[-1] for work in result["referenced_works"]]
        related_works = [work.split("/")[-1] for work in result["related_works"]]

        try:
            return Article(
                work_id=work_id,
                title=title if title else "",
                landing_page_url=landing_page_url if landing_page_url else "",
                inverted_abstract=inverted_abstract if inverted_abstract else {"": [0]},
                authors=authors if authors else [],
                host_venue=host_venue if host_venue else "",
                affiliations=list(set(institutions)),
                concepts=concepts if concepts else [],
                references=referenced_works if referenced_works else [],
                related=related_works if related_works else [],
            )
        except Exception as e:
            logger.exception(e)
            logger.info(result)

    @staticmethod
    def from_open_alex_query(query_response):
        articles = []
        for paper in query_response["results"]:
            try:
                article = ArticleFactory.from_open_alex_response(paper)
                articles.append(article)
            except Exception as e:
                logger.exception(e)
                logger.debug(paper)

        return articles

    @staticmethod
    def from_milvus_query(milvus_response: List[dict]) -> List[Article]:
        articles = list()
        for item in milvus_response:
            try:
                articles.append(Article(**item, inverted_abstract={}))
            except Exception as e:
                logger.exception(e)
        return articles
