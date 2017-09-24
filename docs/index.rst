.. image:: img/logo.png
   :align: center
   :width: 30%


Synopsis
========

Jenkins-webapi is a minimal, no-frills, Python module for working with the
Jenkins remote access API_. Its main selling points are:

* Support for Python versions *2.6*, *2.7* and *>=3.3*.
* A comprehensive test suite.
* A concise and intuitive API.


Installing
==========

The latest stable version of *jenkins-webapi* can be installed from
pypi_:

.. code-block:: bash

    $ pip install jenkins-webapi

Alternatively, you may simply place the `jenkins.py`_ module anywhere in your
load path. Outside of the standard library, *jenkins-webapi* depends only on the
requests_ http client library.


Quick start
===========

**Connecting to Jenkins:**

.. code-block:: python

   >>> from jenkins import Jenkins, JenkinsError
   >>> j = Jenkins('http://server:port', 'username', 'password')

The constructor also accepts the ``verify`` and ``cert`` arguments which are
useful when accessing Jenkins over https. Please refer to the documentation_ of
the the requests_ library for more information.

**Working with jobs:**

.. code-block:: python

   >>> j.jobs
   [Job('master'), Job('develop'), Job('feature-one')]

   >>> j.job_exists('master')
   True

   >>> j.job_enabled('master')
   False

   >>> j.job_info('master')
   {'actions': [], 'buildable': False, 'builds': [], ...}

   >>> j.job_config('master')
   '<?xml version=\1.0\' encoding=\'UTF-8\'?>\n<projects>\n...'

   >>> j.job_config_etree('master')
   <Element project at 0x7fc4f564ab08>

   >>> j.job_disable('master')
   >>> j.job_enable('master')

   >>> j.job_build('master')
   >>> j.job_build('master', {'option': 'value'}, 'token')

   >>> j.job_create('new-job', configxml)
   >>> j.job_copy('old-job', 'new-job')
   >>> j.job_reconfigure('master', configxml)
   >>> j.job_reconfigure_etree('master', config_etree)


**Working with views:**

.. code-block:: python

   >>> j.view_create('view-name', configxml)

   >>> j.view_exists('view-name')
   >>> j.view_delete('view-name')

   >>> j.view_config('view-name')
   >>> j.view_config_etree('view-name')

   >>> j.view_reconfigure('view-name', configxml)
   >>> j.view_reconfigure_etree('view-name', config_etree)

   >>> j.view_jobs()
   >>> j.view_add_job('view-name', 'job-name')
   >>> j.view_has_job('view-name', 'job-name')
   >>> j.view_remove_job('view-name', 'job-name')


**Working with builds:**

.. code-block:: python

   >>> j.job_builds('master')
   [Build(Job('master'), 1)]

   >>> j.job_last_build('master')
   >>> j.job_last_stable_build('master')
   >>> j.job_last_successful_build('master')
   [Build(Job('master'), 1)]

   >>> j.build_info('master', 1)
   {timestamp': 1394313822651, 'result': 'SUCCESS', ...}

   >>> j.build_running('master', 1)
   True

   >>> j.build_wait()
   >>> j.build_wait(interval=5, timeout=60)


**Working with nodes:**

.. code-block:: python

   >>> j.nodes
   >>> j.nodenames
   >>> j.computer
   >>> j.node_create('node-name', '/workdir')

   >>> j.node_exists('node-name')
   >>> j.node_delete('node-name')

   >>> j.node_config('node-name')
   >>> j.node_config_etree('node-name')

   >>> j.node_info('node-name')


**Job objects:**

   >>> master = j.job('master')
   >>> master.name
   >>> master.info
   >>> master.config
   >>> master.config_etree
   >>> master.enabled
   >>> master.exists
   >>> master.builds
   >>> master.last_build
   >>> master.last_stable_build
   >>> master.last_successful_build
   >>> master.buildnumbers

   >>> master.delete()
   >>> master.enable()
   >>> master.disable()
   >>> master.reconfigure(newconfig)

   >>> new_master = Job.copy('master')
   >>> new_master.config = new_configxml
   >>> new_master.config_etree = new_configetree

**View objects:**

  >>> view = j.view('viewname')
  >>> 'job-name' in view
  >>> view.add_job(j.job('view'))

**Node objects:**

  >>> node = j.node('nodename')
  >>> node.config

Please refer to the auto-generated :doc:`API documentation <apidoc>`
for more information.


Similar projects
================

* python-jenkins_
* autojenkins_
* jenkinsapi_
* pyjenkins_

Jenkins-webapi was written for the `jenkins-autojobs`_ project in a time when
none of the above libraries offered Python 3k support.


License
=======

Jenkins-webapi is released under the terms of the `Revised BSD License`_.


.. _API:        https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API
.. _Jenkins:    http://jenkins-ci.org/
.. _pypi:       https://pypi.python.org/pypi/jenkins-webapi
.. _github:     https://github.com/gvalkov/jenkins-webapi
.. _jenkins.py: https://raw.githubusercontent.com/gvalkov/jenkins-webapi/master/jenkins.py
.. _requests:   http://docs.python-requests.org/en/latest/
.. _documentation: http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification

.. _jenkinsapi:     https://pypi.python.org/pypi/jenkinsapi
.. _python-jenkins: https://pypi.python.org/pypi/python-jenkins/
.. _autojenkins:    https://pypi.python.org/pypi/autojenkins/
.. _pyjenkins:      https://pypi.python.org/pypi/pyjenkins/
.. _jenkins-autojobs: http://jenkins-autojobs.readthedocs.org/en/latest/

.. _`Revised BSD License`: https://raw.github.com/gvalkov/jenkins-webapi/master/LICENSE
