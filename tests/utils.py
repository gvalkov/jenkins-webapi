from __future__ import print_function

import os
import re
import lxml.etree

here = os.path.abspath(os.path.dirname(__file__))

# a minimal job config.xml
job_config_fn = os.path.join(here, 'etc/empty-job-config.xml')
job_config = open(job_config_fn).read()
job_config_enc = job_config.encode('utf8')

# a minimal view config.xml
view_config_fn = os.path.join(here, 'etc/empty-view-config.xml')
view_config = open(view_config_fn).read()
view_config_enc = view_config.encode('utf8')

# a minimal node config.xml
node_config_fn = os.path.join(here, 'etc/empty-node-config.xml')
node_config = open(node_config_fn).read()
node_config_enc = node_config.encode('utf8')

re_encoding = re.compile(r'''encoding\s*?=\s*?["']([-A-Za-z0-9]+)["']''')
def get_xml_encoding(xml_string, default='utf8'):
	m = re_encoding.search(xml_string)
	if not m:
		return default
	return m.group(1)

def xml_c14n(xml_string):
	'''Convert an xml string to a canonical xml string.'''
	enc = get_xml_encoding(xml_string)
	xml = lxml.etree.fromstring(xml_string.encode(enc))
	return lxml.etree.tostring(xml, method='c14n')
