from airflow.plugins_manager import AirflowPlugin
from airflow_docker.operator import (
    BranchOperator,
    Operator,
    Sensor,
    ShortCircuitOperator,
)
from airflow_docker.views import config, extensions


class AirflowDockerPlugin(AirflowPlugin):
    name = "airflow_docker"

    operators = [BranchOperator, Operator, ShortCircuitOperator]
    sensors = [Sensor]
    admin_views = [config.view, extensions.view]
    flask_blueprints = [config.blueprint, extensions.blueprint]

    appbuilder_views = [config.appbuilder_package, extensions.appbuilder_package]
