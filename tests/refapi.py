# -*- coding: utf-8; -*-

import os, fcntl

from abc import ABCMeta, abstractmethod
from select import select
from subprocess import STDOUT, PIPE, Popen, CalledProcessError, list2cmdline

from . utils import *


__all__ = 'JenkinsCLI'

#-----------------------------------------------------------------------------
class ReferenceAPI(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_jobs(self):
        pass

    @abstractmethod
    def delete_job(self, name):
        pass

    @abstractmethod
    def create_job(self, name, configxml):
        pass

    @abstractmethod
    def job_exists(self, name):
        pass

    @abstractmethod
    def disable_job(self, name):
        pass

    @abstractmethod
    def enable_job(self, name):
        pass

    @abstractmethod
    def create_view(self, name):
        pass


#-----------------------------------------------------------------------------
class JenkinsCLI(ReferenceAPI):
    def __init__(self, url, jar):
        self.cmd = ['java', '-jar', jar, '-s', url]

    def run(self, cmd, success_codes=[0], **kw):
        print('%s' % ' '.join(cmd))
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, **kw)
        out, err = p.communicate()
        if p.returncode not in success_codes:
            raise CalledProcessError(p.returncode, cmd)

        return out

    def list_jobs(self):
        green('\nListing jobs with jenkins-cli ...')
        cmd = self.cmd + ['list-jobs']
        return self.run(cmd).decode('utf8').splitlines()

    def delete_job(self, name):
        green('\nRemoving job "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['delete-job', name]
        return self.run(cmd, success_codes=[0, 255])

    def delete_view(self, name):
        green('\nRemoving view "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['delete-view', name]
        return self.run(cmd, success_codes=[0, 255])

    def create_job(self, name, configxml):
        green('\nCreating job "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['create-job', name]
        print('%s' % ' '.join(cmd))
        p = Popen(cmd, stdin=PIPE)
        out = p.communicate(input=configxml)
        return out

    def create_view(self, configxml):
        green('\nCreating view with jenkins-cli')
        cmd = self.cmd + ['create-view']
        print('%s' % ' '.join(cmd))
        p = Popen(cmd, stdin=PIPE)
        out = p.communicate(input=configxml)
        return out

    def job_exists(self, name):
        green('\nDetermining if job "%s" exists with jenkins-cli' % name)
        try:
            cmd = self.cmd + ['get-job', name]
            self.run(cmd)
            return True
        except CalledProcessError:
            return False

    def view_config(self, name):
        cmd = self.cmd + ['get-view', name]
        return self.run(cmd)

    def view_exists(self, name):
        green('\nDetermining if view "%s" exists with jenkins-cli' % name)
        try:
            self.view_config(name)
            return True
        except CalledProcessError:
            return False

    def disable_job(self, name):
        green('\nDisabling job "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['disable-job', name]
        return self.run(cmd)

    def enable_job(self, name):
        green('\nEnabling job "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['enable-job', name]
        return self.run(cmd)
