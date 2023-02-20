
# FastAPI Backend for Independent Study

A few of these endpoints simply act as proxies to the OpenAlex dataset, except they only return the data relevant to my current project. Before running, make sure you have a Milvus instance running. The docker file for Milvus can be found in this project in the root docker folder.

To run in CLI run the following command from this folder:
`python main.py`

To run from the debugger in VS Code run the main.py file from the debugger menu.

To view the docs, run the server and visit http://127.0.0.1:8080/docs/