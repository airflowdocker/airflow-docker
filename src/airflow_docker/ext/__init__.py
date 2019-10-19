import functools
import importlib

from airflow_docker import conf
from airflow_docker.utils import get_config


def delegate_to_extensions(self, method_name, *args, **kwargs):
    config = get_config()["airflow-docker"]
    for extension in self._extensions:
        method = getattr(extension, method_name, None)
        if not method:
            continue

        method(self, config, *args, **kwargs)


def by_name(item):
    return item.__name__


@functools.lru_cache()
def load_extensions():
    result = set()
    for extension_path in conf.get_default_list("extension_paths"):
        try:
            module_name, extension_name = extension_path.rsplit(":", 1)
        except ValueError:
            raise ValueError("Specify extension paths like: module.submodule:Extension")

        module = importlib.import_module(module_name)
        result.add(getattr(module, extension_name))
    return sorted(list(result), key=by_name)


def register_extensions(cls):
    if hasattr(cls, "_extensions"):
        return

    cls._extensions = load_extensions()

    for extension in cls._extensions:
        cls.known_extra_kwargs.update(getattr(extension, "kwargs", set()))

    return cls
