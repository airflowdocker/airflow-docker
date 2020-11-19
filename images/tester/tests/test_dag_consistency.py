import os
import logging
import subprocess

import pytest

from tests import DAG_FILES, DAG_PATH


@pytest.mark.parametrize("dag_file", DAG_FILES)
def test_all_dags_in_dag_bag(dag_bag, dag_file, dag_files):
    """Assert that all the dags for which there are files exist in the airflow dag bag.
    """
    key = (os.path.join(DAG_PATH, dag_file),)
    if key in dag_bag.dagbag_exceptions:
        raise dag_bag.dagbag_exceptions[key]


def test_no_dag_exceptions(dag_bag):
    """Assert there are no dagbag exceptions in general.
    """
    assert dag_bag.dagbag_exceptions == {}
