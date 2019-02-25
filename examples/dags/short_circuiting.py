from datetime import datetime
import json

from airflow import DAG

from airflow_docker.operator import Operator, ShortCircuitOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 10, 10),
    'retries': 0,
}

dag = DAG(
    'short-circuit',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,
    concurrency=2,
)

####################################################################################################
#
# Short Circuit
#
####################################################################################################
will_short_circuit = ShortCircuitOperator(
    task_id='will-short-circuit',
    image='airflowdocker/example-tasks:latest',
    command=json.dumps([
        "short_circuit.py", "SHORT-CIRCUIT"
    ]),
    dag=dag,
)

wont_run = Operator(
    task_id='wont-run',
    image='hello-world:latest',
    dag=dag,
)
wont_run.set_upstream(will_short_circuit)

####################################################################################################
#
# Don't Short Circuit
#
####################################################################################################
wont_short_circuit = ShortCircuitOperator(
    task_id='wont-short-circuit',
    image='airflowdocker/example-tasks:latest',
    command=json.dumps([
       "short_circuit.py",
    ]),
    dag=dag,
)

will_run = Operator(
    task_id='will-run',
    image='hello-world:latest',
    dag=dag,
)
will_run.set_upstream(wont_short_circuit)