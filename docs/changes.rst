.. _v1.0.0:

-------------------
v1.0.0 - 2019-10-19
-------------------

* Upgraded airflow from 1.10.2 to 1.10.5
* Dropped support for airflow on python 3.5 due to version imcompatibilities with airflow libraries.
* Updated default configuration files with necessary upgrading changes
* Added an example config.json in the example dags and turned on the EnvironmentPreset extension

Authors:

* Hunter Senft-Grupp

.. _v0.5.0:

-------------------
v0.5.0 - 2019-10-19
-------------------

* Install google_auth extra, so that google oauth authentication can be used in the UI
* rbac is turned on by default to make a more similar example setup
* Turned off circleci slack notifications except for master and release branches

Authors:

* Hunter Senft-Grupp

.. _v0.4.6:

-------------------
v0.4.6 - 2019-10-19
-------------------

* Updated codacy badges
* Added releasely to "dev" extra for releasely branch management
* Configured CI to use releasely

Authors:

* Hunter Senft-Grupp
