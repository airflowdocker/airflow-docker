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
import io
import json
import os

import six
from airflow.exceptions import AirflowException
from airflow.hooks.docker_hook import DockerHook
from airflow.models import BaseOperator, SkipMixin
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from docker import APIClient, tls

from airflow_docker.conf import get_boolean_default, get_default
from airflow_docker.constants import (
    BRANCH_OPERATOR_FILENAME,
    CONTAINER_RUN_DIR,
    CONTEXT_FILENAME,
    META_PATH_DIR,
    RESULT_FILENAME,
    SENSOR_OPERATOR_FILENAME,
    SHORT_CIRCUIT_OPERATOR_FILENAME,
    XCOM_PUSH_FILENAME,
)
from airflow_docker.context import serialize_context
from airflow_docker.ext import delegate_to_extensions, register_extensions
from airflow_docker.utils import (
    get_config,
    make_tar_data_stream,
    process_tar_data_stream,
)


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
        if isinstance(branch, six.string_types):
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
class BaseDockerOperator(object):
    """
    Execute a command inside a docker container.

    If a login to a private registry is required prior to pulling the image, a
    Docker connection needs to be configured in Airflow and the connection ID
    be provided with the parameter ``docker_conn_id``.

    :param image: Docker image from which to create the container.
        If image tag is omitted, "latest" will be used.
    :type image: str
    :param api_version: Remote API version. Set to ``auto`` to automatically
        detect the server's version.
    :type api_version: str
    :param auto_remove: Auto-removal of the container on daemon side when the
        container's process exits.
        The default is True.
    :type auto_remove: bool
    :param command: Command to be run in the container. (templated)
    :type command: str or list
    :param cpus: Number of CPUs to assign to the container.
        This value gets multiplied with 1024. See
        https://docs.docker.com/engine/reference/run/#cpu-share-constraint
    :type cpus: float
    :param dns: Docker custom DNS servers
    :type dns: list of strings
    :param dns_search: Docker custom DNS search domain
    :type dns_search: list of strings
    :param docker_url: URL of the host running the docker daemon.
        Default is unix://var/run/docker.sock
    :type docker_url: str
    :param environment: Environment variables to set in the container. (templated)
    :type environment: dict
    :param force_pull: Pull the docker image on every run. Default is True.
    :type force_pull: bool
    :param mem_limit: Maximum amount of memory the container can use.
        Either a float value, which represents the limit in bytes,
        or a string like ``128m`` or ``1g``.
    :type mem_limit: float or str
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
    :param working_dir: Working directory to
        set on the container (equivalent to the -w switch the docker client)
    :type working_dir: str
    :param xcom_push: Does the stdout will be pushed to the next step using XCom.
        The default is False.
    :type xcom_push: bool
    :param xcom_all: Push all the stdout or just the last line.
        The default is False (last line).
    :type xcom_all: bool
    :param docker_conn_id: ID of the Airflow connection to use
    :type docker_conn_id: str
    :param shm_size: Size of ``/dev/shm`` in bytes. The size must be
        greater than 0. If omitted uses system default.
    :type shm_size: int
    :param provide_context: If True, make a serialized form of the context available.
    :type provide_context: bool

    :param environment_preset: The name of the environment-preset to pull from the config.
        If omitted defaults to the "default" key, see `EnvironmentPresetExtension`.
    :type environment_preset: string
    """

    template_fields = ("command", "environment", "extra_kwargs")
    template_ext = (".sh", ".bash")
    known_extra_kwargs = set()

    @apply_defaults
    def __init__(
        self,
        image,
        api_version=None,
        entrypoint=None,
        command=None,
        cpus=1.0,
        docker_url="unix://var/run/docker.sock",
        environment=None,
        force_pull=get_boolean_default("force_pull", True),
        mem_limit=None,
        network_mode=get_default("network_mode", None),
        tls_ca_cert=None,
        tls_client_cert=None,
        tls_client_key=None,
        tls_hostname=None,
        tls_ssl_version=None,
        tmp_dir="/tmp/airflow",
        user=None,
        volumes=None,
        working_dir=None,
        xcom_push=False,
        xcom_all=False,
        docker_conn_id=None,
        dns=None,
        dns_search=None,
        auto_remove=get_boolean_default("auto_remove", True),
        shm_size=None,
        provide_context=False,
        *args,
        **kwargs
    ):
        self.extra_kwargs = {
            known_key: kwargs.pop(known_key)
            for known_key in self.known_extra_kwargs
            # This conditional is critical since we can not know
            # here what a "default" value should look like.
            if known_key in kwargs
        }

        super(BaseDockerOperator, self).__init__(*args, **kwargs)
        self.api_version = api_version
        self.auto_remove = auto_remove
        self.command = command
        self.entrypoint = entrypoint
        self.cpus = cpus
        self.dns = dns
        self.dns_search = dns_search
        self.docker_url = docker_url
        self.environment = environment or {}
        self.force_pull = force_pull
        self.image = image
        self.mem_limit = mem_limit
        self.network_mode = network_mode
        self.tls_ca_cert = tls_ca_cert
        self.tls_client_cert = tls_client_cert
        self.tls_client_key = tls_client_key
        self.tls_hostname = tls_hostname
        self.tls_ssl_version = tls_ssl_version
        self.tmp_dir = tmp_dir
        self.user = user
        self.volumes = volumes or []
        self.working_dir = working_dir
        self.xcom_push_flag = xcom_push
        self.xcom_all = xcom_all
        self.docker_conn_id = docker_conn_id
        self.shm_size = shm_size
        self.provide_context = provide_context

        self.container_data = {}
        """A mapping of filenames to file data in bytes."""

        self.cli = None
        self.container = None

    def get_hook(self):
        return DockerHook(
            docker_conn_id=self.docker_conn_id,
            base_url=self.docker_url,
            version=self.api_version,
            tls=self.__get_tls_config(),
        )

    def _execute(self, context):
        self.log.info("Starting docker container from image %s", self.image)

        tls_config = self.__get_tls_config()

        if self.docker_conn_id:
            self.cli = self.get_hook().get_conn()
        else:
            self.cli = APIClient(
                base_url=self.docker_url, version=self.api_version, tls=tls_config
            )

        if self.force_pull or len(self.cli.images(name=self.image)) == 0:
            self.log.info("Pulling docker image %s", self.image)
            for l in self.cli.pull(self.image, stream=True):
                output = json.loads(l.decode("utf-8").strip())
                if "status" in output:
                    self.log.info("%s", output["status"])

        self.environment["AIRFLOW_TMP_DIR"] = self.tmp_dir
        additional_volumes = [
            os.path.join(self.tmp_dir, META_PATH_DIR),
            CONTAINER_RUN_DIR,
        ]

        self.prepare_environment(context)

        if self.provide_context:
            self.container_data[CONTEXT_FILENAME] = json.dumps(
                serialize_context(context)
            ).encode("utf-8")

        self.container = self.cli.create_container(
            command=self.get_command(),
            entrypoint=self.entrypoint,
            environment=self.environment,
            host_config=self.cli.create_host_config(
                auto_remove=False,  # The operator implementation will be responsible for removing the container
                binds=self.volumes + additional_volumes,
                network_mode=self.network_mode,
                shm_size=self.shm_size,
                dns=self.dns,
                dns_search=self.dns_search,
                cpu_shares=int(round(self.cpus * 1024)),
                mem_limit=self.mem_limit,
            ),
            image=self.image,
            user=self.user,
            working_dir=self.working_dir,
        )

        self.log.info("Container created: %s", self.container["Id"])

        self.put_container_data(root=CONTAINER_RUN_DIR, spec=self.container_data)

        self.put_container_data(
            root=os.path.join(self.tmp_dir, META_PATH_DIR), spec=self.container_data
        )

        self.cli.start(self.container["Id"])

        line = ""
        for line in self.cli.logs(container=self.container["Id"], stream=True):
            line = line.strip()
            if hasattr(line, "decode"):
                line = line.decode("utf-8")
            self.log.info(line)

        result = self.cli.wait(self.container["Id"])
        if result["StatusCode"] != 0:
            raise AirflowException("docker container failed: " + repr(result))

        self.gather_container_data(path=os.path.join(self.tmp_dir, META_PATH_DIR))
        self.gather_container_data(path=CONTAINER_RUN_DIR)

        for row in self.get_xcom_data():
            self.xcom_push(context, key=row["key"], value=row["value"])

        if self.xcom_push_flag:
            return (
                self.cli.logs(container=self.container["Id"])
                if self.xcom_all
                else str(line)
            )

        return self.do_meta_operation(context)

    def get_command(self):
        if self.command is not None and self.command.strip().find("[") == 0:
            commands = ast.literal_eval(self.command)
        else:
            commands = self.command
        return commands

    def on_kill(self):
        if self.cli is not None:
            self.log.info("Stopping docker container")
            self.cli.stop(self.container["Id"])
            self.maybe_remove()

    def maybe_remove(self):
        if self.cli is not None and self.auto_remove:
            self.cli.remove_container(self.container["Id"], v=True)

    def __get_tls_config(self):
        tls_config = None
        if self.tls_ca_cert and self.tls_client_cert and self.tls_client_key:
            tls_config = tls.TLSConfig(
                ca_cert=self.tls_ca_cert,
                client_cert=(self.tls_client_cert, self.tls_client_key),
                verify=True,
                ssl_version=self.tls_ssl_version,
                assert_hostname=self.tls_hostname,
            )
            self.docker_url = self.docker_url.replace("tcp://", "https://")
        return tls_config

    def do_meta_operation(self, context):
        return _maybe_decode_keys(
            data=self.container_data, keys=[RESULT_FILENAME], default=None
        )

    def prepare_environment(self, context):
        delegate_to_extensions(self, "post_prepare_environment", context, None)

    @staticmethod
    def get_config():
        return get_config()

    def put_container_data(self, root, spec):
        tar_stream = make_tar_data_stream(tar_spec=spec)

        return self.cli.put_archive(
            container=self.container["Id"], path=root, data=tar_stream,
        )

    def gather_container_data(self, path):
        data_stream, info = self.cli.get_archive(
            container=self.container["Id"], path=path,
        )
        data = process_tar_data_stream(data_stream, path)
        self.container_data.update(data)

    def get_xcom_data(self):
        if XCOM_PUSH_FILENAME not in self.container_data:
            return []

        result = self.container_data[XCOM_PUSH_FILENAME]
        result = [
            json.loads(row.decode("utf-8").strip())
            for row in result.split(b"\n")
            if row.decode("utf-8").strip()
        ]
        return result


