import os

DAG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dags")
DAG_FILES = [
    os.path.join(*subdir.split(os.path.sep)[3:], file)
    for subdir, dirs, files in os.walk(DAG_PATH)
    for file in files
    if file.endswith(".py")
]
