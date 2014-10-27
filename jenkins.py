#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import time
import requests

from requests import HTTPError
from requests.compat import quote
from requests.auth import HTTPBasicAuth


#-----------------------------------------------------------------------------
__all__ = 'Job', 'Jenkins', 'Server', 'JenkinsError', 'Build', 'View'


#-----------------------------------------------------------------------------
class Job(object):
    '''Represents a Jenkins job.'''

    __slots__ = 'name', 'server'

    def __init__(self, name, server):
        self.name = name
        self.server = server

    def __str__(self):
        return 'job:%r' % (self.name)

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%r)' % (cls, self.name)

    def _not_exist_raise(self):
        if not self.exists:
            raise JenkinsError('job "%s" does not exist' % self.name)

    def delete(self):
        '''Permanently remove job.'''
        self._not_exist_raise()
        url = 'job/%s/doDelete' % quote(self.name)

        res = self.server.post(url, throw=False)
        if self.exists:
            raise JenkinsError('delete of job "%s" failed' % self.name)
        return res

    def enable(self):
        '''Enable job.'''
        self._not_exist_raise()
        url = 'job/%s/enable' % quote(self.name)
        return self.server.post(url)

    def disable(self):
        '''Disable job.'''
        self._not_exist_raise()
        url = 'job/%s/disable' % quote(self.name)
        return self.server.post(url)

    def build(self, parameters=None, token=None):
        '''Trigger a build.'''
        self._not_exist_raise()

        params = {}
        if token:
            params['token'] = token

        if parameters:
            params.update(parameters)
            url = 'job/%s/buildWithParameters' % self.name
        else:
            url = 'job/%s/build' % self.name

        return self.server.post(url, params=params)

    def reconfigure(self, newconfig):
        '''Update the config.xml of an existing job.'''
        self._not_exist_raise()

        url = 'job/%s/config.xml' % self.name
        headers = {'Content-Type': 'text/xml'}
        params = {'name': self.name}
        return self.server.post(url, data=newconfig, params=params, headers=headers)

    @property
    def enabled(self):
        return '<disabled>false</disabled>' in self.config

    @property
    def exists(self):
        '''Check if job exists.'''
        try:
            self.info
            return True
        except HTTPError as e:
            if e.response.status_code == 404:
                return False
            raise
        except JenkinsError:
            return False

    @property
    def info(self):
        url = 'job/%s/api/json?depth=0' % quote(self.name)
        err = 'job "%s" does not exist' % self.name
        return self.server.json(url, errmsg=err)

    @property
    def config(self):
        url = 'job/%s/config.xml' % quote(self.name)
        res = self.server.get(url)
        if res.status_code != 200 or res.headers.get('content-type', '') != 'application/xml':
            msg = 'fetching configuration for job "%s" did not return an xml document'
            raise JenkinsError(msg % self.name)
        return res.text

    @config.setter
    def config(self, newconfig):
        self.reconfigure(newconfig)

    @property
    def config_etree(self):
        # The cost of `'lxml' in sys.modules' is negligible and is
        # preferable to having a hard dependency on lxml.
        from lxml import etree
        return etree.fromstring(self.config)

    @config_etree.setter
    def config_etree(self, newconfig):
        newconfig = newconfig.tostring(etree)
        self.reconfigure(newconfig)

    @property
    def builds(self):
        return [Build(self, i['number']) for i in self.info['builds']]

    def __last_build_helper(self, path):
        url = 'job/%s/%s/api/json' % (quote(self.name), path)
        res = self.server.json(url)
        return Build(self, res['number'])

    @property
    def last_build(self):
        return self.__last_build_helper('lastBuild')

    @property
    def last_stable_build(self):
        return self.__last_build_helper('lastStableBuild')

    @property
    def last_successful_build(self):
        return self.__last_build_helper('lastSuccessfulBuild')

    @property
    def buildnumbers(self):
        return [i['number'] for i in self.info['builds']]

    @classmethod
    def create(cls, name, configxml, server):
        '''Create a new Jenkins job.'''

        job = cls(name, server)
        if job.exists:
            raise JenkinsError('job "%s" already exists' % name)

        headers = {'Content-Type': 'text/xml'}
        params = {'name': name}
        res = server.post('createItem', data=configxml, params=params, headers=headers, throw=False)

        if not res or res.status_code != 200:
            raise JenkinsError('create "%s" failed' % name)
        else:
            res.raise_for_status()

        # if not job.exists:
        #     raise JenkinsError('create "%s" failed' % name, url=res.url)

    @classmethod
    def copy(cls, source, dest, server):
        '''Copy a Jenkins job.'''

        job = cls(source, server)
        newjob = cls(dest, server)

        if newjob.exists:
            raise JenkinsError('job "%s" already exists' % dest)

        if not job.exists:
            raise JenkinsError('job "%s" does not exist' % source)

        headers = {'Content-Type': 'text/xml'}
        params = {'name': dest, 'mode': 'copy', 'from': source}
        res = server.post('createItem', params=params, headers=headers)

        if not newjob.exists:
            msg = 'could not copy job "%s" to "%s"'
            raise JenkinsError(msg % (source, dest))

        return newjob


