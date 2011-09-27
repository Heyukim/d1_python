#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright ${year}
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
'''
:mod:`sysmeta`
==============

:Synopsis:
  Utilities for manipulating System Metadata documents.
  
:Created: 2011-04-20
:Author: DataONE (Dahl)
:Dependencies:
  - python 2.6
'''

# Stdlib.
import datetime
import logging
import os
import sys
import StringIO
import urllib

# 3rd party.
try:
  import iso8601
  import lxml
except ImportError, e:
  sys.stderr.write('Import error: {0}\n'.format(str(e)))
  sys.stderr.write('Try: sudo apt-get install python-setuptools\n')
  sys.stderr.write(
    '     sudo easy_install http://pypi.python.org/packages/2.5/i/iso8601/iso8601-0.1.4-py2.5.egg\n'
  )
  raise

import xml.sax._exceptions
import pyxb.exceptions_

# App.
import settings

import d1_common.types.generated.dataoneTypes as dataoneTypes
import d1_common.types.exceptions

import util

# Schema entries for obsoletes and obsoletedBy.
#
#  <xs:element name="obsoletes" type="d1:Identifier" minOccurs="0"
#      maxOccurs="unbounded"/>
#  <xs:element name="obsoletedBy" type="d1:Identifier" minOccurs="0"
#      maxOccurs="unbounded"/>
#
# Example SysMeta doc:
#
# <ns1:systemMetadata>
#   <identifier>brownbear.const.xml</identifier>
#   <objectFormat>eml://ecoinformatics.org/eml-2.0.0</objectFormat>
#   <size>40969</size>
#   <submitter>test</submitter>
#   <rightsHolder>test</rightsHolder>
#   <checksum algorithm="MD5">63e73dfe2feab0e758072671d07d4cad</checksum>
#   <dateUploaded>2010-04-26T07:25:20.050518</dateUploaded>
#   <dateSysMetadataModified>1978-08-10T00:59:07</dateSysMetadataModified>
#   <originMemberNode>MN1</originMemberNode>
#   <authoritativeMemberNode>MN1</authoritativeMemberNode>
# </ns1:systemMetadata>


# TODO: Refactor into sysmeta class and replace scan through directory with
# direct read since the filename is now the PID.
def read_sysmeta(pid):
  '''Get a SysMeta object based on PID.
  :param pid: PID
  :type pid: Identifier
  :return: SysMeta filename and object.
  :rtype: (str, SystemMetadata)
  '''
  sysmeta_found = False
  for sysmeta_filename in os.listdir(settings.SYSMETA_STORE_PATH):
    sysmeta_path = os.path.join(settings.SYSMETA_STORE_PATH, sysmeta_filename)
    if not os.path.isfile(sysmeta_path):
      continue
    sysmeta_xml = open(sysmeta_path, 'rb').read()
    try:
      sysmeta_obj = dataoneTypes.CreateFromDocument(sysmeta_xml)
      if sysmeta_obj.identifier.value() == pid:
        sysmeta_found = True
        break
    except (pyxb.PyXBException, xml.sax.SAXParseException):
      logging.info('sysmeta_path({0}): Invalid SysMeta object'.format(sysmeta_path))

  if sysmeta_found == False:
    raise d1_common.types.exceptions.NotFound(0, 'Non-existing object was requested', pid)

  return sysmeta_filename, sysmeta_obj


def write_sysmeta(sysmeta_filename, sysmeta_obj):
  '''Write a SysMeta file. Will overwrite an existing file.
  :param sysmeta_filename: Filename to write
  :type sysmeta_filename: str
  :param sysmeta_obj: SysMeta object
  :type sysmeta_obj: SystemMetadata
  :return: ServiceFailure exception on error.
  :rtype: DataONEException
  '''
  sysmeta_path = os.path.join(settings.SYSMETA_STORE_PATH, sysmeta_filename)
  try:
    sysmeta_file = open(sysmeta_path, 'wb')
  except EnvironmentError as (errno, strerror):
    err_msg = 'Could not write sysmeta file\n'
    err_msg += 'I/O error({0}): {1}\n'.format(errno, strerror)
    raise d1_common.types.exceptions.ServiceFailure(0, err_msg)
  sysmeta_file.write(mn.util.pretty_xml(sysmeta_obj.toxml()))


def set_modified(sysmeta_obj, timestamp=None):
  '''Set the modified date in a SysMeta object.
  If timestamp is not provided, the current date and time is used.
  :param sysmeta_obj: SysMeta object
  :type sysmeta_obj: SystemMetadata
  :param timestamp: The new timestamp.
  :type timestamp: datetime.datetime
  :return: None
  :rtype: NoneType
  '''
  if timestamp is None:
    timestamp = datetime.datetime.now()
  sysmeta_obj.dateSysMetadataModified = datetime.datetime.isoformat(timestamp)

# SystemMetadata.obsoletes and SystemMetadata.obsoletedBy


