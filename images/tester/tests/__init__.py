import os

DAG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dags')
DAG_FILES = [
    f for f in os.listdir(DAG_PATH)
    if f.endswith('.py')
]