#-----------------------------------------------------------------------------
class View(object):
    '''Represents a Jenkins view.'''

    __slots__ = 'name', 'server'

    def __init__(self, name, server):
        self.name = name
        self.server = server

    def __str__(self):
        return 'view:%r' % self.name

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%r)' % (cls, self.name)

    def _not_exist_raise(self):
        if not self.exists:
            raise JenkinsError('view "%s" does not exist' % self.name)

    @property
    def exists(self):
        '''Check if view exists.'''
        try:
            self.info
            return True
        except HTTPError as e:
            if e.response.status_code == 404:
                return False
            raise
        except JenkinsError:
            return False

    @property
    def info(self):
        url = 'view/%s/api/json?depth=0' % quote(self.name)
        err = 'view "%s" does not exist' % self.name
        return self.server.json(url, errmsg=err)

    @property
    def config(self):
        url = 'view/%s/config.xml' % quote(self.name)
        res = self.server.get(url)
        if res.status_code != 200 or res.headers.get('content-type', '') != 'application/xml':
            msg = 'fetching configuration for view "%s" did not return an xml document'
            raise JenkinsError(msg % self.name)
        return res.text

    @config.setter
    def config(self, newconfig):
        self.reconfigure(newconfig)

    @property
    def config_etree(self):
        # The cost of `'lxml' in sys.modules' is negligible and is
        # preferable to having a hard dependency on lxml.
        from lxml import etree
        return etree.fromstring(self.config)

    @config_etree.setter
    def config_etree(self, newconfig):
        newconfig = newconfig.tostring(etree)
        self.reconfigure(newconfig)

    def delete(self):
        '''Permanently remove view.'''
        self._not_exist_raise()
        url = 'view/%s/doDelete' % quote(self.name)

        res = self.server.post(url, throw=False)
        if self.exists:
            raise JenkinsError('delete of view "%s" failed' % self.name)
        return res

    def reconfigure(self, newconfig):
        '''Update the config.xml of an existing view.'''
        self._not_exist_raise()

        url = 'view/%s/config.xml' % self.name
        headers = {'Content-Type': 'text/xml'}
        params = {'name': self.name}
        return self.server.post(url, data=newconfig, params=params, headers=headers)

    def remove_job(self, job):
        '''Remove job from view.'''

        if not self.exists:
            raise JenkinsError('view "%s" does not exist' % self.name)

        if not job.exists:
            raise JenkinsError('job "%s" does not exist' % job.name)

        url = 'view/%s/removeJobFromView' % self.name
        params = {'name': job.name}
        res = self.server.post(url, params=params)

        if not res.status_code == 200:
            msg = 'could not remove job "%s" from view "%s"'
            raise JenkinsError(msg % (job.name, self.name))

    def add_job(self, job):
        '''Add job to the view.'''

        if not self.exists:
            raise JenkinsError('view "%s" does not exist' % self.name)

        if not job.exists:
            raise JenkinsError('job "%s" does not exist' % job.name)

        url = 'view/%s/addJobToView' % self.name
        params = {'name': job.name}
        res = self.server.post(url, params=params)

        if not res.status_code == 200:
            msg = 'could not add job "%s" to view "%s"'
            raise JenkinsError(msg % (job.name, self.name))

    @classmethod
    def create(cls, name, configxml, server):
        '''Create a new Jenkins view.'''

        view = cls(name, server)
        if view.exists:
            raise JenkinsError('view "%s" already exists' % name)

        headers = {'Content-Type': 'text/xml'}
        params = {'name': name}
        res = server.post('createView', data=configxml, params=params, headers=headers, throw=False)

        if not res or res.status_code != 200:
            raise JenkinsError('create "%s" failed' % name)
        else:
            res.raise_for_status()


#-----------------------------------------------------------------------------
class Build(object):
    '''A representation of a Jenkins build.'''

    __slots__ = 'job', 'number'

    def __init__(self, job, number):
        self.job = job
        self.number = number

    @property
    def info(self):
        '''Get information about this build.'''
        url = 'job/%s/%d/api/json' % (self.job.name, self.number)
        return self.job.server.json(url, 'unable to retrieve info')

    @property
    def building(self):
        return self.info['building']

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%r, %r)' % (cls, self.job, self.number)

    def stop(self):
        url = 'job/%s/%d/stop' % (self.job.name, self.number)
        return self.job.server.post(url)

    def wait(self, interval=1, timeout=None):
        '''Wait for build to complete.'''
        start = time.time()
        while self.building:
            time.sleep(interval)
            if timeout and (time.time() - start) > timeout:
                break


