import functools

from airflow.models import Variable
from airflow.utils.db import provide_session


def collect_variable_values(session, *variables):
    return {
        item.key: item.val
        for item in session.query(Variable).filter(Variable.key.in_(variables))
    }


def calculate_task_name(operator, context, sep="__"):
    dag_id = context["dag"].dag_id
    return sep.join([dag_id, operator.task_id])


@functools.lru_cache()
def classify_docker_image(image):
    sections = image.split(":")

    image_name = sections[0]

    if len(sections) > 1:
        tag = sections[1]
    else:
        tag = "latest"

    return (image_name, tag)


def collect_environment_preset(session, operator, context, keys):
    variables = collect_variable_values(session, *keys.keys())

    supported_environment_collectors = {
        "task_name": lambda: calculate_task_name(operator, context),
        "dagrun_id": lambda: context["run_id"],
        "docker_image": lambda: operator.image,
        "docker_image_name": lambda: classify_docker_image(operator.image)[0],
        "docker_image_tag": lambda: classify_docker_image(operator.image)[1],
    }

    result = {}

    for key, destination_key in keys.items():
        value = None
        if key in supported_environment_collectors:
            value = supported_environment_collectors[key]()
        elif key in variables:
            value = variables[key]

        if value is not None:
            result[destination_key] = value
    return result


def write_environment_preset(session, operator, context, environment_preset):
    environment_preset_data = collect_environment_preset(
        session, operator, context, environment_preset
    )

    operator.log.info("Setting Environment:")
    for name, value in environment_preset_data.items():
        # The operator's "environment" kwarg has the highest precedent, dont overwrite it.
        if name in operator.environment:
            continue

        operator.environment[name] = value
        operator.log.info("  %s = '%s'", name, value)


class EnvironmentPresetExtension:
    kwargs = {"environment_preset"}
    config_key = "environment-presets"
    default_preset = "default"

    @classmethod
    @provide_session
    def post_prepare_environment(
        cls, operator, config, context, host_tmp_dir, session=None
    ):
        environment_presets = config.get(cls.config_key, {cls.default_preset: {}})

        environment_preset = operator.extra_kwargs.get(
            "environment_preset", cls.default_preset
        )
        if environment_preset in environment_presets:
            write_environment_preset(
                session,
                operator,
                context,
                environment_preset=environment_presets[environment_preset],
            )
