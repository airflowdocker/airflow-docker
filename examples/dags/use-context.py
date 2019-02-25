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
    'use-context',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,
    concurrency=2,
)

with dag:
    use_context = Operator(
        task_id='use-context',
        image='airflowdocker/example-tasks:latest',
        provide_context=True,
        command=json.dumps([
            'use-context.py',
        ]),
    )
