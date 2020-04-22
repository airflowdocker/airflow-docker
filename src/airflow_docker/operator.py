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
#
# NOTICE: The code in this file is derived from the apache-airflow project
#         and has been modified to suit the needs of this project. Below is
#         the original copyright notice.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import ast
import json
from tempfile import TemporaryDirectory
from typing import Dict, Iterable, List, Optional, Union

import airflow.configuration as conf
import airflow_docker_helper
from airflow.exceptions import AirflowConfigException, AirflowException
from airflow.models import SkipMixin
from airflow.providers.docker.hooks.docker import DockerHook
from airflow.providers.docker.operators.docker import (
    DockerOperator as AirflowDockerOperator,
)
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from docker import APIClient, tls

from airflow_docker.conf import get_boolean_default, get_default
from airflow_docker.ext import delegate_to_extensions, register_extensions
from airflow_docker.utils import get_config


class ShortCircuitMixin(SkipMixin):
    def execute(self, context):
        condition = super(ShortCircuitMixin, self).execute(context)
        self.log.info("Condition result is %s", condition)

        if condition:
            self.log.info("Proceeding with downstream tasks...")
            return

        self.log.info("Skipping downstream tasks...")

        downstream_tasks = context["task"].get_flat_relatives(upstream=False)
        self.log.debug("Downstream task_ids %s", downstream_tasks)

        if downstream_tasks:
            self.skip(
                context["dag_run"], context["ti"].execution_date, downstream_tasks
            )

        self.log.info("Done.")


class BranchMixin(SkipMixin):
    def execute(self, context):
        branch = super(BranchMixin, self).execute(context)
        if isinstance(branch, str):
            branch = [branch]
        self.log.info("Following branch %s", branch)
        self.log.info("Marking other directly downstream tasks as skipped")

        downstream_tasks = context["task"].downstream_list
        self.log.debug("Downstream task_ids %s", downstream_tasks)

        if downstream_tasks:
            # Also check downstream tasks of the branch task. In case the task to skip
            # is a downstream task of the branch task, we exclude it from skipping.
            branch_downstream_task_ids = set()
            for b in branch:
                branch_downstream_task_ids.update(
                    context["dag"].get_task(b).get_flat_relative_ids(upstream=False)
                )
            skip_tasks = [
                t
                for t in downstream_tasks
                if t.task_id not in branch
                and t.task_id not in branch_downstream_task_ids
            ]
            self.skip(context["dag_run"], context["ti"].execution_date, skip_tasks)

        self.log.info("Done.")


