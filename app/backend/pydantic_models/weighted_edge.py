from pydantic import BaseModel
from typing import *


class WeightedEdge(BaseModel):
    target: str = ""
    source: str = ""
    weight: float = 0.0
    root_weight: float = 0.0
    concept_overlap: float = 0.0
    author_overlap: float = 0.0
