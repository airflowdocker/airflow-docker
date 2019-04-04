try:
    import unittest.mock as mock
except ImportError:
    import mock


from airflow_docker.conf import get_boolean_default, get_default


def test_boolean_env_var_set():
    with mock.patch.dict("os.environ", {"AIRFLOW__AIRFLOWDOCKER__FORCE_PULL": "true"}):
        force_pull = get_boolean_default("force_pull", False)
        assert force_pull is True


def test_boolean_env_var_not_set():
    with mock.patch.dict("os.environ", clear=True):
        force_pull = get_boolean_default("force_pull", False)
        assert force_pull is False


def test_env_var_set():
    with mock.patch.dict(
        "os.environ", {"AIRFLOW__AIRFLOWDOCKER__NETWORK_MODE": "mynetwork"}
    ):
        network_mode = get_default("network_mode", None)
        assert network_mode == "mynetwork"


def test_env_var_not_set():
    with mock.patch.dict("os.environ", clear=True):
        network_mode = get_default("network_mode", None)
        assert network_mode is None
