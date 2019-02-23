FROM python:3.6.6-alpine

RUN pip install airflow-docker-helper

WORKDIR /usr/local/lib/airflow-docker/scripts
COPY scripts/ .

ENTRYPOINT ["python"]
