#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import time
import requests

from requests import HTTPError
from requests.compat import quote, json
from requests.auth import HTTPBasicAuth


#-----------------------------------------------------------------------------
__all__ = (
    'Job',
    'Jenkins',
    'Server',
    'JenkinsError',
    'Build',
    'View',
    'Node'
)

#-----------------------------------------------------------------------------
class _JenkinsBase(object):
    '''Base class for Jenkins objects.'''

    @property
    def baseurl(self):
        raise NotImplementedError()

    def url(self, path):
        return '%s/%s' % (self.baseurl, path)

    @property
    def info(self):
        url = self.url('api/json?depth=0')
        err = '%s does not exist' % str(self)
        return self.server.json(url, errmsg=err)

    @property
    def exists(self):
        '''Check if object exists.'''
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
    def config(self):
        url = self.url('config.xml')
        res = self.server.get(url)
        if res.status_code != 200 or res.headers.get('content-type', '') != 'application/xml':
            msg = 'fetching configuration for item "%s" did not return an xml document'
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
        return etree.fromstring(self.config.encode('utf8'))

    @config_etree.setter
    def config_etree(self, newconfig):
        newconfig = newconfig.tostring(etree)
        self.reconfigure(newconfig)

    def reconfigure(self, newconfig):
        '''Update the config.xml of an existing item.'''
        self._not_exist_raise()

        url = self.url('config.xml')
        headers = {'Content-Type': 'text/xml'}
        params = {'name': self.name}
        return self.server.post(url, data=newconfig, params=params, headers=headers)

    def _not_exist_raise(self):
        if not self.exists:
            raise JenkinsError('%s does not exist' % str(self))


#-----------------------------------------------------------------------------
class Job(_JenkinsBase):
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

    def __hash__(self):
        key = (self.name, self.server, self.__class__)
        return hash(key)

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and self.name == other.name \
               and self.server == other.server

    @property
    def baseurl(self):
        return 'job/%s' % quote(self.name)

    def delete(self):
        '''Permanently remove job.'''
        self._not_exist_raise()
        url = self.url('doDelete')
        res = self.server.post(url, throw=False)
        if self.exists:
            raise JenkinsError('delete of job "%s" failed' % self.name)
        return res

    def enable(self):
        '''Enable job.'''
        self._not_exist_raise()
        url = self.url('enable')
        return self.server.post(url)

    def disable(self):
        '''Disable job.'''
        self._not_exist_raise()
        url = self.url('disable')
        return self.server.post(url)

    def build(self, parameters=None, token=None):
        '''Trigger a build.'''
        self._not_exist_raise()

        params = {}
        if token:
            params['token'] = token

        if parameters:
            params.update(parameters)
            url = self.url('buildWithParameters')
        else:
            url = self.url('build')

        return self.server.post(url, params=params)

    @property
    def enabled(self):
        return not '<disabled>true</disabled>' in self.config

    @property
    def builds(self):
        return [Build(self, i['number']) for i in self.info['builds']]

    def __last_build_helper(self, path):
        url = self.url(path + '/api/json')
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
class View(_JenkinsBase):
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

    def __hash__(self):
        key = (self.name, self.server, self.__class__)
        return hash(key)

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and self.name == other.name \
               and self.server == other.server

    @property
    def baseurl(self):
        return 'view/%s' % quote(self.name)

    @property
    def jobs(self):
        return [Job(i['name'], self.server) for i in self.info['jobs']]

    @property
    def jobnames(self):
        return [i['name'] for i in self.info['jobs']]

    def delete(self):
        '''Permanently remove view.'''
        self._not_exist_raise()
        url = self.url('doDelete')
        res = self.server.post(url, throw=False)
        if self.exists:
            raise JenkinsError('delete of view "%s" failed' % self.name)
        return res

    def remove_job(self, job):
        '''Remove job from view.'''

        if not self.exists:
            raise JenkinsError('view "%s" does not exist' % self.name)

        if not job.exists:
            raise JenkinsError('job "%s" does not exist' % job.name)

        url = self.url('removeJobFromView')
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

        url = self.url('addJobToView')
        params = {'name': job.name}
        res = self.server.post(url, params=params)

        if not res.status_code == 200:
            msg = 'could not add job "%s" to view "%s"'
            raise JenkinsError(msg % (job.name, self.name))

    def has_job(self, job):
        '''Check if view contains job.'''
        config = self.config_etree
        jobs = config.xpath('jobNames/string/text()')
        job = getattr(job, 'name', job)
        return job in jobs

    def __contains__(self, job):
        return self.has_job(job)

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
class NodeLaunchMethod:
    COMMAND = 'hudson.slaves.CommandLauncher'
    JNLP    = 'hudson.slaves.JNLPLauncher'
    SSH     = 'hudson.plugins.sshslaves.SSHLauncher'
    WINDOWS_SERVICE = 'hudson.os.windows.ManagedWindowsServiceLauncher'