def add_obsoletes(sysmeta_obj, pid):
  '''Add a PID to the list of "obsoletes" items in a SysMeta object.
  :param sysmeta_obj: SysMeta object
  :type sysmeta_obj: SystemMetadata
  :param pid: PID
  :type pid: Identifier
  :return: None
  :rtype: NoneType  
  '''
  pass


def add_obsoleted_by(sysmeta_obj, pid):
  '''Add a PID to the list of "obsoletes by" items in a SysMeta object.
  :param sysmeta_obj: SysMeta object
  :type sysmeta_obj: SystemMetadata
  :param pid: PID
  :type pid: Identifier
  :return: None
  :rtype: NoneType  
  '''
  pass


def get_replication_status_list(pid=None):
  raise d1_common.types.exceptions.NotImplemented(0, '')


def set_replication_status(status, node_ref, pid):
  raise d1_common.types.exceptions.NotImplemented(0, '')


def clear_replication_status(node_ref=None, pid=None):
  raise d1_common.types.exceptions.NotImplemented(0, '')

# ------------------------------------------------------------------------------
# Based on PyXB.
# ------------------------------------------------------------------------------


class sysmeta():
  '''Manipulate SysMeta objects in the SysMeta store.
  
  Preconditions:
    - Exclusive access to the given PID must be ensured by the caller.

  Example:
    with sysmeta('mypid') as m:
      m.accessPolicy = access_policy
  '''

  def __init__(self, pid, read_only=False):
    self.sysmeta_path = util.store_path(settings.SYSMETA_STORE_PATH, pid)
    self.read_only = read_only
    # Read.
    with open(self.sysmeta_path, 'rb') as file:
      sysmeta_str = file.read()
    # Deserialize.
    self.sysmeta_pyxb = dataoneTypes.CreateFromDocument(sysmeta_str)

  def __enter__(self):
    return self.sysmeta_pyxb

  def __exit__(self, exc_type, exc_value, traceback):
    if not self.read_only:
      self.save()
    return False

  def save(self, update_modified_datetime=True):
    '''Save the SysMeta object in the store.
    '''
    if update_modified_datetime:
      self.set_modified_datetime()
    # Write new SysMeta object to disk.
    with open(self.sysmeta_path, 'wb') as file:
      file.write(self.sysmeta_pyxb.toxml())

  def set_modified_datetime(self, timestamp=None):
    '''Update the dateSysMetadataModified field.
    '''
    if timestamp is None:
      timestamp = datetime.datetime.now()
    self.sysmeta_pyxb.dateSysMetadataModified = \
      datetime.datetime.isoformat(timestamp)

