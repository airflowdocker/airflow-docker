import functools
import json
import os

from airflow import configuration
from airflow.models import Variable


@functools.lru_cache()
def get_config(path=None, file="config.json"):
    """Load the config for the current airflow environment."""
    if path is None:
        path = configuration.get("core", "dags_folder")

    path = os.path.join(path, file)
    if os.path.exists(path):
        with open(path, "rb") as f:
            config = json.load(f)
    else:
        config = {}

    config.setdefault("airflow-docker", {})

    return config


def get_env():
    """Get the name of the environment for the current airflow environment."""
    return Variable.get("env")
