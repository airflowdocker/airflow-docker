from airflow_docker.utils import get_config


def test_get_config_with_env():
    config = get_config(env="test", config_path="tests", config_file="config.json")
    assert config == {"test-run": {"image": "path/to/image"}}


def test_get_config():
    config = get_config(config_path="tests", config_file="config.json")
    assert config == {"test": {"test-run": {"image": "path/to/image"}}}
