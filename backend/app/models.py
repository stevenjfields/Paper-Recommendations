from pydantic import BaseModel
from typing import Dict, List, Optional

class Article(BaseModel):
    # Keeping track of some needed paper details
    work_id: str
    title: str = ""
    inverted_abstract: Dict[str, List[int]] = {"": [0]}
    authors: List[str] = []
    host_venue: str = ""
    affiliations: List[str] = []
    concepts: List[str] = []
    references: List[str] = []
    related: List[str] = []

    def get_abstract(self) -> str:
        abstract = dict()
        for k, v in self.inverted_abstract.items():
            for i in v:
                abstract[i] = k

        final = ""
        for i in sorted(abstract.keys()):
            final += abstract[i] + " "
        return final
    
    def fetch_references_queries(self):
        # open alex only allows 50 OR joins per request
        queries = list()
        for i in range(0, len(self.references), 50):
            queries.append('|'.join(self.references[i:i+50]))
        return queries
    
    def fetch_related_queries(self):
        # open alex only allows 50 OR joins per request
        queries = list()
        for i in range(0, len(self.related), 50):
            queries.append('|'.join(self.related[i:i+50]))
        return queries
    
    def __str__(self):
        return f"{self.id}: {self.title}\n{self.get_abstract()}"
    
class WeightedEdge(BaseModel):
    target: str = ""
    source: str = ""
    weight: float = 0.0