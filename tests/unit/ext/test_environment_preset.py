from unittest.mock import patch

from airflow_docker.ext.environment_preset import (
    calculate_task_name,
    classify_docker_image,
    collect_environment_preset,
    EnvironmentPresetExtension,
)


class Test_calculate_task_name:
    def test_default(self):
        class Operator:
            task_id = "food"

        class Dag:
            dag_id = "bar"

        context = {"dag": Dag()}

        task_name = calculate_task_name(Operator(), context)
        assert task_name == "bar__food"


class Test_classify_docker_image:
    def test_no_tag(self):
        result = classify_docker_image("1234.foo/bar")
        assert result == ("1234.foo/bar", "latest")

    def test_with_tag(self):
        result = classify_docker_image("1234.foo/bar:1.2.3")
        assert result == ("1234.foo/bar", "1.2.3")


class Test_collect_environment_preset:
    class Operator:
        task_id = "foo"
        image = "foo/bar"

    class Dag:
        dag_id = "bar"

    def test_invalid_keys(self):
        with patch(
            "airflow_docker.ext.environment_preset.collect_variable_values",
            return_value={"meow": "meow"},
        ):
            result = collect_environment_preset(None, self.Operator(), None, {})
        assert result == {}

    def test_keys_no_variables(self):
        with patch(
            "airflow_docker.ext.environment_preset.collect_variable_values",
            return_value={},
        ):
            result = collect_environment_preset(
                None,
                self.Operator(),
                {"dag": self.Dag(), "run_id": "run"},
                {
                    "docker_image_name": "DI",
                    "docker_image_tag": "DT",
                    "docker_image": "D",
                    "dagrun_id": "DR",
                    "task_name": "TN",
                },
            )
        assert result == {
            "DI": "foo/bar",
            "DT": "latest",
            "D": "foo/bar",
            "DR": "run",
            "TN": "bar__foo",
        }

    def test_keys_variables(self):
        with patch(
            "airflow_docker.ext.environment_preset.collect_variable_values",
            return_value={"env": "prod"},
        ):
            result = collect_environment_preset(
                None, self.Operator(), None, {"docker_image_name": "DI", "env": "ENV"}
            )
        assert result == {"DI": "foo/bar", "ENV": "prod"}

    def test_null_variables(self):
        with patch(
            "airflow_docker.ext.environment_preset.collect_variable_values",
            return_value={"env": None},
        ):
            result = collect_environment_preset(
                None, self.Operator(), None, {"env": "ENV"}
            )
        assert result == {}


class TestEnvironmentPresetExtension_post_prepare_environment:
    def setup(self):
        class Operator:
            task_id = "food"
            extra_kwargs = {}

        self.operator = Operator()

    def test_no_default_no_op(self):
        EnvironmentPresetExtension().post_prepare_environment(
            self.operator, {}, context={}, host_tmp_dir=""
        )
