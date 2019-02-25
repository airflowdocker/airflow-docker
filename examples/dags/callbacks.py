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
from datetime import datetime, timedelta
import json

from airflow import DAG

from airflow_docker.operator import Operator


def on_failure(context):
    operator = Operator(
        task_id='on_failure',
        image='bash',
        command=json.dumps([
            'echo', '"it failed"'
        ])
    )

    return operator.execute(context)


def on_success(context):
    operator = Operator(
        task_id='on_success',
        image='bash',
        command=json.dumps([
            'echo', '"it succeeded"'
        ])
    )

    return operator.execute(context)


def on_retried(context):
    operator = Operator(
        task_id='on_retry',
        image='bash',
        command=json.dumps([
            'echo', '"it is retrying"'
        ])
    )

    return operator.execute(context)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 10, 10),
    'retries': 0,
    'on_success_callback': on_success,
    'on_failure_callback': on_failure,
    'on_retry_callback': on_retried,
}

dag = DAG(
    'callbacks',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,
    concurrency=2,
)

with dag:
    success = Operator(
        task_id='success',
        image='hello-world:latest',
    )

    failure = Operator(
        task_id='failure',
        image='airflowdocker/example-tasks:latest',
        command=json.dumps([
           'failure.py',
        ]),
    )

    retry = Operator(
        task_id='will-fail-3-times',
        image='airflowdocker/example-tasks:latest',
        retries=2,
        retry_delay=timedelta(seconds=30),
        command=json.dumps([
            'failure.py',
        ]),
    )
