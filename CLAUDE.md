# CLAUDE.md — Paper Recommendations

Comprehensive guide for AI assistants working in this repository.

---

## Project Overview

An academic paper recommendation web application built as a master's capstone at Indiana University. Given a paper title, it recursively fetches references to a configurable depth, computes semantic similarity using OAG-BERT embeddings, and renders an interactive 3D graph showing paper relationships.

**Core idea**: Two similarity metrics per edge — `weight` (similarity to immediate parent) and `root_weight` (similarity to the root/seed paper) — are averaged to size graph nodes.

---

## Repository Layout

```
Paper-Recommendations/
├── readme.md                    # Project overview and setup guide
├── Dockerfile                   # CPU-only build (Python 3.11)
├── Dockerfile-nvidia            # GPU-enabled build (CUDA 12.2.2 / Ubuntu 22.04)
├── docker-compose.yml           # Full stack: etcd + MinIO + Milvus + app
├── scrape_data.py               # One-off script: scrape OpenAlex → TSV
├── Paper_Trail.ipynb            # Prototype / exploration notebook
├── Paper_Trail_Milvus.ipynb     # Milvus integration exploration notebook
├── images/                      # Example visualisation screenshots
└── app/                         # All runnable application code lives here
    ├── main.py                  # Entry point — initialises Milvus schema, starts uvicorn
    ├── pyproject.toml           # Poetry dependency manifest
    ├── poetry.lock              # Locked dependency tree
    ├── log_config.ini           # Python logging configuration (dictConfig format)
    ├── frontend/
    │   ├── index.html           # Jinja2 template (Bootstrap 5.3 + Helios-web + D3)
    │   └── resources/
    │       ├── index.css
    │       └── javascript/
    │           ├── globals.js       # Shared state and constants
    │           ├── autocomplete.js  # OpenAlex autocomplete search
    │           └── visualization.js # Data orchestration + 3D graph rendering
    └── backend/
        ├── api.py               # FastAPI route definitions
        ├── constants.py         # App-wide constants and environment settings
        ├── helpers.py           # Embedding creation + similarity computation
        ├── pydantic_models/
        │   ├── article.py       # Article model + ArticleFactory
        │   └── weighted_edge.py # Graph edge model
        └── utils/
            ├── logger.py        # Rich-formatted AppLogger singleton
            ├── singleton.py     # Thread-safe singleton metaclass
            ├── milvus_client.py # Milvus connection, schema, query, insert
            ├── open_alex_client.py # OpenAlex REST API wrapper
            └── oag_bert_model.py   # OAG-BERT singleton (GPU-aware)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI 0.94+ |
| ASGI server | uvicorn 0.21 |
| Embeddings | OAG-BERT v2 via cogdl 0.6 |
| Deep learning | PyTorch 1.13+ |
| Vector database | Milvus 2.3 (standalone) |
| Milvus storage | etcd v3.5.5 + MinIO |
| Python deps | Poetry (python ^3.10) |
| Console output | Rich 13.6 |
| Frontend render | Jinja2 3.x |
| 3D visualisation | Helios-web 0.7.0 |
| Colour scales | D3.js v7 |
| Paper data source | OpenAlex API (public, no auth required) |
| Containerisation | Docker / Docker Compose |

---

## Running the Application

All commands are run from the repository root.

### With Docker (recommended)

```bash
# CPU only
sudo docker compose -f docker-compose.yml run --service-ports paper-recommendations

# With NVIDIA GPU acceleration
sudo docker compose -f docker-compose.yml run --service-ports paper-recommendations-nvidia

# Tear down all services
sudo docker compose -f docker-compose.yml down
```

### Without Docker (local development)

Prerequisites: Milvus running on `localhost:19530`.

```bash
cd app
poetry install
poetry run python main.py
```

The server starts on **http://0.0.0.0:8080**.
FastAPI interactive docs: **http://127.0.0.1:8080/docs/**

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_ENV` | `dev` | `dev` (reload, debug) or `prod` (8 workers, info logging) |
| `MILVUS_ADDRESS` | `localhost:19530` | Milvus gRPC address (`host:port`) |

---

## API Endpoints

Defined in `app/backend/api.py`.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Serve frontend HTML via Jinja2 |
| `GET` | `/paper/{work_id}/` | Fetch one paper (Milvus first, OpenAlex fallback) |
| `POST` | `/references/` | Fetch all references for an `Article` body |
| `POST` | `/embeddings/` | Create + store OAG-BERT embeddings for a list of articles |
| `POST` | `/similarities/` | Compute `WeightedEdge` list for a root/target/sources triple |

CORS is open to all origins (`*`). Static assets are mounted at `/static/`.

---

## Data Models

### `Article` (`app/backend/pydantic_models/article.py`)

```python
work_id: str               # OpenAlex work ID, e.g. "W2963403868"
title: str
landing_page_url: str
inverted_abstract: Optional[Dict[str, List[int]]]  # OpenAlex inverted-index format
authors: List[str]
host_venue: str
affiliations: List[str]
concepts: List[str]        # Only concepts with score > 0.5
references: List[str]      # Referenced work IDs
related: List[str]         # Related work IDs
```

`get_abstract()` reconstructs plain text from the inverted index.

`ArticleFactory` has three static constructors:
- `from_open_alex_response(result)` — single API result dict
- `from_open_alex_query(query_response)` — batch API response
- `from_milvus_query(milvus_response)` — list of Milvus row dicts

