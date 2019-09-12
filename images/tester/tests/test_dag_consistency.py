import os

import pytest

from tests import DAG_PATH, DAG_FILES


@pytest.mark.parametrize('dag_file', DAG_FILES)
def test_all_dags_in_dag_bag(dag_bag, dag_file):
    """Assert that all the dags for which there are files exist in the airflow dag bag.
    """
    dag_files = {
        os.path.split(dag.full_filepath)[-1]
        for dag in dag_bag.dags.values()
    }

    assert dag_file in dag_files
