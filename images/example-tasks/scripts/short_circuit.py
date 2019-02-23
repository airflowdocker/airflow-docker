from airflow_docker_helper import client
import sys

print('In short circuit')


if 'SHORT-CIRCUIT' in sys.argv:
    print('short circuiting')
    client.short_circuit()
