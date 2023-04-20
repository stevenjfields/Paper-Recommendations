# Independent Study: Recommending Papers based on similarity metrics
This repo contains my work for an independent study in place of my capstone course for a master's in data science from Indiana University. The aim of the study is to try and recommend papers to read relevant to research you want to read in order to fill in any knowledge gaps you may have.

## Tech Stack
* Backend: Python's FastAPI
* Frontend: Javascript and Helios-web
* PyTorch, OAG-Bert, and Milvus for creating and storing embeddings.

## Local Setup: Milvus
In order to get a local standalone version of Milvus up and running, run the following docker-compose command:

`docker-compose -f ./docker/docker-compose.milvus.yml up`

Then to shut the servers down simply run the following:

`docker-compose -f ./docker/docker-compose.milvus.yml down`

## Local Setup: Web App
To run the webserver, you'll need python 3.6+ installed, and to install the `requirements.txt` file. This can be done with the following command:

`pip install -r requirements.txt`

To run the web app, run the following command from the backend folder:

`python main.py`

To shut down the server use `Ctrl + C`.

