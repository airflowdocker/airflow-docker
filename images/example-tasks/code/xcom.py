import json


def push(data_to_push):
    return data_to_push


def pull(xcom_data):
    print(xcom_data)
    print(type(xcom_data))
    data = json.loads(xcom_data)
    for item in data:
        print("Got: {}".format(item))
