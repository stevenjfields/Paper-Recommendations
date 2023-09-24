FROM nvidia/cuda:12.2.0-runtime-ubuntu20.04

RUN apt-get -y update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip

WORKDIR /code

COPY ./requirements-nvidia.txt /code/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

COPY /backend/ /code/

ENTRYPOINT ["python3", "main.py"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]