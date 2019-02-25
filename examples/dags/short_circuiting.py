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