RELEASE_TYPE: major

* Replaced various dev requirements files with a single set of `dev` dependencies
* Removed host/container volume mounts and replaced them with pure docker volumes
* Added docker-based worker/container two-way communication
* Added an extension equivalent to the PythonOperator, for running a python callable in a user provided image.
* Updated `do_meta_operation` implementations to work with existing `airflow-docker-helper` and `python_callable` based mechanisms for two-way communication

Authors:

* Hunter Senft-Grupp