@register_extensions
class DockerOperator(AirflowDockerOperator):
    """
    Execute a command inside a docker container.

    A temporary directory is created on the host and
    mounted into a container to allow storing files
    that together exceed the default disk size of 10GB in a container.
    The path to the mounted directory can be accessed
    via the environment variable ``AIRFLOW_TMP_DIR``.

    If a login to a private registry is required prior to pulling the image, a
    Docker connection needs to be configured in Airflow and the connection ID
    be provided with the parameter ``docker_conn_id``.

    :param image: Docker image from which to create the container.
        If image tag is omitted, "latest" will be used.
    :type image: str
    :param api_version: Remote API version. Set to ``auto`` to automatically
        detect the server's version.
    :type api_version: str
    :param command: Command to be run in the container. (templated)
    :type command: str or list
    :param container_name: Name of the container. Optional (templated)
    :type container_name: str or None
    :param cpus: Number of CPUs to assign to the container.
        This value gets multiplied with 1024. See
        https://docs.docker.com/engine/reference/run/#cpu-share-constraint
    :type cpus: float
    :param docker_url: URL of the host running the docker daemon.
        Default is unix://var/run/docker.sock
    :type docker_url: str
    :param environment: Environment variables to set in the container. (templated)
    :type environment: dict
    :param private_environment: Private environment variables to set in the container.
        These are not templated, and hidden from the website.
    :type private_environment: dict
    :param force_pull: Pull the docker image on every run. Default is False.
    :type force_pull: bool
    :param mem_limit: Maximum amount of memory the container can use.
        Either a float value, which represents the limit in bytes,
        or a string like ``128m`` or ``1g``.
    :type mem_limit: float or str
    :param host_tmp_dir: Specify the location of the temporary directory on the host which will
        be mapped to tmp_dir. If not provided defaults to using the standard system temp directory.
    :type host_tmp_dir: str
    :param network_mode: Network mode for the container.
    :type network_mode: str
    :param tls_ca_cert: Path to a PEM-encoded certificate authority
        to secure the docker connection.
    :type tls_ca_cert: str
    :param tls_client_cert: Path to the PEM-encoded certificate
        used to authenticate docker client.
    :type tls_client_cert: str
    :param tls_client_key: Path to the PEM-encoded key used to authenticate docker client.
    :type tls_client_key: str
    :param tls_hostname: Hostname to match against
        the docker server certificate or False to disable the check.
    :type tls_hostname: str or bool
    :param tls_ssl_version: Version of SSL to use when communicating with docker daemon.
    :type tls_ssl_version: str
    :param tmp_dir: Mount point inside the container to
        a temporary directory created on the host by the operator.
        The path is also made available via the environment variable
        ``AIRFLOW_TMP_DIR`` inside the container.
    :type tmp_dir: str
    :param user: Default user inside the docker container.
    :type user: int or str
    :param volumes: List of volumes to mount into the container, e.g.
        ``['/host/path:/container/path', '/host/path2:/container/path2:ro']``.
    :type volumes: list
    :param working_dir: Working directory to
        set on the container (equivalent to the -w switch the docker client)
    :type working_dir: str
    :param xcom_all: Push all the stdout or just the last line.
        The default is False (last line).
    :type xcom_all: bool
    :param docker_conn_id: ID of the Airflow connection to use
    :type docker_conn_id: str
    :param dns: Docker custom DNS servers
    :type dns: list[str]
    :param dns_search: Docker custom DNS search domain
    :type dns_search: list[str]
    :param auto_remove: Auto-removal of the container on daemon side when the
        container's process exits.
        The default is False.
    :type auto_remove: bool
    :param shm_size: Size of ``/dev/shm`` in bytes. The size must be
        greater than 0. If omitted uses system default.
    :type shm_size: int
    :param tty: Allocate pseudo-TTY to the container
        This needs to be set see logs of the Docker container.
    :type tty: bool

    :param provide_context: If True, make a serialized form of the context available.
    :type provide_context: bool

    :param environment_preset: The name of the environment-preset to pull from the config.
        If omitted defaults to the "default" key, see `EnvironmentPresetExtension`.
    :type environment_preset: string
    """
    template_fields = ('command', 'environment', 'container_name', "extra_kwargs")
    known_extra_kwargs = set()

    @apply_defaults
    def __init__(
            self,
            image: str,
            force_pull: bool = get_boolean_default("force_pull", True),
            network_mode: Optional[str] = get_default("network_mode", None),
            auto_remove: bool = get_boolean_default("auto_remove", True),
            provide_context=False,
            *args,
            **kwargs) -> None:

        self.extra_kwargs = {
            known_key: kwargs.pop(known_key)
            for known_key in self.known_extra_kwargs
            # This conditional is critical since we can not know
            # here what a "default" value should look like.
            if known_key in kwargs
        }

        super().__init__(*args, force_pull=force_pull, network_mode=network_mode, auto_remove=auto_remove, **kwargs)

        self._host_client = None  # Shim for attaching a test client

    def execute(self, context):
        # Hook for creating mounted meta directories
        self.prepare_host_tmp_dir(context, self.host_tmp_dir)
        self.prepare_environment(context, self.host_tmp_dir)

        if self.provide_context:
            self.write_context(context, self.host_tmp_dir)

        super().execute(context)

        # Move the in-container xcom-pushes into airflow.
        result = self.host_client.get_xcom_push_data(self.host_tmp_dir)
        for row in result:
            self.xcom_push(context, key=row["key"], value=row["value"])

        return self.do_meta_operation(context, self.host_tmp_dir)

    def do_meta_operation(self, context, host_tmp_dir):
        pass

    def prepare_environment(self, context, host_tmp_dir):
        delegate_to_extensions(self, "post_prepare_environment", context, host_tmp_dir)

    def prepare_host_tmp_dir(self, context, host_tmp_dir):
        self.host_client.make_meta_dir(host_tmp_dir)
        host_meta_dir = airflow_docker_helper.get_host_meta_path(host_tmp_dir)
        self.log.info("Making host meta dir: {}".format(host_meta_dir))

    def write_context(self, context, host_tmp_dir):
        self.host_client.write_context(context, host_tmp_dir)

    def host_meta_dir(self, context, host_tmp_dir):
        return airflow_docker_helper.get_host_meta_path(host_tmp_dir)

    @property
    def host_client(self):
        return self._host_client or airflow_docker_helper.host

    @staticmethod
    def get_config():
        return get_config()


class Operator(BaseDockerOperator, BaseOperator):
    def execute(self, context):
        return self._execute(context)


class Sensor(BaseDockerOperator, BaseSensorOperator):
    def poke(self, context):
        return self._execute(context)

    def do_meta_operation(self, context, host_tmp_dir):
        return self.host_client.sensor_outcome(host_tmp_dir)


class ShortCircuitOperator(ShortCircuitMixin, Operator):
    def do_meta_operation(self, context, host_tmp_dir):
        return self.host_client.short_circuit_outcome(host_tmp_dir)


class BranchOperator(BranchMixin, Operator):
    def do_meta_operation(self, context, host_tmp_dir):
        return self.host_client.branch_task_ids(host_tmp_dir)
