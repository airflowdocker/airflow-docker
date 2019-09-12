FROM airflowdocker/service:latest

COPY airflow.cfg ./

USER root

RUN pip install --no-cache-dir pytest && \
    airflow initdb

COPY tests ./tests

ENTRYPOINT ["pytest"]
CMD ["-vvv"]
