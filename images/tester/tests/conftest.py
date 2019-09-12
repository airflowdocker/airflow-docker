import airflow
import pytest

from tests import DAG_PATH


@pytest.fixture(scope='session')
def dag_bag():
    return airflow.models.DagBag(DAG_PATH)
