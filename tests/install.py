# -*- coding: utf-8; -*-

import os
import time
import textwrap
import contextlib

from os.path import abspath, dirname, join as pjoin
from subprocess import STDOUT, Popen, CalledProcessError, call, check_call
from . utils import *


__all__ = ['JenkinsInstall']


#-----------------------------------------------------------------------------
class JenkinsInstall:
    def __init__(self, url, destdir, addr, port, cport, logfile=None):
        self.url = url
        self.port = port
        self.cport = cport
        self.addr = addr
        self.destdir = destdir

        self.logfile    = logfile if logfile else pjoin(self.destdir, 'jenkins.log')
        self.jenkinswar = pjoin(self.destdir, 'jenkins.war')
        self.jenkinscli = pjoin(self.destdir, 'jenkins-cli.jar')
        self.homedir    = pjoin(self.destdir, 'home')

        self.proc = None

    def __str__(self):
        return '<jenkins %s>' % self.homedir

    def bootstrap(self):
        msg1 = 'Bootsrapping Jenkins instance:'
        msg2 = '''\
        war:     %(url)s
        addr:    http://%(addr)s:%(port)s
        destdir: %(destdir)s
        cport:   %(cport)s
        ''' % self.__dict__

        green(msg1)
        print(textwrap.dedent(msg2))

        if not os.path.exists(self.destdir):
            green('Mkdir: %s' % self.destdir)
            os.makedirs(self.destdir)

        self.download()
        print()
        self.extractcli()

    def start(self):
        assert not self.proc
        cmd = '''\
        java -DJENKINS_HOME=%(homedir)s -jar %(jenkinswar)s \\
             --httpListenAddress=%(addr)s \\
             --httpPort=%(port)s \\
             --controlPort=%(cport)s''' % self.__dict__

        green('Starting Jenkins on %s:%s ... ' % (self.addr, self.port))
        print(textwrap.dedent(cmd))

        fh = open(self.logfile, 'w')
        self.proc = Popen(cmd, shell=True, stdout=fh, stderr=STDOUT)

    def stop(self):
        assert self.proc
        cmd = 'echo 0 | nc %s %s &>/dev/null' % (self.addr, self.cport)
        call(cmd, shell=True)
        green('Sending shutdown signal ...')
        print(cmd)
        self.proc.wait()
        self.proc = None

    def wait(self, retries=10):
        cmd = 'curl --retry 5 -s %s:%s &>/dev/null' % (self.addr, self.port)
        green('Waiting for Jenkins to start ...')
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
            green('Extracing jenkins-cli.jar from jenkins.war ...')
            print(cmd)
            call(cmd, shell=True)

    def download(self, overwrite=False):
        if not os.path.exists(self.jenkinswar) or overwrite:
            cmd = 'curl -# -L %s > %s' % (self.url, self.jenkinswar)
            green('Downloading jenkins.war ...')
            print(cmd)
            call(cmd, shell=True)

        # r = requests.get(self.url, stream=True)
        # with open(pjoin(self.destdir, 'jenkins.war'), 'wb') as fh:
        #     for chunk in r.iter_content(8096):
        #         fh.write(chunk)

    @contextlib.contextmanager
    def instance():
        a.bootstrap()
        a.start() ; print()
        a.wait()  ; print()
        yield
        a.stop()
