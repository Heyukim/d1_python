'''
Implements serializaton and de-serialization for the MonitorList.
'''

# Stdlib.
import csv
import datetime
import os
import StringIO
import sys
import types
import urllib
import wsgiref.handlers
import time

try:
  import cjson as json
except:
  import json

# 3rd party.
# Lxml
try:
  from lxml import etree
except ImportError, e:
  sys.stderr.write('Import error: {0}\n'.format(str(e)))
  sys.stderr.write('Try: sudo apt-get install python-lxml\n')
  raise

try:
  import iso8601
except ImportError, e:
  sys.stderr.write('Import error: {0}\n'.format(str(e)))
  sys.stderr.write('Try: sudo apt-get install python-setuptools\n')
  sys.stderr.write(
    '     sudo easy_install http://pypi.python.org/packages/2.5/i/iso8601/iso8601-0.1.4-py2.5.egg\n'
  )
  raise

# MN API.
try:
  import d1common
  import d1common.exceptions
  import d1common.ext.mimeparser
  import d1common.util
except ImportError, e:
  sys.stderr.write('Import error: {0}\n'.format(str(e)))
  sys.stderr.write(
    'Try: svn co https://repository.dataone.org/software/cicore/trunk/api-common-python/src/d1common\n'
  )
  raise

try:
  import d1common.types.generated.monitorlist
except ImportError, e:
  sys.stderr.write('Import error: {0}\n'.format(str(e)))
  sys.stderr.write('Try: sudo easy_install pyxb\n')
  raise

#===============================================================================


class MonitorList(object):
  def __init__(self):
    self.serialize_map = {
      'application/json': self.serialize_null,
      'text/csv': self.serialize_null,
      'text/xml': self.serialize_xml,
      'application/xml': self.serialize_xml,
      'application/rdf+xml': self.serialize_null,
      'text/html': self.serialize_null,
      'text/log': self.serialize_null,
    }

    self.deserialize_map = {
      'application/json': self.deserialize_null,
      'text/csv': self.deserialize_null,
      'text/xml': self.deserialize_xml,
      'application/xml': self.deserialize_xml,
      'application/rdf+xml': self.deserialize_null,
      'text/html': self.deserialize_null,
      'text/log': self.deserialize_null,
    }

    self.pri = [
      #'application/json',
      #'text/csv',
      'text/xml',
      'application/xml',
      #'application/rdf+xml',
      #'text/html',
      #'text/log',
    ]

    self.monitorlist = d1common.types.generated.monitorlist.monitorList()

    #===============================================================================

  def serialize(self, accept='application/json', pretty=False, jsonvar=False):
    # Determine which serializer to use. If client does not supply accept, we
    # default to JSON.
    try:
      content_type = d1common.ext.mimeparser.best_match(self.pri, accept)
    except ValueError:
      # An invalid Accept header causes mimeparser to throw a ValueError.
      #sys_log.debug('Invalid HTTP_ACCEPT value. Defaulting to JSON')
      content_type = 'application/json'

    # Deserialize object
    return self.serialize_map[d1common.util.get_content_type(content_type)](
      pretty, jsonvar
    ), content_type

  def serialize_xml(self, pretty=False, jsonvar=False):
    return self.monitorlist.toxml()

  def serialize_null(self, doc, pretty=False, jsonvar=False):
    raise d1common.exceptions.NotImplemented(0, 'Serialization method not implemented.')

    #===============================================================================

  def deserialize(self, doc, content_type='application/json'):
    return self.deserialize_map[d1common.util.get_content_type(content_type)](doc)

  def deserialize_xml(self, doc):
    self.monitorList = d1common.types.generated.monitorlist.CreateFromDocument(doc)

  def deserialize_null(self, doc):
    raise d1common.exceptions.NotImplemented(0, 'Deserialization method not implemented.')
