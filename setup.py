#!/usr/bin/env python
# encoding: utf-8

from os.path import abspath, dirname, join
from setuptools import setup
from setuptools.command.test import test as TestCommand

classifiers = (
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'License :: OSI Approved :: BSD License',
    'Intended Audience :: Developers',
    'Operating System :: POSIX :: Linux',
)

kw = {
    'name'             : 'jenkins-webapi',
    'version'          : '0.2.0',
    'description'      : 'Package for interacting with the Jenkins ci server',
    'long_description' : open(join(abspath(dirname(__file__)), 'README.rst')).read(),
    'author'           : 'Georgi Valkov',
    'author_email'     : 'georgi.t.valkov@gmail.com',
    'license'          : 'Revised BSD License',
    'url'              : 'https://github.com/gvalkov/jenkins-webapi',
    'keywords'         : 'jenkins ci',
    'classifiers'      : classifiers,
    'py_modules'       : ['jenkins'],
    'install_requires' : ['requests>=2.2.1'],
    'tests_require'    : ['pytest', 'termcolor', 'pytest-cov', 'httmock'],
    'zip_safe'         : True,
}

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

kw['cmdclass'] = {'test': PyTest}

if __name__ == '__main__':
    setup(**kw)
