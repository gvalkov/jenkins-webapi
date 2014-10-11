SHELL := python

JENKINS_WAR_URL := http://mirrors.jenkins-ci.org/war/latest/jenkins.war
JENKINS_CLI_JAR := tests/tmp/latest/jenkins-cli.jar
JENKINS_DESTDIR := tests/tmp/latest
JENKINS_ADDR    := localhost
JENKINS_PORT    := 60888
JENKINS_CPORT   := 60887

start-jenkins:
	config = {
	    'url': '$(JENKINS_WAR_URL)',
	    'destdir': '$(JENKINS_DESTDIR)',
	    'addr': '$(JENKINS_ADDR)',
	    'port': $(JENKINS_PORT),
	    'cport': $(JENKINS_CPORT),
	}

	from tests.install import JenkinsInstall
	ji = JenkinsInstall(**config)
	ji.bootstrap() ; print()
	ji.start() ; print()
	ji.wait()

remove-jobs:
	url = 'http://$(JENKINS_ADDR):$(JENKINS_PORT)'
	from tests.refapi import JenkinsCLI
	cli = JenkinsCLI(url, '$(JENKINS_CLI_JAR)')

	for job in cli.list_jobs():
		cli.delete_job(job)

stop-jenkins:
	addr, port = '$(JENKINS_ADDR)', $(JENKINS_CPORT)
	from subprocess import check_call as run
	run('echo 0 | nc %s %s' % (addr, port), shell=True)

test:
	from subprocess import check_call as run
	run('py.test tests -xvs', shell=True)

coverage:
	from subprocess import check_call as run
	run('py.test --cov-report term-missing --cov  jenkins tests', shell=True)

.ONESHELL:
.PHONY: start-jenkins stop-jenkins test coverage remove-jobs
