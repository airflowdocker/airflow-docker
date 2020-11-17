def get_boolean_default(key, default):
    from airflow.configuration import conf

    if conf.has_option("airflowdocker", key):
        return conf.getboolean("airflowdocker", key)
    else:
        return default


def get_default(key, default=None):
    from airflow.configuration import conf

    if conf.has_option("airflowdocker", key):
        return conf.get("airflowdocker", key)
    else:
        return default


def get_default_list(key, default=None):
    default = default if default is not None else []

    result = get_default(key)
    if result is None:
        return default
    return [line.strip() for line in result.split("\n") if line.strip()]
