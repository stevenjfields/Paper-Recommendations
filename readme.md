# Independent: Recommending Papers based on similarity metrics
This repo contains my work for an independent study in place of my capstone course for a master's in data science from Indiana University. The aim of the study is to try and recommend papers to read relevant to research you plan to read.

## Local Setup: Milvus
In order to get a local standalone version of Milvus up and running, run the following docker-compose command:

`docker-compose -f ./docker/docker-compose.milvus.yml up`

Then to shut the servers down simply run the following:

`docker-compose -f ./docker/docker-compose.milvus.yml down`