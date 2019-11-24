import functools
import io
import json
import os
import tarfile
import time

from airflow import configuration
from airflow.models import Variable


@functools.lru_cache()
def get_config(path=None, file="config.json"):
    """Load the config for the current airflow environment.
    """
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
    """Get the name of the environment for the current airflow environment.
    """
    return Variable.get("env")


def make_tar_data_stream(tar_spec):
    tar_stream = io.BytesIO()
    with tarfile.TarFile(fileobj=tar_stream, mode="w") as tar:
        for key, bytes_data in tar_spec.items():
            tarinfo = tarfile.TarInfo(name=key)
            tarinfo.size = len(bytes_data)
            tarinfo.mtime = time.time()
            tar.addfile(tarinfo, io.BytesIO(bytes_data))

    tar_stream.seek(0)

    return tar_stream


def process_tar_data_stream(tar_data_stream, root):
    data_file = io.BytesIO()
    for chunk in tar_data_stream:
        data_file.write(chunk)
    data_file.seek(0)

    root, base = os.path.split(root)
    base = f"{base}/"
    data = {}

    with tarfile.open(mode="r", fileobj=data_file) as t:
        for filename in t.getnames():
            file = t.extractfile(filename)
            if file:
                key = filename.split(base, 1)[-1]  # Gets the path after the first root
                data[key] = file.read()
                file.close()
    return data
