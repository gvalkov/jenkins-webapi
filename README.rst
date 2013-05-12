Jenkins-webapi
==============

Jenkins-webapi is a library for programatically accessing Jenkins'
remote web API_. It has the following advantages over other similar
libraries:

* Supports Python versions 2.6 to 3.3.
* Has a comprehensive test suite.
* A consice and intuitive API.

This is a work in progress.

Tutorial
========

.. code-block:: python

   from jenkins import Jenkins, JenkinsError

   j = Jenkins('http://server:port', 'user1', 'pass1')

   for job in j.jobs:
       job.exists()

       job.disable()
       job.enable()
       job.enabled

       configxml = job.config     # fetch current config.xml
       job.config = newconfigxml  # reconfigure job

       info = job.info  # fetch job info

   j.job_create('job-name', configxml)
   job = j.job('job-name')
   job.exists() == j.job_exists('job-name')
   job.config == j.job_config('job-name')
   job.info == j.job_info('job-name')

   j.copy('job-name', 'job-new-name')
   j.build('job-name')
   j.build('job-name', {'option':'value'}, 'token')


Similar projects
----------------

* python-jenkins_
* autojenkins_
* jenkinsapi_


License
-------

Jenkins-webapi is released under the terms of the `New BSD License`_.

.. _API: https://wiki.jenkins-ci.org/display/JENKINS/Remote+access+API

.. _jenkinsapi: https://pypi.python.org/pypi/jenkinsapi
.. _python-jenkins: https://pypi.python.org/pypi/python-jenkins/
.. _autojenkins: https://pypi.python.org/pypi/autojenkins/
