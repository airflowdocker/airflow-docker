from unittest.mock import mock_open, patch

from airflow_docker.utils import get_config


class Test_get_config:
    def setup(self):
        get_config.cache_clear()

    def test_file_missing(self):
        with patch("os.path.exists", return_value=False):
            result = get_config()
        assert result == {"airflow-docker": {}}

    def test_empty_file_exists(self):
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data="{}")
        ):
            result = get_config()
        assert result == {"airflow-docker": {}}

    def test_file_exists_with_data(self):
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data='{"foo": 4}')
        ):
            result = get_config()
        assert result == {"airflow-docker": {}, "foo": 4}

    def test_file_exists_with_airflow_docker_section(self):
        with patch("os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data='{"airflow-docker": {"anything": 4}}')
        ):
            result = get_config()
        assert result == {"airflow-docker": {"anything": 4}}

    def test_explicit_path(self):
        with patch("os.path.exists", return_value=False):
            result = get_config(path="/path/")
        assert result == {"airflow-docker": {}}
