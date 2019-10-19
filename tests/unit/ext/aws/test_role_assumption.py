import datetime
import os
from unittest import mock

import airflow_docker.ext.aws.role_assumption
import airflow_docker.operator
from airflow.models import DAG, DagRun, TaskInstance

import pytest

HERE = os.path.dirname(__file__)


def test_credentials_file_format():
    from airflow_docker.ext.aws.role_assumption import aws_credentials_file_format

    file_format = aws_credentials_file_format("foo", "bar", "baz", "boo")
    with open(
        os.path.join(HERE, "..", "..", "..", "data", "test_credentials_file"), "rb"
    ) as f:
        test_file = f.read().decode("utf-8")

    assert file_format == test_file


def test_default_profile_name():
    from airflow_docker.ext.aws.role_assumption import aws_credentials_file_format

    file_format = aws_credentials_file_format("foo", "bar", "baz")
    assert file_format.startswith("[default]")


@mock.patch("airflow_docker.ext.aws.role_assumption.boto3")
def test_generate_credentials(boto3):
    boto3.client.return_value.assume_role.return_value = {
        "Credentials": {
            "AccessKeyId": "access_key_id",
            "SecretAccessKey": "secret_access_key",
            "SessionToken": "session_token",
        }
    }

    result = airflow_docker.ext.aws.role_assumption.generate_role_credentials(
        "arn:aws:iam::123456789012:role/test-role", "foobar"
    )
    assert result == boto3.client.return_value.assume_role.return_value

    _, args, kwargs = boto3.client.return_value.assume_role.mock_calls[0]
    assert "arn:aws:iam::123456789012:role/test-role" in kwargs.values()
    assert "foobar" in kwargs.values()


def test_format_credentials_data():
    raw_credentials = {
        "Credentials": {
            "AccessKeyId": "access_key_id",
            "SecretAccessKey": "secret_access_key",
            "SessionToken": "session_token",
        }
    }

    credentials = airflow_docker.ext.aws.role_assumption.format_credentials_data(
        raw_credentials
    )
    assert credentials["aws_access_key_id"] == "access_key_id"
    assert credentials["aws_secret_access_key"] == "secret_access_key"
    assert credentials["aws_session_token"] == "session_token"


def test_generate_role_session_name():
    dag = DAG("a-test-dag")
    task = airflow_docker.operator.Operator(
        dag=dag,
        task_id="some-task",
        image="hello-world",
        start_date=datetime.datetime(2019, 2, 14, 15),
    )
    ti = TaskInstance(task=task, execution_date=datetime.datetime(2019, 2, 14, 15))
    dag_run = DagRun(dag_id=dag.dag_id)
    dag_run.id = 5

    context = {"dag": dag, "task_instance": ti, "dag_run": dag_run}

    session_name = airflow_docker.ext.aws.role_assumption.generate_role_session_name(
        context
    )
    assert "5__1__some-task" == session_name


def test_generate_role_session_name_long_task_id():
    dag = DAG("a-test-dag")
    task = airflow_docker.operator.Operator(
        dag=dag,
        task_id="some-task-id-that-is-very-long-way-past-the-64-character-limit-foo-bar-baz",
        image="hello-world",
        start_date=datetime.datetime(2019, 2, 14, 15),
    )
    ti = TaskInstance(task=task, execution_date=datetime.datetime(2019, 2, 14, 15))
    dag_run = DagRun(dag_id=dag.dag_id)
    dag_run.id = 5

    context = {"dag": dag, "task_instance": ti, "dag_run": dag_run}

    session_name = airflow_docker.ext.aws.role_assumption.generate_role_session_name(
        context
    )
    assert (
        "5__1__some-task-id-that-is-very-long-way-past-the-64-character-l"
        == session_name
    )
