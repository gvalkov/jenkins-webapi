import time
import pytest

from os.path import abspath, dirname, join as pjoin
from functools import partial

from jenkins import Jenkins, Job, JenkinsError
from install import JenkinsInstall
from refapi import JenkinsCLI
from util import *


environments = [
    (('url', 'http://mirrors.jenkins-ci.org/war/latest/jenkins.war'),
     ('destdir', pjoin(here, 'tmp/latest')),
     ('addr', 'localhost'),
     ('port', 60888),
     ('cport', 60887)),

    # (('url', 'http://mirrors.jenkins-ci.org/war-stable/latest/jenkins.war'),
    #  ('destdir', pjoin(here, 'tmp/stable')),
    #  ('addr', 'localhost'),
    #  ('port', 60878),
    #  ('cport', 60877)),
]


def pytest_addoption(parser):
    parser.addoption("--reuse-jenkins", action="store_true",
                     help="list of stringinputs to pass to test functions")


@pytest.fixture(params=environments, scope='session')
def env(request):
    ji = JenkinsInstall(**dict(request.param))

    def start():
        print()
        ji.bootstrap()
        ji.start() ; print ()
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

@pytest.fixture(scope='module')
def api(env):
    # print('Looking for a running Jenkins instance ...')
    return Jenkins('http://%(addr)s:%(port)s' % env.__dict__)

@pytest.fixture(scope='module')
def ref(env):
    # print('Looking for a running Jenkins instance ...')
    r = JenkinsCLI('http://%(addr)s:%(port)s' % env.__dict__, env.jenkinscli)

    green('Removing all jobs ...')
    for name in r.list_jobs():
        r.delete_job(name)

    return r

@pytest.fixture(scope='function', params=[
'test-job', 'test job spaces'])
def jobname(request):
    return request.param

@pytest.fixture(scope='function')
def jobname_wf(jobname, ref, request):
    request.addfinalizer(partial(ref.delete_job, jobname))
    return jobname

class TempJob(object):
    def __init__(self, ref):
        self.ref = ref

    def __call__(self, name, config=econfig_enc):
        self.name = name
        self.ref.create_job(name, config)
        return name

    def finalize(self):
        self.ref.delete_job(self.name)
        time.sleep(0.1)
        

@pytest.fixture(scope='function')
def tmpjob(ref, request):
    tmp = TempJob(ref)
    request.addfinalizer(tmp.finalize)
    return tmp

@pytest.fixture(scope='function')
def tempjob(jobname, ref, request):
    ref.create_job(jobname, econfig_enc)
    request.addfinalizer(partial(ref.delete_job, jobname))
    return jobname
