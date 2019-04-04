# airflow-docker
[![CircleCI](https://circleci.com/gh/huntcsg/airflow-docker.svg?style=svg)](https://circleci.com/gh/huntcsg/airflow-docker) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/fd30a7ce26094c2b9f2e4d80d671a3d0)](https://www.codacy.com/app/fool.of.god/airflow-docker?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=huntcsg/airflow-docker&amp;utm_campaign=Badge_Grade) [![codecov](https://codecov.io/gh/huntcsg/airflow-docker/branch/master/graph/badge.svg)](https://codecov.io/gh/huntcsg/airflow-docker)

## Description
An opinionated implementation of exclusively using airflow DockerOperators for all Operators.

## Default Operator

```python
from airflow_docker.operator import Operator

task = Operator(
    image='some-image:latest',
    ...
)

```

## Default Sensor

```python
from airflow_docker.operator import Sensor

sensor = Sensor(
    image='some-image:latest',
    ...
)
```

Task Code

```python
from airflow_docker_helper import client

client.sensor(True)
```

## Branch Operator

Dag Task 

```python
from airflow_docker.operator import BranchOperator

branching_task = BranchOperator(
    image='some-image:latest',
    ...
)
```

Task Code

```python
from airflow_docker_helper import client

client.branch_to_tasks(['task1', 'task2'])
```

## Short Circuit Operator

Dag Task 

```python
from airflow_docker.operator import ShortCircuitOperator

short_circuit = ShortCircuitOperator(
    image='some-image:latest',
    ...
)
```

Task Code

```python
from airflow_docker_helper import client

client.short_circuit()  # This task will short circuit if this function gets called
```

## Context Usage

Dag Task 

```python
from airflow_docker.operator import Operator

task = Operator(
    image='some-image:latest',
    provide_context=True,
    ...
)
```

Task Code

```python
from airflow_docker_helper import client

context = client.context()

```

## Configuration

The following operator defaults can be set under the `airflowdocker` namespace:

* force_pull (boolean true/false)
* auto_remove (boolean true/false)
* network_mode

For example, to set `force_pull` to False by default set the following environment variable like so:

```bash
export AIRFLOW__AIRFLOWDOCKER__FORCE_PULL=false

```
