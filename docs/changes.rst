.. _v2.1.0:

-------------------
v2.1.0 - 2021-02-10
-------------------

* Add configuration to the aws role assumption extension to set environment variables instead of writing a file.

Authors:

* Hunter Senft-Grupp

.. _v2.0.3:

-------------------
v2.0.3 - 2020-11-20
-------------------

Update the tester image to allow for non-dag files.

Authors:

* Dan Cardin

.. _v2.0.2:

-------------------
v2.0.2 - 2020-11-19
-------------------

Update config access to remove direct access to configuration method 'has_option', which has been deprecated.

Authors:

* Gordon Fierce

.. _v2.0.1:

-------------------
v2.0.1 - 2020-11-13
-------------------

No code changes.
Updated requirements. Relaxed boto3 range.

Authors:

* Gordon Fierce

.. _v2.0.0:

-------------------
v2.0.0 - 2020-09-18
-------------------

* Bumped airflow version to 1.10.9 and releasely version to >=1.1
* Added python-3.8-test step as dependency of coverage step

Authors:

* Hunter Senft-Grupp

.. _v1.1.4:

-------------------
v1.1.4 - 2020-04-23
-------------------

Pin versions in CI.

Authors:

* Gordon Fierce

.. _v1.1.3:

-------------------
v1.1.3 - 2019-10-25
-------------------

* Ensure dag tester test failures print out the reason why they failed.

Authors:

* Dan Cardin

.. _v1.1.2:

-------------------
v1.1.2 - 2019-10-24
-------------------

* Update airflow-queue-stats plugin to fix a bug in the backlog task count implementation.

Authors:

* Hunter Senft-Grupp

.. _v1.1.1:

-------------------
v1.1.1 - 2019-10-22
-------------------

* Added airflow-queue-stats to project. This provides a json endpoint to get queue and worker information.

Authors:

* Hunter Senft-Grupp

.. _v1.1.0:

-------------------
v1.1.0 - 2019-10-20
-------------------

* Added an aws role assumption extension to permit task level aws role assumption
* Added an 'extensions' tab to the airflow docker UI tab to view loaded extension docs
* Small fixes to eliminate noisy task log warnings

Authors:

* Hunter Senft-Grupp

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
