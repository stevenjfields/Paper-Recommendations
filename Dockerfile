FROM python:3.8

WORKDIR /app
COPY /app/ /app/

RUN apt-get -y update
RUN apt-get -y install python3 python3-pip curl ca-certificates
RUN pip3 install poetry==1.5.0 requests==2.29.0 certifi && \
    poetry config installer.max-workers 10 && \
    poetry install

ENTRYPOINT ["poetry", "run", "python", "main.py"]