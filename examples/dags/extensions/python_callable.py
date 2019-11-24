# -*- coding: utf-8 -*-
#
#     Copyright 2019 Contributing Authors
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
from airflow import DAG

from airflow_docker.operator import Operator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 10, 10),
    'retries': 0,
}

dag = DAG(
    'python-callable',
    default_args=default_args,
    schedule_interval=None,
)

with dag:
    no_context = Operator(
        task_id='call-python-callable-no-context',
        image='airflowdocker/example-tasks:latest',
        python_callable="call:call_me",
        op_args=[
            'foo',
            'bar',
        ],
        op_kwargs={
            'integer': 1,
            'float': 2.0,
            'bool': True,
            'nested': [
                'foo',
                'baz',
            ],
        },
    )

    use_context = Operator(
        task_id='call-python-callable-with-context',
        image='airflowdocker/example-tasks:latest',
        provide_context=True,
        python_callable="call:call_me",
    )

    xcom_push = Operator(
        task_id='call-python-callable-xcom-push',
        image='airflowdocker/example-tasks:latest',
        python_callable="xcom:push",
        op_kwargs={
            "data_to_push": [
                "this",
                "that",
            ]
        }
    )

    xcom_pull = Operator(
        task_id='call-python-callable-xcom-pull',
        image='airflowdocker/example-tasks:latest',
        python_callable="xcom:pull",
        op_args=[
            "{{ task_instance.xcom_pull(task_ids='call-python-callable-xcom-push') | tojson }}"
        ]
    )
    xcom_pull.set_upstream(xcom_push)