### `WeightedEdge` (`app/backend/pydantic_models/weighted_edge.py`)

```python
target: str           # Parent work_id
source: str           # Child work_id
weight: float         # Cosine sim(target_embedding, source_embedding)
root_weight: float    # Cosine sim(root_embedding, source_embedding)
concept_overlap: float  # |root.concepts ∩ source.concepts| / |root.concepts|
author_overlap: float   # |root.authors ∩ source.authors| / |root.authors|
```

---

## Core Logic

### Embedding Pipeline (`app/backend/helpers.py`)

1. `create_embeddings(papers)` — skips papers already in Milvus, runs OAG-BERT on the remainder, inserts results.
2. OAG-BERT inputs: `title`, `abstract` (reconstructed), `venue`, `authors`, `concepts`, `affiliations`.
3. Output: L2-normalised 768-dimensional float vector.
4. Stored in Milvus collection `Work_Embeddings`.

### Similarity Computation (`app/backend/helpers.py`)

- `compute_similarities(target, sources)` — inner product (dot product) of normalised embeddings = cosine similarity.
- `get_similarities(root, target, sources)` — runs root and target similarity computations concurrently via `asyncio`, then assembles `WeightedEdge` objects.
- When `root == target`, only one similarity pass is needed.

### Vector Database (`app/backend/utils/milvus_client.py`)

- Collection: `Work_Embeddings`
- Index: `IVF_FLAT`, metric `IP` (Inner Product), `nlist=1`
- Primary key: `work_id` (VARCHAR 32)
- Embeddings field: `FLOAT_VECTOR` dim=768
- Array fields: `authors`, `affiliations`, `concepts`, `references`, `related`

### Frontend Data Flow (`app/frontend/resources/javascript/visualization.js`)

1. User selects a paper and depth (2–5).
2. `getReferencesToDepth()` recursively calls `POST /references/` for each level.
3. `createEmbeddings()` batches all papers to `POST /embeddings/`.
4. `getSimilarities()` calls `POST /similarities/` for each parent/child relationship.
5. Helios-web renders the resulting graph; node size = `avg(weight, root_weight) × parent_size` (root fixed at 1).

**Rate limiting**: `CONCURRENCY_LIMIT = 1` in `globals.js` — OpenAlex allows 10 req/s; the frontend is intentionally conservative.

**Default seed paper**: `W2963403868` ("Attention Is All You Need").

---

## Singletons

`AppLogger`, `MilvusClient`, and `OAGBertModel` all use the thread-safe `Singleton` metaclass in `app/backend/utils/singleton.py`. Do not instantiate these with `new` logic expecting fresh state — they return the same instance after the first call.

The OAG-BERT model auto-detects CUDA. The `oagbert-v2` variant (not `-sim`) is used deliberately to produce lower raw similarity scores with better spread.

---

## Logging

- Logger name: `paper_recommender` (constant `LOGGER_TITLE`).
- Retrieve via `AppLogger().get_logger()`.
- Console output uses Rich with 100–200 char width; colours are per-logger (blue for app, yellow for uvicorn access, red for uvicorn errors).
- Config file: `app/log_config.ini`.

---

## Dependency Management

```bash
cd app

# Install all dependencies
poetry install

# Add a new dependency
poetry add <package>

# Update lock file
poetry lock
```

Do not edit `poetry.lock` by hand. Poetry 1.5.0 is pinned in the Dockerfiles.

---

## Docker Compose Services

| Service | Image | Ports |
|---|---|---|
| `milvus-etcd` | `quay.io/coreos/etcd:v3.5.5` | internal |
| `milvus-minio` | `minio/minio:RELEASE.2023-03-13T19-46-17Z` | 9000, 9001 |
| `milvus-standalone` | `milvusdb/milvus:v2.3.2` | 19530, 9091 |
| `paper-recommendations` | built from `Dockerfile` | 8080 |
| `paper-recommendations-nvidia` | built from `Dockerfile-nvidia` | 8080 |

MinIO default credentials: `minioadmin / minioadmin`.
App volume mount: `./app:/app` — code changes are reflected without rebuilding.

---

## No Test Suite

There are no automated tests. Exploration and validation were done via:
- `Paper_Trail.ipynb` — initial prototyping
- `Paper_Trail_Milvus.ipynb` — Milvus integration experiments
- FastAPI's built-in `/docs` interface for manual API testing

When adding tests, place them in `app/tests/` and use `pytest`.

---

## Key Conventions

- **All Python code lives under `app/`**; the repo root contains only Docker/config files.
- **Imports are relative to `app/`** — run from there (`poetry run python main.py`).
- **Factory pattern** for model construction: use `ArticleFactory` methods, not the `Article` constructor directly from raw API data.
- **Milvus insert order matters**: columns must be passed as a list in the exact schema field order (see `milvus_client.py:144`).
- **Abstract reconstruction**: always use `article.get_abstract()` — never access `inverted_abstract` directly.
- **Concepts filter**: only concepts with `score > 0.5` are stored (applied in `ArticleFactory.from_open_alex_response`).
- **`inverted_abstract` is not stored in Milvus** — set to `{}` when reconstructing from DB (`from_milvus_query`).
- **Environment detection**: `APP_ENV=dev` (default) enables hot-reload; `APP_ENV=prod` uses 8 workers.
