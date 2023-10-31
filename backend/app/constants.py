
LOGGER_NAME = "paper_recommender"

BASE_WORKS_URL = "https://api.openalex.org/works"
WORKS_ID_FILTER = "?filter=openalex_id:"

COLLECTION_NAME = 'Article_Vectors'

DEV_SETTINGS = {
    "server_settings": {
        "host": "0.0.0.0",
        "port": 8080,
        "reload": True
    }
}

PROD_SETTINGS = {
    "server_settings": {
        "host": "0.0.0.0",
        "port": 8080,
        "workers": 8
    }
}

SETTINGS = {
    "dev": DEV_SETTINGS,
    "prod": PROD_SETTINGS
}