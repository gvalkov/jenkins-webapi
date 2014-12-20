# -*- coding: utf-8; -*-

from subprocess import STDOUT, PIPE, Popen, CalledProcessError
from functools import partial

from . utils import *


#-----------------------------------------------------------------------------
class JenkinsCLI:
    def __init__(self, url, jar):
        self.cmd = ['java', '-jar', jar, '-s', url]

        self.view_exists = partial(self.item_exists, 'view')
        self.node_exists = partial(self.item_exists, 'node')
        self.job_exists  = partial(self.item_exists, 'job')

        self.view_create = partial(self.item_create, 'view', None)
        self.node_create = partial(self.item_create, 'node', None)
        self.job_create  = partial(self.item_create, 'job')

        self.view_delete = partial(self.item_delete, 'view')
        self.node_delete = partial(self.item_delete, 'node')
        self.job_delete  = partial(self.item_delete, 'job')

        self.view_config = partial(self.item_config, 'view')
        self.node_config = partial(self.item_config, 'node')
        self.job_config  = partial(self.item_config, 'job')

    def item_delete(self, item, name):
        green('\nRemoving %s "%s" with jenkins-cli' % (item, name))
        cmd = self.cmd + ['delete-%s' % item, name]
        return run(cmd, success_codes=[0, 255])

    def item_create(self, item, name, configxml):
        green('\nCreating %s "%s" with jenkins-cli' % (item, name))
        cmd = self.cmd + ['create-%s' % item]
        if name:
            cmd.append(name)

        print('%s' % ' '.join(cmd))
        p = Popen(cmd, stdin=PIPE)
        out = p.communicate(input=configxml)
        return out

    def item_config(self, item, name):
        cmd = self.cmd + ['get-%s' % item, name]
        return run(cmd)

    def item_exists(self, item, name):
        green('\nDetermining if %s "%s" exists with jenkins-cli' % (item, name))
        try:
            self.item_config(item, name)
            return True
        except CalledProcessError:
            return False

    def job_disable(self, name):
        green('\nDisabling job "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['disable-job', name]
        return run(cmd)

    def job_enable(self, name):
        green('\nEnabling job "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['enable-job', name]
        return run(cmd)

    def jobs(self):
        green('\nListing jobs with jenkins-cli ...')
        cmd = self.cmd + ['list-jobs']
        return run(cmd).decode('utf8').splitlines()


#-----------------------------------------------------------------------------
def run(cmd, success_codes=[0], **kw):
    print('%s' % ' '.join(cmd))
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, **kw)
    out, err = p.communicate()
    if p.returncode not in success_codes:
        raise CalledProcessError(p.returncode, cmd)

    return out


__all__ = 'JenkinsCLI'
