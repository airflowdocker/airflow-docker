import json
import os

from airflow.models import Variable


def get_config(env=None, config_path="/airflow/dags", config_file="config.json"):
    """Load the config for the current airflow environment.

    The only assumption about the structure of the file is that, if `env` is provided,
    there exists top-level keys containing the name(s) of the different environments.

    Example:
        {
            "dev": {
                "image": "<image-location>"
            },
            "prod": {
                "image": "<image-location>"
            }
        }
    """
    with open(os.path.join(config_path, config_file), "r") as f:
        config = json.load(f)

    if env is not None:
        return config[env]
    return config


def get_env():
    """Get the name of the environment for the current airflow environment.
    """
    return Variable.get("env")
