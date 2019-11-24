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
import airflow_docker_helper

META_PATH_DIR = airflow_docker_helper.META_PATH_DIR
"""This is the legacy subdirectory where airflow-docker run time files used to live."""

CONTAINER_RUN_DIR = "/var/run/airflow-docker"
"""The current reserved run time directory, mounted as a volume in running containers."""

BRANCH_OPERATOR_FILENAME = airflow_docker_helper.BRANCH_OPERATOR_FILENAME
"""The non-python callable filename for the branch operator result."""

SHORT_CIRCUIT_OPERATOR_FILENAME = airflow_docker_helper.SHORT_CIRCUIT_OPERATOR_FILENAME
"""The non-python callable filename for the branch operator result."""

SENSOR_OPERATOR_FILENAME = airflow_docker_helper.SENSOR_OPERATOR_FILENAME
"""The non-python callable filename for the sensor operator result."""

CONTEXT_FILENAME = airflow_docker_helper.CONTEXT_FILENAME
"""The filename for the serialized context info."""

XCOM_PUSH_FILENAME = airflow_docker_helper.XCOM_PUSH_FILENAME
"""The filename for runtime xcom pushed data."""

RESULT_FILENAME = "result.json"
"""The python callable filename for the return result."""
