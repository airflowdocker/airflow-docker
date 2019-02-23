from airflow_docker_helper import client
import sys

client.branch_to_tasks(sys.argv[1])

print('In Branch')