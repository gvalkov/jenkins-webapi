# -*- coding: utf-8; -*-

import re
import time
import pytest

from os.path import join as pjoin

from jenkins import Jenkins
from . install import JenkinsInstall
from . refapi import JenkinsCLI
from . utils import *


#-----------------------------------------------------------------------------
# Specify the Jenkins environments that we wish to test against.
environments = [
    {
        'url':  'http://mirrors.jenkins-ci.org/war/latest/jenkins.war',
        'addr': 'localhost',
        'port':  60888,
        'cport': 60887,
        'destdir': pjoin(here, 'tmp/latest'),
    },
    # {
    #     'url':  'http://mirrors.jenkins-ci.org/war-stable/latest/jenkins.war',
    #     'addr': 'localhost',
    #     'port':  60878,
    #     'cport': 60877,
    #     'destdir': pjoin(here, 'tmp/stable'),
    # },
]


#-----------------------------------------------------------------------------
def pytest_addoption(parser):
    parser.addoption('--reuse-jenkins', action='store_true',
                     help='do not send a shutdown signal to Jenkins upon exit')


#-----------------------------------------------------------------------------
@pytest.fixture(params=environments, scope='session')
def env(request):
    # Download and install jenkins.war
    ji = JenkinsInstall(**request.param)

    def start():
        print()
        ji.bootstrap()
        ji.start()
        print()
        ji.wait()

    if request.config.getoption('--reuse-jenkins'):
        green('Trying to connect to an already running Jenkins ...')
        if ji.wait(2):
            return ji
        else:
            start()
    else:
        start()
        request.addfinalizer(ji.stop)

    return ji

#-----------------------------------------------------------------------------
# A fixture to our api (the code we're trying to test)
@pytest.fixture(scope='module')
def api(env):
    return Jenkins('http://%(addr)s:%(port)s' % env.__dict__)

#-----------------------------------------------------------------------------
# A fixture to the reference api (implemented through jenkins-cli.jar)
@pytest.fixture(scope='module')
def ref(env):
    r = JenkinsCLI('http://%(addr)s:%(port)s' % env.__dict__, env.jenkinscli)

    green('Removing all jobs ...')
    for name in r.jobs():
        r.job_delete(name)

    return r

#-----------------------------------------------------------------------------
# Job names to test with.
job_names = ['test-job', 'test job spaces', 'проба-грешка']
@pytest.fixture(scope='function', params=job_names)
def jobname(request):
    return request.param

# Job names to test with and ensure that they don't exist upon completion.
@pytest.yield_fixture(scope='function')
def jobname_gc(jobname, ref, request):
    yield jobname
    ref.job_delete(jobname)

# A temporary job using the jobname fixture and the reference api.
@pytest.yield_fixture(scope='function')
def tmpjob_named(jobname, ref, request):
    ref.job_create(jobname, job_config_enc)
    yield jobname
    ref.job_delete(jobname)

#-----------------------------------------------------------------------------
# A temporary job to which we give a name. Uses the reference api.
@pytest.yield_fixture(scope='function')
def tmpjob(ref, request):
    job = TempJob(ref)
    yield job
    job.finalize()

@pytest.yield_fixture(scope='function')
def tmpview(ref, request):
    view = TempView(ref)
    yield view
    view.finalize()

@pytest.yield_fixture(scope='function')
def tmpnode(ref, request):
    node = TempNode(ref)
    yield node
    node.finalize()

class TempJob:
    def __init__(self, ref):
        self.ref = ref

    def __call__(self, name, config=job_config_enc):
        self.name = name
        self.ref.job_create(name, config)
        return name

    def finalize(self):
        self.ref.job_delete(self.name)
        time.sleep(0.1)

class TempJenkinsObject:
    def create(config):
        raise NotImplementedError

    def delete(config):
        raise NotImplementedError

    def __init__(self, ref):
        self.ref = ref

    def __call__(self, name, config=None):
        config = config if config else self.default_config
        config = re.sub('<name>.*</name>', '<name>%s</name>' % name, config)
        config = config.encode('utf8')
        self.name = name
        self.create(config)
        return name

    def finalize(self):
        self.delete(self.name)
        time.sleep(0.1)

class TempView(TempJenkinsObject):
    default_config = view_config

    def create(self, config):
        self.ref.view_create(config)

    def delete(self, name):
        self.ref.view_delete(name)

class TempNode(TempJenkinsObject):
    default_config = node_config

    def create(self, config):
        self.ref.node_create(config)

    def delete(self, name):
        self.ref.node_delete(name)
