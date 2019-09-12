import airflow.configuration as conf
from airflow.exceptions import AirflowConfigException


def get_boolean_default(key, default):
    try:
        return conf.getboolean("airflowdocker", key)
    except AirflowConfigException:
        return default


def get_default(key, default=None):
    try:
        return conf.get("airflowdocker", key)
    except AirflowConfigException:
        return default


def get_default_list(key, default=None):
    default = default if default is not None else []

    result = get_default(key)
    if result is None:
        return default
    return [line.strip() for line in result.split("\n") if line.strip()]
