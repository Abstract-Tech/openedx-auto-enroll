Open edX Auto Enroll
=====================

Open edX Auto Enroll is a Django plugin that enrolls newly registered users in courses selected from Django admin.

Features
--------

* Enable or disable automatic enrollment from Django admin.
* Add one or more Open edX course keys from Django admin.
* Choose the enrollment mode per course.
* Automatically enroll users when the Open edX ``STUDENT_REGISTRATION_COMPLETED`` event is emitted.

Getting Started with Development
--------------------------------

Please first see the Open edX documentation for `guidance on Python development`_ in Open edX plugin repositories.

Then follow the steps below to mount and install this plugin in a local Tutor-based Open edX instance:

.. code-block:: bash

    # Clone the repository.
    git clone git@github.com:Abstract-Tech/openedx-auto-enroll.git

    # Mount the repository into Tutor.
    tutor mounts add /path/to/openedx-plugins/openedx-auto-enroll

Tutor mounts the repository under ``/mnt/`` in the Open edX containers. Install the plugin from inside the LMS container:

.. code-block:: bash

    tutor dev exec lms bash
    cd /mnt/openedx-auto-enroll
    pip install -e .

Then run migrations from the Open edX platform directory:

.. code-block:: bash

    cd ~/edx-platform/
    ./manage.py lms migrate

After installation, open Django admin and configure:

* ``Auto enroll configuration``: enable or disable automatic enrollment globally.
* ``Auto enroll courses``: add the course keys that new users should be enrolled in.

Useful development commands:

.. code-block:: bash

    # Run tests locally inside this repository.
    tox -e django42

    # Build documentation.
    make docs

    # Re-run migrations after model changes.
    tutor dev exec lms bash
    cd ~/edx-platform/
    ./manage.py lms migrate

    # Open an LMS shell when debugging enrollment behavior.
    tutor dev exec lms bash
    cd ~/edx-platform/
    ./manage.py lms shell

Installation
------------

Install the package in the LMS environment and run migrations:

.. code-block:: bash

    pip install openedx-auto-enroll
    ./manage.py lms migrate openedx_auto_enroll

Tutor Deployment
----------------

To install this plugin in a Tutor-managed Open edX instance, add it to Tutor's ``OPENEDX_EXTRA_PIP_REQUIREMENTS`` configuration setting:

.. code-block:: yaml

    OPENEDX_EXTRA_PIP_REQUIREMENTS:
    - git+https://github.com/Abstract-Tech/openedx-auto-enroll.git@X.Y.Z

Then rebuild/relaunch and run migrations:

.. code-block:: bash

    tutor config save
    tutor local launch
    tutor local run lms ./manage.py lms migrate openedx_auto_enroll

For production environments, use the same extra pip requirement in your Tutor configuration, then rebuild the Open edX image and run migrations during deployment.

Configuration
-------------

In Django admin:

* Open ``Auto enroll configuration`` and set ``enabled``.
* Open ``Auto enroll courses`` and add the course keys new users should be enrolled in.

Course keys should use the normal Open edX format, for example ``course-v1:edX+DemoX+Demo_Course``.

How it Works
------------

The plugin registers a handler for the Open edX ``STUDENT_REGISTRATION_COMPLETED`` event. When a new user completes registration, the handler checks the global admin switch, loads all enabled auto-enroll course rows, and enrolls the user in each selected course through Open edX's ``CourseEnrollment.enroll`` API.

.. _guidance on Python development: https://docs.openedx.org/en/latest/developers/how-tos/get-ready-for-python-dev.html
