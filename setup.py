#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup


requires = [
    'requests>=2.7.0',
]

tests_require = [
    'pytest >= 2.6.3',
    'termcolor >= 1.1.0',
    'pytest-cov >= 1.8.0',
    'httmock >= 1.2.2',
]

classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'License :: OSI Approved :: BSD License',
    'Intended Audience :: Developers',
    'Operating System :: POSIX :: Linux',
]

kw = {
    'name':             'jenkins-webapi',
    'version':          '0.5.0',
    'description':      'Module for interacting with the Jenkins CI server',
    'long_description': open('README.rst').read(),
    'author':           'Georgi Valkov',
    'author_email':     'georgi.t.valkov@gmail.com',
    'license':          'Revised BSD License',
    'url':              'https://github.com/gvalkov/jenkins-webapi',
    'keywords':         'jenkins ci',
    'classifiers':      classifiers,
    'py_modules':       ['jenkins'],
    'install_requires': requires,
    'tests_require':    tests_require,
    'zip_safe':         True,
}

if __name__ == '__main__':
    setup(**kw)
