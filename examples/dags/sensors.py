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

from airflow_docker.operator import Sensor, Operator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2018, 10, 10),
}

dag = DAG(
    'sensors',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,
    concurrency=2,
)

with dag:
    polling_sensor = Sensor(
        task_id='polling-sensor',
        image='airflowdocker/example-tasks:latest',
        command=json.dumps([
            'sensor.py',
        ]),
    )
    will_run_eventually = Operator(
        task_id='will-run-eventually',
        image='hello-world',
    )
    will_run_eventually.set_upstream(polling_sensor)


    rescheduled_sensor = Sensor(
        task_id='rescheduled-sensor',
        image='airflowdocker/example-tasks:latest',
        poke_interval=45,
        mode='reschedule',
        command=json.dumps([
            'sensor.py',
        ]),
    )
    will_run_eventually_too = Operator(
        task_id='will-run-eventually-too',
        image='hello-world',
    )
    will_run_eventually_too.set_upstream(rescheduled_sensor)


    hard_fail_sensor = Sensor(
        task_id='hard-fail-sensor',
        image='airflowdocker/example-tasks:latest',
        poke_interval=60,
        mode='reschedule',
        soft_fail=False,
        timeout=30,
        command=json.dumps([
            "sensor.py", "FAIL",
        ]),
    )

    upstream_failed = Operator(
        task_id='upstream-failed',
        image='hello-world',
    )
    upstream_failed.set_upstream(hard_fail_sensor)


    soft_fail_sensor = Sensor(
        task_id='soft-fail-sensor',
        image='airflowdocker/example-tasks:latest',
        poke_interval=60,
        mode='reschedule',
        soft_fail=True,
        timeout=30,
        command=json.dumps([
            "sensor.py", "FAIL",
        ]),
    )

    skipped = Operator(
        task_id='skipped',
        image='hello-world',
    )
    skipped.set_upstream(soft_fail_sensor)
