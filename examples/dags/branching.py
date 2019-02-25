# -*- coding: utf-8 -*-
#
#     Copyright 2019 Hunter Senft-Grupp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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