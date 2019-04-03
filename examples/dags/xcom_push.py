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

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2018, 10, 10),
}

dag = DAG("xcom_push", default_args=default_args, catchup=False, schedule_interval=None)


def callback(context):
    ti = context["task_instance"]
    result = ti.xcom_pull(
        dag_id="xcom_push", task_ids="default-xcom_push-callback", key="foo"
    )
    print("{} == {}".format(result, {"bar": "baz"}))

    result = ti.xcom_pull(
        dag_id="xcom_push", task_ids="default-xcom_push-callback", key="foo2"
    )
    print("{} == {}".format(result, {"bar2": "baz2"}))


with dag:
    xcom_push = Operator(
        task_id="default-xcom_push",
        image="airflowdocker/example-tasks:latest",
        command=json.dumps(["xcom_push.py"]),
        force_pull=False,
    )

    xcom_push_callback = Operator(
        task_id="default-xcom_push-callback",
        image="airflowdocker/example-tasks:latest",
        command=json.dumps(["xcom_push.py"]),
        force_pull=False,
        on_success_callback=callback,
    )
