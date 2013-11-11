#!/usr/bin/env python3

import requests

from requests import HTTPError
from requests.compat import quote
from requests.auth import HTTPBasicAuth


__all__ = 'Job', 'Jenkins', 'Server', 'JenkinsError'


class Job(object):
    '''Represents a jenkins job.'''

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
        if not self.exists():
            raise JenkinsError('job "%s" does not exist' % self.name)

    def exists(self):
        '''Determine if job exists.'''
        try:
            self.info
            return True
        except JenkinsError:
            return False

    def delete(self):
        '''Permanently remove job.'''

        self._not_exist_raise()
        url = 'job/%s/doDelete' % quote(self.name)

        self.server.post(url)
        if self.exists():
            raise JenkinsError('delete of job "%s" failed' % self.name)

    def enable(self):
        '''Enable job.'''
        self._not_exist_raise()
        url = 'job/%s/enable' % quote(self.name)
        self.server.post(url)

    def disable(self):
        '''Disable job.'''
        self._not_exist_raise()
        url = 'job/%s/disable' % quote(self.name)
        self.server.post(url)

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

        self.server.post(url, params=params)

    def reconfigure(self, newconfig):
        '''Update config.xml of an existing job.'''

        self._not_exist_raise()

        url = 'job/%s/config.xml' % self.name
        headers = {'Content-Type': 'text/xml'}
        params = {'name': name}
        res = server.post(url, data=newconfig, params=params, headers=headers)

    @property
    def enabled(self):
        return '<disabled>false</disabled>' in self.config

    @property
    def info(self):
        '''Fetch job information.'''

        url = 'job/%s/api/json?depth=0' % quote(self.name)
        err = 'job "%s" does not exist' % self.name
        return self.server.json(url, errmsg=err)

    @property
    def config(self):
        url = 'job/%s/config.xml' % quote(self.name)
        res = self.server.get(url)
        if res.status_code != 200 or res.headers.get('content-type', '') != 'application/xml':
            msg = 'fetching configuration for job "%s" did not return a xml document'
            raise JenkinsError(msg % self.name)
        return res.text

    @config.setter
    def config(self, newconfig):
        self.reconfigure(newconfig)

    @property
    def builds(self):
        return [Build(self, i['number']) for i in self.info['builds']]

    @property
    def buildnumbers(self):
        return [i['number'] for i in self.info['builds']]

    @classmethod
    def create(cls, name, configxml, server):
        '''Create a new Jenkins job.'''

        job = cls(name, server)
        if job.exists():
            raise JenkinsError('job "%s" already exists' % name)

        headers = {'Content-Type': 'text/xml'}
        params = {'name': name}
        res = server.post('createItem', data=configxml, params=params, headers=headers)

        if not res or res.status_code != 200:
            raise JenkinsError('create "%s" failed' % name, url=res.url)

        # if not job.exists():
        #     raise JenkinsError('create "%s" failed' % name, url=res.url)

    @classmethod
    def copy(cls, source, dest, server):
        '''Copy a Jenkins job.'''

        job = cls(source, server)
        newjob = cls(dest, server)

        if newjob.exists():
            raise JenkinsError('job "%s" already exists' % dest)

        if not job.exists():
            raise JenkinsError('job "%s" does not exist' % source)

        headers = {'Content-Type': 'text/xml'}
        params = {'name': dest, 'mode': 'copy', 'from': source}
        res = server.post('createItem', params=params, headers=headers)

        if not newjob.exists():
            msg = 'could not copy job "%s" to "%s"'
            raise JenkinsError(msg % (source, dest))

        return newjob


class Build(object):
    '''A representation of a Jenkins build.'''

    __slots__ = 'job', 'number'

    def __init__(self, job, number):
        self.job = job
        self.number = number

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%r, %r)' % (cls, self.job, self.number)

    def stop(self):
        url = 'job/%s/%d/stop' % (self.job.name, self.number)
        return self.job.post(url)


class Server(object):
    def __init__(self, url, username=None, password=None):
        self.url = url if url.endswith('/') else url + '/'
        self.auth = HTTPBasicAuth(username, password) if username else None

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%s)' % (cls, self.url)

    def urljoin(self, *args):
        return '%s%s' % (self.url, '/'.join(args))

    def post(self, url, **kw):
        res = requests.post(self.urljoin(url), auth=self.auth, **kw)
        return res

    def get(self, url, **kw):
        res = requests.get(self.urljoin(url), auth=self.auth, **kw)
        return res

    def json(self, url, errmsg=None, **kw):
        url = self.urljoin(url)
        try:
            res = requests.get(url, **kw)
            if not res:
                raise JenkinsError(errmsg)
            return res.json()
        except HTTPError:
            raise JenkinsError(errmsg)
        except ValueError:
            raise JenkinsError('unparsable json response')


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

    # convenience job api
    def job(self, name):
        return Job(name, self.server)

    def job_info(self, name):
        return self.job(name).info

    def job_exists(self, name):
        return self.job(name).exists()

    def job_delete(self, name):
        return self.job(name).delete()

    def job_enable(self, name):
        return self.job(name).enable()

    def job_enabled(self, name):
        return self.job(name).enabled

    def job_disable(self, name):
        return self.job(name).disable()

    def job_config(self, name):
        return self.job(name).config

    def job_reconfigure(self, name, newconfig):
        job = self.job(name)
        job.config = newconfig
        return job

    def job_build(self, name, parameters=None, token=None):
        return self.job(name).build(parameters, token)

    def job_create(self, name, config):
        return Job.create(name, config, self.server)

    def job_copy(self, source, dest):
        return Job.copy(source, dest, self.server)


class JenkinsError(Exception):
    '''General exception type for jenkins-API-related failures.'''

    def __init__(self, msg, url=None, **kw):
        super(JenkinsError, self).__init__(msg, **kw)
        self.url = url
