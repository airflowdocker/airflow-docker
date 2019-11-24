FROM python:3.6.6-alpine

RUN pip install airflow-docker-helper

WORKDIR /usr/local/lib/airflow-docker
COPY scripts/ scripts
COPY code/ code

WORKDIR /usr/local/lib/airflow-docker/scripts

ENV PYTHONPATH /usr/local/lib/airflow-docker/code
ENTRYPOINT ["python"]
