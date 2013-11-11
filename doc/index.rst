Introduction
============

Jenkins-webapi is a library for programatically accessing Jenkins'
remote web API_. It has the following advantages over other similar
libraries:

* Supports Python versions 2.6 to 3.3.
* Has a comprehensive test suite.
* A consice and intuitive API.

Usage
=====

.. code-block:: python

   >>> from jenkins import Jenkins, JenkinsError, Job

   >>> j = Jenkins('http://server:port', 'username', 'password')

   >>> j.jobs
   [Job('master'), Job('develop'), Job('feature/one')]

   >>> j.job('master')  # get job by name
   Job('master')

   >>> j.job('master').exists()
   >>> j.job_exists('master')
   True

   >>> j.job('master').disable()
   >>> j.job_disable('master')

   >>> j.job('master').enabled
   >>> j.job_enabled('master')
   False

   >>> j.job_build('master')
   >>> j.job('master').build()
   >>> j.job('master').build({'option':'value'}, 'token')

   >>> j.job('master').config
   >>> j.job_config('master')
   '<?xml version=\1.0\' encoding=\'UTF-8\'?>\n<projects>\n...'

   >>> j.job('master').config = newconfigxml
   >>> j.job_reconfigure('master', newconfigxml)

   >>> j.job('master').info
   >>> j.job_info('master')
   {'actions': [], 'buildable': False, 'builds': [], ...}

   >>> new = Job.create('new-job', configxml, j)
   >>> new = j.job_create('new-job', configxml)

   >>> copy = Job.copy('old-job', 'new-job', j)
   >>> copy = j.job_copy('old-job', 'new-job')

Installation
------------

The latest stable version of jenkins-webapi can be installed from
pypi_, while the development version can be installed from github_:

.. code-block:: bash

    $ pip install jenkins-webapi  # stable version
    $ pip install git+git://github.com/gvalkov/jenkins-webapi.git  # development version


Similar projects
----------------

* python-jenkins_
* autojenkins_
* jenkinsapi_


License
-------

Jenkins-webapi is released under the terms of the `Revised BSD License`_.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _API: https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API
.. _pypi: https://pypi.python.org/pypi/jenkins-webapi
.. _github: https://github.com/gvalkov/jenkins-webapi

.. _jenkinsapi: https://pypi.python.org/pypi/jenkinsapi
.. _python-jenkins: https://pypi.python.org/pypi/python-jenkins/
.. _autojenkins: https://pypi.python.org/pypi/autojenkins/
.. _`Revised BSD License`: https://raw.github.com/gvalkov/jenkins-webapi/master/LICENSE