#  def set_owner(self, owner):
#      sysmeta_path = os.path.join(settings.SYSMETA_STORE_PATH,
#                              urllib.quote(pid, ''))
#  try:
#    file = open(sysmeta_path, 'rb')
#  except EnvironmentError:
#    return 'DATAONE_UNKNOWN'
#  with file: 
#    sysmeta_str = file.read()
#    sysmeta = dataoneTypes.SystemMetadata(sysmeta_str)
#    return sysmeta.rightsHolder
#  
#
#
#def test_replicate(src_node_ref, pid):
#  '''Build the mime multipart document that will be sent to /mn/replicate.
#  '''
#  files = [] 
#  sysmeta_filename, sysmeta_obj = get_sysmeta(pid)
#  files.append(('sysmeta', 'sysmeta', sysmeta_obj.toxml()))
#
#  fields = []
#  fields.append(('sourceNode', src_node_ref))
#
#  multipart_obj = d1_common.mime_multipart.multipart(fields, files)
#  
#  multipart_doc = StringIO.StringIO()
#  for part in multipart_obj:
#    multipart_doc.write(part)
#  
#   Set CN SysMeta replication status for object being replicated. 
#  set_replication_status('queued', src_node_ref, pid)
#
#  return multipart_doc.getvalue()
#
#def baseurl_by_noderef(node_ref):
#  try:
#    node_registry = open(os.path.join(settings.STATIC_STORE_PATH, 'nodeRegistry.xml')).read()
#  except EnvironmentError:
#    raise d1_common.types.exceptions.ServiceFailure(0, 'Missing static node registry file')
#
#  nodes = dataoneTypes.CreateFromDocument(node_registry)
#  
#  base_url = ''
#  for node in nodes.node:
#    if node.identifier == node_ref:
#      base_url = node.baseURL
#      break
#  if base_url == '':
#    raise d1_common.types.exceptions.InvalidRequest(0, 'Could not resolve node reference: {0}'.format(node_ref))
#
#  return base_url
#
#def get_sysmeta(pid):
#   Iterate over sysmeta objects.
#  sysmeta_found = False
#  for sysmeta_filename in os.listdir(settings.CN_SYSMETA_STORE_PATH):
#    sysmeta_path = os.path.join(settings.CN_SYSMETA_STORE_PATH, sysmeta_filename)
#    if not os.path.isfile(sysmeta_path):
#      continue
#    sysmeta_xml = open(sysmeta_path, 'rb').read()
#    try:
#      sysmeta_obj = dataoneTypes.CreateFromDocument(sysmeta_xml)
#      if sysmeta_obj.identifier.value() == pid:
#        sysmeta_found = True
#        break;  
#    except (xml.sax._exceptions.SAXParseException, pyxb.exceptions_.DOMGenerationError):
#      logging.info('sysmeta_path({0}): Invalid SysMeta object'.format(sysmeta_path))
#
#  if sysmeta_found == False:
#    raise d1_common.types.exceptions.NotFound(0, 'Non-existing object was requested', pid)
#        
#  return sysmeta_filename, sysmeta_obj
#
#def get_replication_status_list(pid=None):
#  status_list = []
#  
#   Iterate over sysmeta objects.
#  for sysmeta_filename in os.listdir(settings.CN_SYSMETA_STORE_PATH):
#    sysmeta_path = os.path.join(settings.CN_SYSMETA_STORE_PATH, sysmeta_filename)
#    if not os.path.isfile(sysmeta_path):
#      continue
#    sysmeta_xml = open(sysmeta_path, 'rb').read()
#    try:
#      sysmeta_obj = dataoneTypes.CreateFromDocument(sysmeta_xml)
#    except (xml.sax._exceptions.SAXParseException, pyxb.exceptions_.DOMGenerationError):
#      logging.info('sysmeta_path({0}): Invalid SysMeta object'.format(sysmeta_path))
#      continue
#
#    if pid is None or pid == sysmeta_obj.identifier.value():
#      for replica in sysmeta_obj.replica:
#        status_list.append((sysmeta_obj.identifier.value(), replica.replicaMemberNode,
#                          replica.replicationStatus, replica.replicaVerified))
#
#  return status_list
#
#def set_sysmeta(sysmeta_filename, sysmeta_obj):
#  sysmeta_path = os.path.join(settings.CN_SYSMETA_STORE_PATH, sysmeta_filename)
#  try:
#    sysmeta_file = open(sysmeta_path, 'wb')
#  except EnvironmentError as (errno, strerror):
#    err_msg = 'Could not write sysmeta file\n'
#    err_msg += 'I/O error({0}): {1}\n'.format(errno, strerror)
#    raise d1_common.types.exceptions.ServiceFailure(0, err_msg)
#  sysmeta_file.write(mn.util.pretty_xml(sysmeta_obj.toxml()))  
#
#def sysmeta_set_modified(sysmeta_obj, timestamp=None):
#  if timestamp is None:
#    timestamp = datetime.datetime.now()
#  sysmeta_obj.dateSysMetadataModified = datetime.datetime.isoformat(timestamp)
#
#def set_replication_status(status, node_ref, pid):
#  if status not in ('queued', 'requested', 'completed', 'invalidated'):
#    raise d1_common.types.exceptions.InvalidRequest(0, 'Invalid status: {0}'.format(status))
#
#  sysmeta_filename, sysmeta_obj = get_sysmeta(pid)
#  
#  # Find out if there is an existing Replica for this node.
#  replica_found = False
#  for replica in sysmeta_obj.replica:
#    if replica.replicaMemberNode == node_ref:
#      replica_found = True
#      break
#  if replica_found == True:
#    # Found existing Replica node. Update it with new status.
#    replica.replicationStatus = status
#  else:
#    # No existing Replica node for this node_ref. Create one.
#    replica = dataoneTypes.Replica()
#    replica.replicationStatus = status
#    replica.replicaMemberNode = node_ref
#    replica.replicaVerified = datetime.datetime.isoformat(datetime.datetime.now())
#    sysmeta_obj.replica.append(replica)
#
#  sysmeta_set_modified(sysmeta_obj)
#  set_sysmeta(sysmeta_filename, sysmeta_obj)
#
#def clear_replication_status(node_ref=None, pid=None):
#  removed_count = 0
#
#  # Iterate over sysmeta objects.
#  for sysmeta_filename in os.listdir(settings.CN_SYSMETA_STORE_PATH):
#    sysmeta_path = os.path.join(settings.CN_SYSMETA_STORE_PATH, sysmeta_filename)
#    if not os.path.isfile(sysmeta_path):
#      continue
#    sysmeta_xml = open(sysmeta_path, 'rb').read()
#    try:
#      sysmeta_obj = dataoneTypes.CreateFromDocument(sysmeta_xml)
#    except (xml.sax._exceptions.SAXParseException, pyxb.exceptions_.DOMGenerationError):
#      logging.info('sysmeta_path({0}): Invalid SysMeta object'.format(sysmeta_path))
#      continue
#
#    sysmeta_updated = False
#    if pid is None or pid == sysmeta_obj.identifier.value():
#      for i, replica in enumerate(sysmeta_obj.replica):
#        if node_ref is None or node_ref == replica.replicaMemberNode:
#          del sysmeta_obj.replica[i]
#          removed_count += 1
#          sysmeta_updated = True
#    
#    if sysmeta_updated == True:
#      set_sysmeta(sysmeta_filename, sysmeta_obj)
#      
#  return removed_count
