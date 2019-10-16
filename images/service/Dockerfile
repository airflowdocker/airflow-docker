FROM python:3.6.6

ENV AIRFLOW_HOME=/airflow
ENV SLUGIFY_USES_TEXT_UNIDECODE=yes

RUN set -ex \
    # Install docker client
    && wget -q https://download.docker.com/linux/static/stable/x86_64/docker-18.03.1-ce.tgz \
    && tar xzvf docker-18.03.1-ce.tgz \
    && cp docker/docker /usr/bin/ \
    && rm docker-18.03.1-ce.tgz \
    && rm -rf docker \
    # Prep an airflow user
    && useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow \
    && chown -R airflow: ${AIRFLOW_HOME} \
    && chmod -R 775 ${AIRFLOW_HOME}

WORKDIR /tmp-install
COPY deps/requirements.txt ./

RUN set -ex \
    && pip install --no-cache-dir -r requirements.txt

COPY dist/airflow_docker-0.4.2-py2.py3-none-any.whl .
RUN pip install airflow_docker-0.4.2-py2.py3-none-any.whl

# Set Up defaults for running the container
USER airflow
WORKDIR /airflow
COPY airflow.cfg ./
# Ports for the webserver, flower, and the worker log server
EXPOSE 8080 5555 8793
ENTRYPOINT ["airflow"]
