from .constants import COLLECTION_NAME
from .models import Article, WeightedEdge
from .milvus_schema import establish_connection

from typing import List
from pymilvus import utility, Collection
from cogdl.oag import oagbert
import torch
import asyncio
import numpy as np

def parse_article(result: str) -> Article:
    work_id = result["id"].split('/')[-1]
    title = result["title"]
    landing_page_url = result["primary_location"]["landing_page_url"] if result["primary_location"] else None
    inverted_abstract = result['abstract_inverted_index']
    authors = []
    host_venue = ""
    institutions = []

    for authorship in result['authorships']:
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

    concepts = [concept['display_name'] for concept in result['concepts'] if float(concept['score']) > 0.5]
    referenced_works = [work.split('/')[-1] for work in result['referenced_works']]
    related_works = [work.split('/')[-1] for work in result['related_works']]

    return Article(
        work_id=work_id,
        title=title if title else "",
        landing_page_url=landing_page_url if landing_page_url else "",
        inverted_abstract=inverted_abstract if inverted_abstract else {"": [0]},
        authors=authors,
        host_venue=host_venue if host_venue else "",
        affiliations=list(set(institutions)),
        concepts=concepts if concepts else [],
        references=referenced_works if referenced_works else [],
        related=related_works if related_works else []
    )

def ids_to_query(ids: List[str]) -> str:
    ids_query = [f'"{work_id}"' for work_id in ids]
    return ', '.join(ids_query)

def create_embeddings(papers: List[Article]):
    establish_connection()
    collection = Collection(COLLECTION_NAME)
    collection.load()

    work_ids = [paper.work_id for paper in papers]
    work_ids_query = ids_to_query(work_ids)
    db_response = collection.query(
        expr=f"work_id in [{work_ids_query}]",
        output_fields=["work_id"]
    )

    ids_to_embed = work_ids
    if len(db_response) > 0:
        ids_in_db = [item["work_id"] for item in db_response]
        ids_to_embed = list(set(ids_to_embed) - set(ids_in_db))


    _, model = oagbert("oagbert-v2")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    for paper in papers:
        if paper.work_id in ids_to_embed:
            input_ids, input_masks, token_type_ids, masked_lm_labels, position_ids, position_ids_second, masked_positions, num_spans = model.build_inputs(
            title=paper.title, 
            abstract=paper.get_abstract(), 
            venue=paper.host_venue, 
            authors=paper.authors, 
            concepts=paper.concepts, 
            affiliations=paper.affiliations
            )

            _, pooled_output = model.bert.forward(
                input_ids=torch.LongTensor(input_ids).unsqueeze(0).to(device),
                token_type_ids=torch.LongTensor(token_type_ids).unsqueeze(0).to(device),
                attention_mask=torch.LongTensor(input_masks).unsqueeze(0).to(device),
                output_all_encoded_layers=False,
                checkpoint_activations=False,
                position_ids=torch.LongTensor(position_ids).unsqueeze(0).to(device),
                position_ids_second=torch.LongTensor(position_ids_second).unsqueeze(0).to(device)
            )

            pooled_normalized = torch.nn.functional.normalize(pooled_output, p=2, dim=1)

            collection.insert([
                [paper.work_id], 
                [pooled_normalized.tolist()[0]]
            ])
    
    collection.flush() # allows inserted data to be indexed

async def compute_similarities(target: Article, sources: List[Article]):
    establish_connection()
    collection = Collection(COLLECTION_NAME)

    target_embeddings = collection.query(
        expr = f'work_id == "{target.work_id}"',
        output_fields=['embeddings']
    )[0]['embeddings']

    source_ids = [source.work_id for source in sources]
    source_id_query = ids_to_query(source_ids)

    results = collection.query(
        f'work_id in [{source_id_query}]',
        output_fields=["work_id", "embeddings"],
    )

    sims = {}
    for result in results:
        work_id = result["work_id"]
        embeddings = result["embeddings"]

        sim = np.dot(target_embeddings, np.asarray(embeddings).T)
        sims[work_id] = sim

    return sims


async def get_similarities(root: Article, target: Article, sources: List[Article]) -> List[WeightedEdge]:
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
                author_overlap=author_overlaps[source.work_id]
            )
        )
    
    return edges
