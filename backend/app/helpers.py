from .constants import COLLECTION_NAME
from .models import Article, WeightedEdge
from .milvus_schema import establish_connection

from typing import List
from pymilvus import utility, Collection
from cogdl.oag import oagbert
import torch

def parse_article(result: str) -> Article:
    work_id = result["id"].split('/')[-1]
    title = result["title"]
    inverted_abstract = result['abstract_inverted_index']
    authors = [authorship['author']['display_name'] for authorship in result['authorships']]
    host_venue = result['host_venue']['publisher']
    institutions = list()

    for authorship in result['authorships']:
        for institution in authorship['institutions']: 
            if institution['display_name'] not in institutions:
                institutions.append(institution['display_name'])

    concepts = [concept['display_name'] for concept in result['concepts'] if float(concept['score']) > 0.5]
    referenced_works = [work.split('/')[-1] for work in result['referenced_works']]
    related_works = [work.split('/')[-1] for work in result['related_works']]

    return Article(
        work_id=work_id,
        title=title if title else "",
        inverted_abstract=inverted_abstract if inverted_abstract else {"": [0]},
        authors=authors if authors else [],
        host_venue=host_venue if host_venue else "",
        affiliations=institutions if institutions else [],
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
                input_ids=torch.LongTensor(input_ids).unsqueeze(0),
                token_type_ids=torch.LongTensor(token_type_ids).unsqueeze(0),
                attention_mask=torch.LongTensor(input_masks).unsqueeze(0),
                output_all_encoded_layers=False,
                checkpoint_activations=False,
                position_ids=torch.LongTensor(position_ids).unsqueeze(0),
                position_ids_second=torch.LongTensor(position_ids_second).unsqueeze(0)
            )

            pooled_normalized = torch.nn.functional.normalize(pooled_output, p=2, dim=1)

            collection.insert([
                [paper.work_id], 
                [pooled_normalized.tolist()[0]]
            ])
    
    collection.flush() # allows inserted data to be indexed

def get_similarities(target: Article, sources: List[Article]) -> List[WeightedEdge]:
    establish_connection()
    collection = Collection(COLLECTION_NAME)
    collection.load()

    target_embeddings = collection.query(
        expr = f'work_id == "{target.work_id}"',
        output_fields=['embeddings']
    )[0]['embeddings']

    source_ids = [source.work_id for source in sources]
    source_id_query = ids_to_query(source_ids)

    search_params = {"metric_type": "IP", "params": {"nprobe": 10}, "offset": 5}

    results = collection.search(
        data=[target_embeddings],
        anns_field="embeddings",
        param=search_params,
        limit=len(sources),
        expr=f"work_id in [{source_id_query}]",
        consistency_level="Strong"
    )

    ids, distances = results[0].ids, results[0].distances
    results = zip(ids, distances)

    edges = []
    for result in results:
        edges.append(
            WeightedEdge(
                target=target.work_id,
                source=result[0],
                weight=result[1]
            )
        )
    
    collection.release() # frees memory from collection.load()
    return edges
