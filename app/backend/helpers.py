from backend.constants import COLLECTION_NAME, LOGGER_TITLE
from backend.pydantic_models.article import Article
from backend.pydantic_models.weighted_edge import WeightedEdge
from backend.utils.logger import AppLogger
from backend.utils.oag_bert_model import OAGBertModel
from backend.utils.milvus_client import MilvusClient

from typing import List
from pymilvus import utility, Collection
from cogdl.oag import oagbert
import torch
import asyncio
import numpy as np
import json

logger = AppLogger().get_logger()


def ids_to_query(ids: List[str]) -> str:
    ids_query = [f'"{work_id}"' for work_id in ids]
    return ", ".join(ids_query)


def create_embeddings(papers: List[Article]):
    milvus_client = MilvusClient()

    work_ids = [paper.work_id for paper in papers]
    db_response = milvus_client.query_by_work_ids(work_ids)

    logger.info(f"Works passed: {len(work_ids)}")
    logger.info(f"Unique works: {len(set(work_ids))}")

    ids_to_embed = set(work_ids)
    if len(db_response) > 0:
        ids_in_db = [item["work_id"] for item in db_response]
        logger.info(f"Works found in Milvus: {len(set(ids_in_db))}")
        ids_to_embed = list(set(ids_to_embed) - set(ids_in_db))

    # Leaving the code below just because this change caused like a 2x speedup during this function
    # https://media.giphy.com/media/2UCt7zbmsLoCXybx6t/giphy.gif
    # _, model = oagbert("oagbert-v2")

    if ids_to_embed:
        device, model = OAGBertModel().get_model()
        embeddings = list()
        embedded_papers = list()
    else:
        return

    embedded_ids = list()
    for paper in papers:
        if paper.work_id in ids_to_embed and paper.work_id not in embedded_ids:
            embedded_papers.append(paper)
            embedded_ids.append(paper.work_id)
            (
                input_ids,
                input_masks,
                token_type_ids,
                masked_lm_labels,
                position_ids,
                position_ids_second,
                masked_positions,
                num_spans,
            ) = model.build_inputs(
                title=paper.title,
                abstract=paper.get_abstract(),
                venue=paper.host_venue,
                authors=paper.authors,
                concepts=paper.concepts,
                affiliations=paper.affiliations,
            )

            _, pooled_output = model.bert.forward(
                input_ids=torch.LongTensor(input_ids).unsqueeze(0).to(device),
                token_type_ids=torch.LongTensor(token_type_ids).unsqueeze(0).to(device),
                attention_mask=torch.LongTensor(input_masks).unsqueeze(0).to(device),
                output_all_encoded_layers=False,
                checkpoint_activations=False,
                position_ids=torch.LongTensor(position_ids).unsqueeze(0).to(device),
                position_ids_second=torch.LongTensor(position_ids_second)
                .unsqueeze(0)
                .to(device),
            )

            pooled_normalized = torch.nn.functional.normalize(pooled_output, p=2, dim=1)
            embeddings.append(pooled_normalized.tolist()[0])

    milvus_client.insert_embedded_articles(embedded_papers, embeddings)


async def compute_similarities(target: Article, sources: List[Article]):
    milvus_client = MilvusClient()

    target_embeddings = milvus_client.query_by_work_id(target.work_id, ["embeddings"])[
        0
    ]["embeddings"]

    source_ids = [source.work_id for source in sources]
    results = milvus_client.query_by_work_ids(source_ids, ["embeddings"])

    sims = {}
    for result in results:
        work_id = result["work_id"]
        embeddings = result["embeddings"]

        sim = np.dot(target_embeddings, np.asarray(embeddings).T)
        sims[work_id] = sim

    return sims


async def get_similarities(
    root: Article, target: Article, sources: List[Article]
) -> List[WeightedEdge]:
    if root == target:
        root_sims = target_sims = await compute_similarities(root, sources)
    else:
        root_sims = asyncio.create_task(compute_similarities(root, sources))
        target_sims = asyncio.create_task(compute_similarities(target, sources))
        await asyncio.wait([root_sims, target_sims])
        root_sims = root_sims.result()
        target_sims = target_sims.result()

    concept_overlaps = {}
    author_overlaps = {}
    for source in sources:
        c_overlap = len(set(root.concepts) & set(source.concepts))
        a_overlap = len(set(root.authors) & set(source.authors))
        concept_overlaps[source.work_id] = float(c_overlap / len(root.concepts))
        author_overlaps[source.work_id] = float(a_overlap / len(root.authors))

    edges = []
    for source in sources:
        edges.append(
            WeightedEdge(
                target=target.work_id,
                source=source.work_id,
                weight=target_sims[source.work_id],
                root_weight=root_sims[source.work_id],
                concept_overlap=concept_overlaps[source.work_id],
                author_overlap=author_overlaps[source.work_id],
            )
        )

    return edges
