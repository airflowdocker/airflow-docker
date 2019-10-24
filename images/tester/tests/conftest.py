import logging
import os
import sys

import airflow
import pytest

from tests import DAG_PATH


class Logger(logging.Logger):
    def __get__(self, instance, owner):
        self.instance = instance
        return self

    def exception(self, message, *args):
        self.instance.dagbag_exceptions[args] = sys.exc_info()[1]
        return super().exception(message, *args)


class DagBag(airflow.models.DagBag):
    _log = Logger(".")

    dagbag_exceptions = {}


@pytest.fixture(scope="session")
def dag_bag():
    return DagBag(DAG_PATH)


@pytest.fixture(scope="session")
def dag_files(dag_bag):
    return {
        os.path.join(*dag.full_filepath.split(os.path.sep)[3:])
        for dag in dag_bag.dags.values()
    }
