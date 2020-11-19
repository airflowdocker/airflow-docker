FROM airflowdocker/service:latest

COPY airflow.cfg ./

USER root

RUN pip install --no-cache-dir pytest>=6 && \
    airflow initdb

COPY pyproject.toml .
COPY tests ./tests

ENTRYPOINT ["pytest"]
CMD ["-vvv"]