class Operator(BaseDockerOperator, BaseOperator):
    def execute(self, context):
        return self._execute(context)


class Sensor(BaseDockerOperator, BaseSensorOperator):
    def poke(self, context):
        # In mode=poke, this operator will hold state in between each run.
        # We should clear out the sensor result before running.
        self.reset_sensor()
        return self._execute(context)

    def reset_sensor(self):
        for key in [RESULT_FILENAME, SENSOR_OPERATOR_FILENAME]:
            if key in self.container_data:
                del self.container_data[key]

    def do_meta_operation(self, context):
        return _maybe_decode_keys(
            data=self.container_data,
            keys=[RESULT_FILENAME, SENSOR_OPERATOR_FILENAME],
            default=False,
        )


class ShortCircuitOperator(ShortCircuitMixin, Operator):
    def do_meta_operation(self, context):
        return _maybe_decode_keys(
            data=self.container_data,
            keys=[RESULT_FILENAME, SHORT_CIRCUIT_OPERATOR_FILENAME],
            default=True,
        )


class BranchOperator(BranchMixin, Operator):
    def do_meta_operation(self, context):
        return _maybe_decode_keys(
            data=self.container_data,
            keys=[RESULT_FILENAME, BRANCH_OPERATOR_FILENAME],
            default=[],
        )


def _maybe_decode_keys(data, keys, default=None):
    for key in keys:
        if key in data:
            return json.loads(data[key].decode('utf-8'))
    else:
        return default
