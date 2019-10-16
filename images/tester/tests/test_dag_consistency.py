import os

import pytest

from tests import DAG_FILES, DAG_PATH


@pytest.mark.parametrize("dag_file", DAG_FILES)
def test_all_dags_in_dag_bag(dag_bag, dag_file):
    """Assert that all the dags for which there are files exist in the airflow dag bag.
    """
    dag_files = {
        os.path.join(*dag.full_filepath.split(os.path.sep)[3:])
        for dag in dag_bag.dags.values()
    }

    assert dag_file in dag_files