class Node(_JenkinsBase):
    '''Represents a Jenkins node.'''

    __slots__ = 'name', 'server'

    def __init__(self, name, server):
        self.name = name
        self.server = server

    def __str__(self):
        return '<node:%s>' % (self.name)

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%r)' % (cls, self.name)

    def __hash__(self):
        key = (self.name, self.server, self.__class__)
        return hash(key)

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and self.name == other.name \
               and self.server == other.server

    @property
    def baseurl(self):
        return 'computer/%s' % quote(self.name)

    @classmethod
    def create(cls, name, remotefs, server,
               num_executors=2,
               node_description=None,
               labels=None,
               exclusive=False,
               launcher=NodeLaunchMethod.COMMAND,
               launcher_params={}):
        '''
        :param name: name of node to create, ``str``
        :param remotefs: Remote root directory, ``str``
        :param num_executors: number of executors for node, ``int``
        :param node_description: Description of node, ``str``
        :param labels: Labels to associate with node, ``str``
        :param exclusive: Use this node for tied jobs only, ``bool``
        :param launcher: Slave launch method, ``NodeLaunchMethod|str``
        :param launcher_params: Additional launcher parameters, ``dict``
        '''
        node = cls(name, server)
        if node.exists:
            raise JenkinsError('node "%s" already exists' % name)

        mode = 'EXCLUSIVE' if exclusive else 'NORMAL'
        launcher_params['stapler-class'] = launcher

        inner_params = {
            'name': name,
            'nodeDescription': node_description,
            'numExecutors': num_executors,
            'remoteFS': remotefs,
            'labelString': labels,
            'mode': mode,
            'type': 'hudson.slaves.DumbSlave$DescriptorImpl',
            'retentionStrategy': {
                'stapler-class':
                'hudson.slaves.RetentionStrategy$Always'
            },
            'nodeProperties': {'stapler-class-bag': 'true'},
            'launcher': launcher_params
        }

        params = {
            'name': name,
            'type': 'hudson.slaves.DumbSlave$DescriptorImpl',
            'json': json.dumps(inner_params)
        }

        res = server.post('computer/doCreateItem', params=params, throw=False)

        if not res or res.status_code != 200:
            print(res.text)
            raise JenkinsError('create "%s" failed' % name)
        else:
            res.raise_for_status()

    def delete(self):
        '''Permanently remove node.'''
        self._not_exist_raise()
        url = self.url('doDelete')
        res = self.server.post(url, throw=False)
        if self.exists:
            raise JenkinsError('delete of node "%s" failed' % self.name)
        return res

    def reconfigure(self, newconfig):
        raise NotImplementedError


#-----------------------------------------------------------------------------
class Build(_JenkinsBase):
    '''Represents a Jenkins build.'''

    __slots__ = 'job', 'number', 'server'

    def __init__(self, job, number):
        self.job = job
        self.number = number
        self.server = self.job.server

    def __hash__(self):
        key = (self.job, self.number, self.server, self.__class__)
        return hash(key)

    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and self.job == other.job \
               and self.number == other.number \
               and self.server == other.server

    @property
    def baseurl(self):
        return '%s/%d' % (self.job.baseurl, self.number)

    @property
    def building(self):
        return self.info['building']

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%r, %r)' % (cls, self.job, self.number)

    def stop(self):
        url = self.url('stop')
        return self.server.post(url)

    def wait(self, tick=1, timeout=None):
        '''Wait for build to complete.'''
        start = time.time()
        while self.building:
            time.sleep(tick)
            if timeout and (time.time() - start) > timeout:
                break


#-----------------------------------------------------------------------------
class Server(object):
    def __init__(self, url, username=None, password=None, verify=True, cert=None):
        self.url = url if url.endswith('/') else url + '/'
        self.auth = HTTPBasicAuth(username, password) if username else None
        self.verify = verify
        self.cert = cert

        # These arguments will be passed in every call to requests.get|post().
        self.request_kw = {
            'auth': self.auth,
            'cert': cert,
            'verify': verify,
        }

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%s)' % (cls, self.url)

    def __hash__(self):
        key = (self.url, self.verify, self.cert, self.__class__,
               self.auth.username if self.auth else None,
               self.auth.password if self.auth else None)
        return hash(key)

    def __eq__(self, other):
        self_auth  = (self.auth.username, self.auth.password) if self.auth else None
        other_auth = (other.auth.username, other.auth.password) if other.auth else None

        return isinstance(other, self.__class__) \
            and self.url == other.url \
            and self.verify == other.verify \
            and self.cert == other.cert \
            and self_auth == other_auth

    def urljoin(self, *args):
        return '%s%s' % (self.url, '/'.join(args))

    def post(self, url, throw=True, **kw):
        kw = mergedict(self.request_kw, kw)
        res = requests.post(self.urljoin(url), **kw)
        throw and res.raise_for_status()
        return res

    def get(self, url, throw=True, **kw):
        kw = mergedict(self.request_kw, kw)
        res = requests.get(self.urljoin(url), **kw)
        throw and res.raise_for_status()
        return res

    def json(self, url, errmsg=None, throw=True, **kw):
        url = self.urljoin(url)
        kw = mergedict(self.request_kw, kw)
        try:
            res = requests.get(url, **kw)
            throw and res.raise_for_status()
            if not res:
                raise JenkinsError(errmsg)
            return res.json()
        except ValueError:
            raise JenkinsError('unparsable json response')


