import time
import pytest

from util import *
from jenkins import Jenkins, Job, JenkinsError


def test_job_exists(api, ref, tmpjob):
    assert api.job_exists(tmpjob('test-1'))

def test_job_exists_fail(api, ref):
    assert api.job_exists('does not exist') == False
        
def test_job_create(api, ref, jobname_wf):
    api.job_create(jobname_wf, econfig_enc)
    time.sleep(1)
    assert ref.job_exists(jobname_wf)

def test_job_create_fail(api, ref, jobname):
    with pytest.raises(JenkinsError):
        api.job_create(jobname, 'not xml')

    ref.create_job(jobname, econfig_enc)
    with pytest.raises(JenkinsError):
        api.job_create(jobname, econfig_enc)

def test_job_copy(api, ref):
    ref.create_job('job-copy-src', econfig_enc)
    ref.create_job('job-copy-dst-1', econfig_enc)

    assert api.job_copy('job-copy-src', 'job-copy-dst').exists()
    assert api.job_config('job-copy-src') == api.job_config('job-copy-dst')

    with pytest.raises(JenkinsError):
        api.job_copy('job-copy-src', 'job-copy-dst-1')

def test_job_delete(api, ref, jobname):
    ref.create_job(jobname, econfig_enc)
    try:
        api.job_delete(jobname)
        assert True
    except JenkinsError:
        ref.delete_job(jobname)
        assert False

def test_job_enable(api, ref, tempjob):
    ref.disable_job(tempjob)
    api.job_enable(tempjob)
    assert Job(tempjob, api.server).enabled

def test_job_disable(api, ref, tempjob):
    ref.enable_job(tempjob)
    api.job_disable(tempjob)
    assert not Job(tempjob, api.server).enabled