#-----------------------------------------------------------------------------
class Server(object):
    def __init__(self, url, username=None, password=None):
        self.url = url if url.endswith('/') else url + '/'
        self.auth = HTTPBasicAuth(username, password) if username else None

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%s)' % (cls, self.url)

    def urljoin(self, *args):
        return '%s%s' % (self.url, '/'.join(args))

    def post(self, url, throw=True, **kw):
        res = requests.post(self.urljoin(url), auth=self.auth, **kw)
        throw and res.raise_for_status()
        return res

    def get(self, url, throw=True, **kw):
        res = requests.get(self.urljoin(url), auth=self.auth, **kw)
        throw and res.raise_for_status()
        return res

    def json(self, url, errmsg=None, throw=True, **kw):
        url = self.urljoin(url)
        try:
            res = requests.get(url, auth=self.auth, **kw)
            throw and res.raise_for_status()
            if not res:
                raise JenkinsError(errmsg)
            return res.json()
        except ValueError:
            raise JenkinsError('unparsable json response')


#-----------------------------------------------------------------------------
class Jenkins(object):
    def __init__(self, url, username=None, password=None):
        '''Create handle to Jenkins instance.'''

        self.server = Server(url, username, password)
        self.url = self.server.url

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%r)' % (cls, self.url)

    @property
    def info(self):
        '''Get information about this Jenkins instance.'''
        url = 'api/json'
        res = self.server.json(url, 'unable to retrieve info')
        return res

    @property
    def jobs(self):
        return [Job(i['name'], self.server) for i in self.info['jobs']]

    @property
    def jobnames(self):
        return [i['name'] for i in self.info['jobs']]

    #-------------------------------------------------------------------------
    # alternative job, view and build api
    def job(self, name):
        return Job(name, self.server)

    def view(self, name):
        return View(name, self.server)

    def build(self, name, number):
        name = name.name if isinstance(name, Job) else name
        return Build(name, number)

    #-------------------------------------------------------------------------
    def job_info(self, name):
        return self.job(name).info

    def job_exists(self, name):
        return self.job(name).exists

    def job_delete(self, name):
        return self.job(name).delete()

    def job_enable(self, name):
        return self.job(name).enable()

    def job_disable(self, name):
        return self.job(name).disable()

    def job_enabled(self, name):
        return self.job(name).enabled

    def job_config(self, name):
        return self.job(name).config

    def job_reconfigure(self, name, newconfig):
        job = self.job(name)
        job.config = newconfig
        return job

    def job_config_etree(self, name):
        return self.job(name).config_etree

    def job_reconfigure_etree(self, name, newconfig):
        job = self.job(name)
        job.config_etree = newconfig
        return job

    def job_build(self, name, parameters=None, token=None):
        return self.job(name).build(parameters, token)

    def job_builds(self, name):
        return self.job(name).builds

    def job_last_build(self, name):
        return self.job(name).last_build

    def job_last_stable_build(self, name):
        return self.job(name).last_stable_build

    def job_last_successful_build(self, name):
        return self.job(name).last_successful_build

    def job_create(self, name, config):
        return Job.create(name, config, self.server)

    def job_copy(self, source, dest):
        return Job.copy(source, dest, self.server)

    #-------------------------------------------------------------------------
    def view_exists(self, name):
        return self.view(name).exists

    def view_config(self, name):
        return self.view(name).config

    def view_reconfigure(self, name, newconfig):
        view = self.view(name)
        view.config = newconfig
        return view

    def view_config_etree(self, name):
        return self.view(name).config_etree

    def view_delete(self, name):
        return self.view(name).delete()

    def view_reconfigure_etree(self, name, newconfig):
        view = self.view(name)
        view.config_etree = newconfig
        return view

    def view_add_job(self, name, job_name):
        job = self.job(job_name)
        return self.view(name).add_job(job)

    def view_remove_job(self, name, job_name):
        job = self.job(job_name)
        return self.view(name).remove_job(job)

    def view_create(self, name, config):
        return View.create(name, config, self.server)

    job_exists.__doc__ = Job.exists.__doc__
    job_delete.__doc__ = Job.delete.__doc__
    job_enable.__doc__ = Job.enable.__doc__
    job_disable.__doc__ = Job.disable.__doc__
    job_reconfigure.__doc__ = Job.reconfigure.__doc__
    job_build.__doc__ = Job.build.__doc__
    job_create.__doc__ = Job.create.__doc__
    job_copy.__doc__ = Job.copy.__doc__

    view_exists.__doc__ = View.exists.__doc__
    view_add_job.__doc__ = View.add_job.__doc__
    view_remove_job.__doc__ = View.remove_job.__doc__
    view_create.__doc__ = View.create.__doc__
    view_delete.__doc__ = View.delete.__doc__


#-----------------------------------------------------------------------------
class JenkinsError(Exception):
    '''Exception type for Jenkins-API related failures.'''

    def __init__(self, msg):
        super(JenkinsError, self).__init__(msg)
        self.msg = msg


#-----------------------------------------------------------------------------
# uncomment to enable http logging
# try:
#     import logging, httplib
#     httplib.HTTPConnection.debuglevel = 1
# except ImportError:
#     import logging, http.client
#     http.client.HTTPConnection.debuglevel = 1
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger('requests.packages.urllib3')
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
