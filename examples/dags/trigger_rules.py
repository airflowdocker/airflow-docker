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
from airflow.operators.dummy_operator import DummyOperator
from airflow_docker.operator import Operator
from airflow.utils.trigger_rule import TriggerRule



default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 10, 10),
    'retries': 0,
}

dag = DAG(
    'trigger-rules',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,
    concurrency=3,
)


with dag:
    not_actually_dependent = Operator(
        task_id='no-actually-dependant',
        image='bash:latest',
        command=json.dumps([
            'sleep', '15',
        ]),
    )

    just_for_show = DummyOperator(
        task_id='just-for-show',
        trigger_rule=TriggerRule.DUMMY,
    )
    just_for_show.set_upstream(not_actually_dependent)

    eventually_run = Operator(
        task_id='eventually-run',
        image='hello-world:latest',
    )
    eventually_run.set_upstream(just_for_show)


    success = Operator(
        task_id='success',
        image='bash:latest',
        command=json.dumps([
            'sleep', '60',
        ]),
    )
    success.set_upstream(eventually_run)

    success_too = Operator(
        task_id='success-too',
        image='bash:latest',
        command=json.dumps([
            'sleep', '10',
        ]),
    )
    success_too.set_upstream(eventually_run)

    failure = Operator(
        task_id='failure',
        image='airflowdocker/example-tasks:latest',
        command=json.dumps([
            'failure.py', 'FAIL',
        ]),
    )
    failure.set_upstream(eventually_run)

    one_failed = Operator(
        task_id='one-failed',
        image='hello-world:latest',
        trigger_rule=TriggerRule.ONE_FAILED,
    )
    one_failed.set_upstream([
        success,
        failure,
    ])

    one_success = Operator(
        task_id='one-success',
        image='hello-world:latest',
        trigger_rule=TriggerRule.ONE_SUCCESS,
    )
    one_success.set_upstream([
        success, success_too,
    ])

    all_success = Operator(
        task_id='all-success',
        image='hello-world:latest',
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )
    all_success.set_upstream([
        success, success_too,
    ])
