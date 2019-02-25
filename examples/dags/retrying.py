from datetime import datetime, timedelta
import json
from airflow import DAG

from airflow_docker.operator import Operator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 10, 10),
    'retries': 2,
    'retry_delay': timedelta(seconds=30),
}

dag = DAG(
    'retrying',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,
    concurrency=2,
)

with dag:
    default_retry = Operator(
        task_id='default-retry',
        image='airflowdocker/example-tasks:latest',
        command=json.dumps([
            'failure.py',
        ]),
    )

    overridden_retry = Operator(
        task_id='overridden-retry',
        image='airflowdocker/example-tasks:latest',
        retries=1,
        retry_delay=timedelta(seconds=20),
        command=json.dumps([
            'failure.py',
        ]),
    )
