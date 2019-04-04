import airflow.configuration as conf
from airflow.exceptions import AirflowConfigException


def get_boolean_default(key, default):
    try:
        return conf.getboolean("airflowdocker", key)
    except AirflowConfigException:
        return default


def get_default(key, default):
    try:
        return conf.get("airflowdocker", key)
    except AirflowConfigException:
        return default
