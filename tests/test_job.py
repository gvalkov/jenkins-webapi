# -*- coding: utf-8; -*-

import time
import pytest

# local imports
from . utils import *
from jenkins import Job, JenkinsError

# third-party imports
from requests import HTTPError
from httmock import all_requests, HTTMock


#-----------------------------------------------------------------------------
def test_job_exists(api, ref, tmpjob):
    job = tmpjob('test-1')
    assert api.job_exists(job)

def test_job_exists_fail(api, ref):
    assert api.job_exists('does not exist') == False

def test_job_exists_auth_fail(api, ref, tmpjob):
    @all_requests
    def response(url, request):
        return {'status_code': 400, 'content': 'error'}

    name = tmpjob('test-1')
    with HTTMock(response):
        with pytest.raises(HTTPError):
            api.job_exists(name)


#-----------------------------------------------------------------------------
def test_job_create(api, ref, jobname_gc):
    api.job_create(jobname_gc, econfig_enc)
    time.sleep(1)
    assert ref.job_exists(jobname_gc)

def test_job_create_fail(api, ref, jobname):
    with pytest.raises(JenkinsError):
        api.job_create(jobname, 'not xml')

    ref.create_job(jobname, econfig_enc)
    with pytest.raises(JenkinsError):
        api.job_create(jobname, econfig_enc)


#-----------------------------------------------------------------------------
def test_job_copy(api, ref):
    ref.create_job('job-copy-src', econfig_enc)
    ref.create_job('job-copy-dst-1', econfig_enc)

    assert api.job_copy('job-copy-src', 'job-copy-dst').exists
    assert api.job_config('job-copy-src').strip() == api.job_config('job-copy-dst').strip()

    with pytest.raises(JenkinsError):
        api.job_copy('job-copy-src', 'job-copy-dst-1')


#-----------------------------------------------------------------------------
def test_job_delete(api, ref, jobname):
    ref.create_job(jobname, econfig_enc)
    try:
        api.job_delete(jobname)
        assert True
    except JenkinsError:
        ref.delete_job(jobname)
        assert False


#-----------------------------------------------------------------------------
def test_job_enable(api, ref, tmpjob_named):
    ref.disable_job(tmpjob_named)
    api.job_enable(tmpjob_named)
    assert Job(tmpjob_named, api.server).enabled

def test_job_disable(api, ref, tmpjob_named):
    ref.enable_job(tmpjob_named)
    api.job_disable(tmpjob_named)
    assert not Job(tmpjob_named, api.server).enabled
