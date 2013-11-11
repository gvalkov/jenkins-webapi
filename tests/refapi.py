from subprocess import STDOUT,  PIPE, Popen, CalledProcessError
from . util import *

__all__ = ['JenkinsCLI']


class JenkinsCLI(object):
    def __init__(self, url, jar, use_drip=False):
        self.url = url
        self.jar = jar
        self.cmd = ['java', '-jar', jar, '-s', url]
        if use_drip:
            self.cmd = [pjoin(here, 'bin/drip'), '-cp', jar, 'hudson.cli.CLI', '-s', url]

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
        green('\nRemoving "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['delete-job', name]
        return self.run(cmd, success_codes=[0, 255])

    def create_job(self, name, configxml):
        green('\nCreating "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['create-job', name]
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

    def disable_job(self, name):
        green('\nDisabling job "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['disable-job', name]
        return self.run(cmd)

    def enable_job(self, name):
        green('\nEnabling job "%s" with jenkins-cli' % name)
        cmd = self.cmd + ['enable-job', name]
        return self.run(cmd)
