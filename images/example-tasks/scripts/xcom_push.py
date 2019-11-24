from airflow_docker_helper import client

client.xcom_push(key="foo", value={"bar": "baz"})
client.xcom_push(key="foo2", value={"bar2": "baz2"})

print("pushed")