#-----------------------------------------------------------------------------
class Jenkins(object):
    def __init__(self, url, username=None, password=None, verify=True, cert=None):
        '''Create handle to Jenkins instance.'''

        self.server = Server(url, username, password, verify, cert)
        self.url = self.server.url

    def __repr__(self):
        cls = self.__class__.__name__
        return '%s(%r)' % (cls, self.url)

    def __hash__(self):
        return hash(self.server) ^ hash(self.__class__)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.server == other.server

    @property
    def info(self):
        '''Get information about this Jenkins instance.'''
        url = 'api/json'
        res = self.server.json(url, 'unable to retrieve info')
        return res

    @property
    def computer(self):
        '''Get information about the Jenkins build executors.'''
        url = 'computer/api/json'
        res = self.server.json(url, 'unable to retrieve info')
        return res

    @property
    def jobs(self):
        return list(self.xjobs)

    @property
    def xjobs(self):
        return (Job(i['name'], self.server) for i in self.info['jobs'])

    @property
    def jobnames(self):
        return [i['name'] for i in self.info['jobs']]

    @property
    def views(self):
        return [View(i['name'], self.server) for i in self.info['views']]

    @property
    def viewnames(self):
        return [i['name'] for i in self.info['views']]

    @property
    def nodes(self):
        return [Node(name, self.server) for name in self.nodenames]

    @property
    def nodenames(self):
        names = []
        for name in (comp['displayName'] for comp in self.computer['computer']):
            names.append(name if name != 'master' else '(master)')
        return names

    #-------------------------------------------------------------------------
    # alternative jenkins object api
    def job(self, name):
        return Job(name, self.server)

    def view(self, name):
        return View(name, self.server)

    def build(self, name, number):
        name = name.name if isinstance(name, Job) else name
        return Build(name, number)

    def node(self, name):
        return Node(name, self.server)

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
    def build_info(self, job, number):
        return self.build(job, number).info

    def build_isbuilding(self, job, number):
        return self.build(job, number).building

    def build_stop(self, job, number):
        return self.build(job, number).stop()

    def build_wait(self, job, number, interval=1, timeout=None):
        return self.build(job, number).wait()

    #-------------------------------------------------------------------------
    def view_exists(self, name):
        return self.view(name).exists

    def view_config(self, name):
        return self.view(name).config

    def view_jobs(self, name):
        return self.view(name).jobs

    def view_jobnames(self, name):
        return self.view(name).jobnames

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

    def view_has_job(self, name, job_name):
        job = self.job(job_name)
        return self.view(name).has_job(job)

    def view_remove_job(self, name, job_name):
        job = self.job(job_name)
        return self.view(name).remove_job(job)

    def view_create(self, name, config):
        return View.create(name, config, self.server)

    #-------------------------------------------------------------------------
    def node_exists(self, name):
        return Node(name, self.server).exists

    def node_create(self, name, remotefs, *args, **kw):
        return Node.create(name, remotefs, self.server, *args, **kw)

    def node_info(self, name):
        return Node(name, self.server).info

    def node_delete(self, name):
        return Node(name, self.server).delete()

    def node_config(self, name):
        return self.node(name).config

    def node_config_etree(self, name):
        return self.node(name).config_etree

    job_exists.__doc__ = Job.exists.__doc__
    job_delete.__doc__ = Job.delete.__doc__
    job_enable.__doc__ = Job.enable.__doc__
    job_disable.__doc__ = Job.disable.__doc__
    job_reconfigure.__doc__ = Job.reconfigure.__doc__
    job_build.__doc__ = Job.build.__doc__
    job_create.__doc__ = Job.create.__doc__
    job_copy.__doc__ = Job.copy.__doc__

    build_stop.__doc__ = Build.stop.__doc__
    build_wait.__doc__ = Build.wait.__doc__

    view_exists.__doc__ = View.exists.__doc__
    view_add_job.__doc__ = View.add_job.__doc__
    view_remove_job.__doc__ = View.remove_job.__doc__
    view_create.__doc__ = View.create.__doc__
    view_delete.__doc__ = View.delete.__doc__
    view_has_job.__doc__ = View.has_job.__doc__

    node_exists.__doc__ = Node.exists.__doc__
    node_create.__doc__ = Node.create.__doc__
    node_delete.__doc__ = Node.delete.__doc__


#-----------------------------------------------------------------------------
# Utility functions.
def mergedict(a, b):
    c = a.copy()
    c.update(b)
    return c

#-----------------------------------------------------------------------------
class JenkinsError(Exception):
    '''Exception type for Jenkins-API related failures.'''

    def __init__(self, msg):
        super(JenkinsError, self).__init__(msg)
        self.msg = msg


#-----------------------------------------------------------------------------
# Uncomment to enable http logging
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
