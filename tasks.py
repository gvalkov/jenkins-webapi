import os

from invoke import task

from tests.refapi import JenkinsCLI
from tests.install import JenkinsInstall


JENKINS_WAR_URL = 'http://mirrors.jenkins-ci.org/war/latest/jenkins.war'
JENKINS_CLI_JAR = 'tests/tmp/latest/jenkins-cli.jar'
JENKINS_HOST = 'localhost'
JENKINS_PORT = 60888
JENKINS_CPORT = 60887
JENKINS_DESTDIR = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'jenkins-webapi-tests/jenkins-latest')


@task(name='start-jenkins')
def start_jenkins(ctx):
    config = {
        'url':     JENKINS_WAR_URL,
        'destdir': JENKINS_DESTDIR,
        'host':    JENKINS_HOST,
        'port':    JENKINS_PORT,
        'cport':   JENKINS_CPORT,
    }

    ji = JenkinsInstall(**config)
    ji.bootstrap()
    ji.start()
    ji.wait()


@task(name='stop-jenkins')
def stop_jenkins(ctx):
    ctx.run('echo 0 | nc %s %s' % (JENKINS_HOST, JENKINS_CPORT))


@task(name='remove-jobs')
def remove_jobs(ctx):
    url = 'http://%s:%s' % (JENKINS_HOST, JENKINS_PORT)
    cli = JenkinsCLI(url, JENKINS_CLI_JAR)

    for job in cli.jobs():
        cli.delete_job(job)


@task
def test(ctx):
    ctx.run('py.test tests -xvs')


@task
def coverage(ctx):
    ctx.run('py.test --cov-report term-missing --cov jenkins tests')
