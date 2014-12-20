# -*- coding: utf-8; -*-

from __future__ import print_function

from os.path import abspath, dirname, join as pjoin
from termcolor import colored, cprint


#-----------------------------------------------------------------------------
here = abspath(dirname(__file__))

# a minimal job config.xml
job_config_fn = pjoin(here, 'etc/empty-job-config.xml')
job_config = open(job_config_fn).read()
job_config_enc = job_config.encode('utf8')

# a minimal view config.xml
view_config_fn = pjoin(here, 'etc/empty-view-config.xml')
view_config = open(view_config_fn).read()
view_config_enc = view_config.encode('utf8')

# a minimal node config.xml
node_config_fn = pjoin(here, 'etc/empty-node-config.xml')
node_config = open(node_config_fn).read()
node_config_enc = node_config.encode('utf8')

# output functions
green = lambda x: cprint(x, 'green')
red   = lambda x: cprint(x, 'red')
