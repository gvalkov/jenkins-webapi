from __future__ import print_function

from os.path import abspath, dirname, join as pjoin
from termcolor import colored, cprint


here = abspath(dirname(__file__))

# a minimal config.xml 
econfig_fn = pjoin(here, 'etc/empty-job-config.xml')
econfig = open(econfig_fn).read()
econfig_enc = econfig.encode('utf8')

# output functions
green = lambda x: cprint(x, 'green')
red = lambda x: cprint(x, 'red')
