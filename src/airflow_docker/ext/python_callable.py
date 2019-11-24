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
import base64
import json
import textwrap

from airflow.utils.db import provide_session

from airflow_docker.constants import CONTAINER_RUN_DIR
from airflow_docker.context import serialize_context

PYTHON_ENTRYPOINT = textwrap.dedent(
    """\
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import {python_import_path}

args = json.loads(base64.b64decode("{args}".encode('ascii')))
kwargs = json.loads(base64.b64decode("{kwargs}".encode('ascii')))
result = {python_import_path}.{callable}(*args, **kwargs)
with open('{container_run_dir}/result.json', 'w') as f:
    json.dump(result, f)
"""
)


class PythonCallableExtension:
    kwargs = {"python_callable", "op_args", "op_kwargs"}

    @classmethod
    @provide_session
    def post_prepare_environment(
        cls, operator, config, context, host_tmp_dir, session=None
    ):
        python_callable = operator.extra_kwargs.get("python_callable", None)
        args = operator.extra_kwargs.get("op_args", [])
        op_kwargs = operator.extra_kwargs.get("op_kwargs", {})

        if operator.provide_context:
            context = serialize_context(context)
            context.update(op_kwargs)
            kwargs = context
        else:
            kwargs = op_kwargs

        if operator.command is None and python_callable is not None:
            operator.log.info(
                "Preparing entry point script to call: {}".format(python_callable)
            )
            module, callable = python_callable.split(":")
            entrypoint = PYTHON_ENTRYPOINT.format(
                python_import_path=module,
                callable=callable,
                args=base64.b64encode(json.dumps(args).encode("utf-8")).decode("ascii"),
                kwargs=base64.b64encode(json.dumps(kwargs).encode("utf-8")).decode(
                    "ascii"
                ),
                container_run_dir=CONTAINER_RUN_DIR,
            )
            operator.container_data["entrypoint.py"] = entrypoint.encode("utf-8")
            operator.log.debug(
                "Set the entrypoint.py script: \n{}".format(
                    operator.container_data["entrypoint.py"]
                )
            )

            if operator.entrypoint is None:
                operator.entrypoint = "/usr/bin/env python"
                operator.log.info(
                    "Set the docker entrypoint: {}".format(operator.entrypoint)
                )

            operator.command = json.dumps(["/var/run/airflow-docker/entrypoint.py"])
            operator.log.info("Set the docker command: {}".format(operator.command))

        else:
            if any([python_callable, args, op_kwargs]):
                raise ValueError(
                    "It appears you are trying to use the PythonCallExtension. You must pass 'call' to the operator."
                )
