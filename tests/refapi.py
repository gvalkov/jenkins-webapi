# -*- coding: utf-8; -*-

import os, fcntl

from abc import ABCMeta, abstractmethod
from select import select
from subprocess import STDOUT, PIPE, Popen, CalledProcessError, list2cmdline

from utils import *


__all__ = 'JenkinsCLI', 'JenkinsCLIPersist'


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

# #-----------------------------------------------------------------------------
# class JenkinsCLIPersist(ReferenceAPI):
#     def __init__(self, url, jar):
#         self.url = url
#         self.jar = jar
#         self.exitsep = '### EXIT STATUS: '

#         cmd = ['java', '-cp', '%s:%s' % (jar, 'bin'), 'JenkinsCLIPersist']
#         # self.proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
#         self.proc = Popen(cmd, stdin=PIPE)

#         # fl = fcntl.fcntl(self.proc.stdout, fcntl.F_GETFL)
#         # fcntl.fcntl(self.proc.stdout, fcntl.F_SETFL, fl | os.O_NONBLOCK)

#     def close(self):
#         self.proc.stdin.close()

#     def read(self):
#         lines = []
#         while True:
#             r, w, e = select([self.proc.stdout], [], [])
#             if r:
#                 line = self.proc.stdout.read(512)
#                 line = line.decode('utf8').strip()

#                 if self.exitsep in line:
#                     ret = line.split(self.exitsep)[1]
#                     ret = int(ret) & 0xFF
#                     return lines, ret

#                 if line:
#                     lines.append(line)

#     def run(self, *cmd, stdin=None, success_codes=[0]):
#         cmd = ['-noKeyAuth', '-s', self.url] + list(cmd)
#         cmd = (list2cmdline(cmd) + '\n').encode('utf8')
#         self.proc.stdin.write(cmd)
#         self.proc.stdin.flush()

#         if stdin:
#             self.proc.stdin.write(stdin.encode('utf8'))
#             self.proc.stdin.flush()

#         lines, ret = self.read()
#         if ret not in success_codes:
#             self.proc.stdin.close()
#             raise CalledProcessError(ret, str(cmd))

#         return lines, ret

#     def list_jobs(self):
#         lines, ret = self.run('list-jobs')
#         return lines

#     def delete_job(self, name):
#         lines, ret = self.run('delete-job', name, success_codes=[0, 255])
#         return lines

#     def create_job(self, name, configxml):
#         lines, ret = self.run('create-job', name, stdin=configxml)
#         return lines

#     def job_exists(self, name):
#         try:
#             lines, ret = self.run('get-job', name)
#             return True
#         except CalledProcessError:
#             return False

#     def disable_job(self, name):
#         lines, ret = self.run('disable-job', name)
#         return lines

#     def enable_job(self, name):
#         lines, ret = self.run('enable-job', name)
#         return lines


# if __name__ == '__main__':
#     c = open('/home/gv/source/github/jenkins-webapi/tests/etc/empty-job-config.xml').read()
#     cli = JenkinsCLIPersist('http://localhost:60888', '/home/gv/source/github/jenkins-webapi/tests/tmp/latest/jenkins-cli.jar')

#     # print(cli.list_jobs())
#     # print(cli.job_exists('job-copy-dst'))
#     # print(cli.disable_job('job-copy-dst'))
#     # print(cli.enable_job('job-copy-dst'))
#     cli.create_job('new-job', c)
#     # print(cli.list_jobs())
#     cli.close()
#     cli.proc.wait()
