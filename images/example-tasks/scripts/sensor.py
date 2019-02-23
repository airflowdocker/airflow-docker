import random
import sys

from airflow_docker_helper import client


if 'FAIL' in sys.argv:
    client.sensor(False)
elif 'PASS' in sys.argv:
    client.sensor(True)
else:
    client.sensor(random.choice([True, False, False, False]))
