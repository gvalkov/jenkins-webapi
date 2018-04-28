# -*- coding: utf-8; -*-

import os
import time
import shutil
import textwrap
import contextlib
from subprocess import STDOUT, Popen, CalledProcessError, call, check_call

from .utils import *
from .refapi import JenkinsCLI


#-----------------------------------------------------------------------------
class JenkinsInstall:
    def __init__(self, url, destdir, host, port, cport, logfile=None):
        self.url = url
        self.port = port
        self.cport = cport
        self.host = host
        self.destdir = destdir

        self.logfile    = logfile if logfile else os.path.join(self.destdir, 'jenkins.log')
        self.jenkinswar = os.path.join(self.destdir, 'jenkins.war')
        self.jenkinscli = os.path.join(self.destdir, 'jenkins-cli.jar')
        self.homedir    = os.path.join(self.destdir, 'home')
        self.initdir    = os.path.join(self.homedir, 'init.groovy.d')
        self.plugindir  = os.path.join(self.homedir, 'plugins')

        self.proc = None

    def __str__(self):
        return '<jenkins %s>' % self.homedir

    def bootstrap(self):
        msg1 = 'Bootsrapping Jenkins instance:'
        msg2 = '''\
        war:     %(url)s
        host:    http://%(host)s:%(port)s
        destdir: %(destdir)s
        cport:   %(cport)s''' % self.__dict__

        print(msg1)
        print(textwrap.dedent(msg2))

        if not os.path.exists(self.destdir):
            print('Mkdir: %s' % self.destdir)
            os.makedirs(self.destdir)

        self.download()
        print()
        self.extractcli()

    def start(self):
        assert not self.proc

        cmd = '''\
        java -DJENKINS_HOME=%(homedir)s -jar %(jenkinswar)s \\
             --httpListenAddress=%(host)s \\
             --httpPort=%(port)s \\
             --controlPort=%(cport)s''' % self.__dict__

        print('Starting Jenkins on %s:%s ... ' % (self.host, self.port))
        print(textwrap.dedent(cmd))

        with open(self.logfile, 'w') as fh:
            self.proc = Popen(cmd, shell=True, stdout=fh, stderr=STDOUT)

    def stop(self):
        assert self.proc
        cmd = 'echo 0 | nc %s %s &>/dev/null' % (self.host, self.cport)
        call(cmd, shell=True)
        print('Sending shutdown signal ...')
        print(cmd)
        self.proc.wait()
        self.proc = None

    def wait(self, retries=10):
        cmd = 'curl --retry 5 -s %s:%s &>/dev/null' % (self.host, self.port)
        print('Waiting for Jenkins to start ...')
        for i in range(retries):
            print(cmd)
            try:
                check_call(cmd, shell=True)
                return True
            except CalledProcessError:
                pass
            time.sleep(1)
        return False

    def extractcli(self, overwrite=False):
        if not os.path.exists(self.jenkinscli) or overwrite:
            cmd = 'unzip -qqc %s WEB-INF/jenkins-cli.jar > %s' \
                  % (self.jenkinswar, self.jenkinscli)
            print('Extracing jenkins-cli.jar from jenkins.war ...')
            print(cmd)
            call(cmd, shell=True)

    def download(self, overwrite=False):
        if not os.path.exists(self.jenkinswar) or overwrite:
            cmd = 'curl -# -L %s > %s' % (self.url, self.jenkinswar)
            print('Downloading jenkins.war ...')
            print(cmd)
            call(cmd, shell=True)

    @contextlib.contextmanager
    def instance(self):
        self.bootstrap()
        self.start()
        print()

        self.wait()
        print()

        yield
        self.stop()


__all__ = ['JenkinsInstall']
