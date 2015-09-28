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
    assert api.job_exists('does not exist') is False

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
    api.job_create(jobname_gc, job_config_enc)
    time.sleep(1)
    assert ref.job_exists(jobname_gc)

def test_job_create_fail(api, ref, jobname):
    with pytest.raises(JenkinsError):
        api.job_create(jobname, 'not xml')

    ref.job_create(jobname, job_config_enc)
    with pytest.raises(JenkinsError):
        api.job_create(jobname, job_config_enc)


#-----------------------------------------------------------------------------
def test_job_copy(api, ref):
    ref.job_create('job-copy-src', job_config_enc)
    ref.job_create('job-copy-dst-1', job_config_enc)

    assert api.job_copy('job-copy-src', 'job-copy-dst').exists
    assert api.job_config('job-copy-src').strip() == api.job_config('job-copy-dst').strip()

    with pytest.raises(JenkinsError):
        api.job_copy('job-copy-src', 'job-copy-dst-1')


#-----------------------------------------------------------------------------
def test_job_delete(api, ref, jobname):
    ref.job_create(jobname, job_config_enc)
    try:
        api.job_delete(jobname)
        assert True
    except JenkinsError:
        ref.job_delete(jobname)
        assert False


#----------------------------------------------------------------------------
def test_job_enable(api, ref, tmpjob_named):
    ref.job_disable(tmpjob_named)
    api.job_enable(tmpjob_named)
    assert Job(tmpjob_named, api.server).enabled

def test_job_disable(api, ref, tmpjob_named):
    ref.job_enable(tmpjob_named)
    api.job_disable(tmpjob_named)
    assert not Job(tmpjob_named, api.server).enabled


#-----------------------------------------------------------------------------
def test_view_exists(api, ref, tmpview):
    view = tmpview('Test')
    assert api.view_exists('Test')
    assert not api.view_exists('NoTest')

def test_view_add_remove_job(api, ref, tmpjob, tmpview):
    view = tmpview('Test')
    job = tmpjob('job-abc')

    api.view_add_job(view, job)
    assert '<string>job-abc</string>' in api.view_config(view)
    assert 'job-abc' in api.view_jobnames('Test')
    assert api.job('job-abc') in api.view_jobs('Test')

    api.view_remove_job(view, job)
    assert '<string>job-abc</string>' not in api.view_config(view)

def test_view_create_remove(api, ref):
    try:
        api.view_create('Test', view_config_enc)
        assert ref.view_exists('Test')
    finally:
        api.view_delete('Test')
        assert not ref.view_exists('Test')

#-----------------------------------------------------------------------------
def test_node_exists(api, ref, tmpnode):
    node = tmpnode('Test')
    assert api.node_exists('Test')
    assert not api.node_exists('NoTest')

def test_node_create_remove(api, ref):
    try:
        api.node_create('Test1', '/tmp/test')
        assert ref.node_exists('Test1')
        api.node_delete('Test1')
        assert not ref.node_exists('Test1')
    finally:
        if ref.node_exists('Test1'):
            ref.node_delete('Test1')

def test_node_config(api, ref, tmpnode):
    node = tmpnode('Test2')
    assert api.node_config('Test2').strip() == ref.node_config('Test2').strip().decode('utf8')
