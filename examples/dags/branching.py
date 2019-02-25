from datetime import datetime
import json

from airflow import DAG

from airflow_docker.operator import Operator, BranchOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 10, 10),
    'retries': 0,
}

dag = DAG(
    'branching',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,
    concurrency=2,
)


####################################################################################################
#
# Branch First
#
####################################################################################################
branch_first = BranchOperator(
    task_id='branch-first',
    image='airflowdocker/example-tasks:latest',
    command=json.dumps([
        'branch.py', 'first'
    ]),
    dag=dag,
)

first = Operator(
    task_id='first',
    image='hello-world:latest',
    dag=dag,
)
first.set_upstream(branch_first)

wont_run_2 = Operator(
    task_id='wont-run-2',
    image='hello-world:latest',
    dag=dag,
)
wont_run_2.set_upstream(branch_first)

####################################################################################################
#
# Branch Second
#
####################################################################################################
branch_second = BranchOperator(
    task_id='branch-second',
    image='airflowdocker/example-tasks:latest',
    command=json.dumps([
        'branch.py', 'second'
    ]),
    dag=dag,
)
wont_run_3 = Operator(
    task_id='wont-run-3',
    image='hello-world:latest',
    dag=dag,
)
wont_run_3.set_upstream(branch_second)
second = Operator(
    task_id='second',
    image='hello-world:latest',
    dag=dag,
)
second.set_upstream(branch_second)