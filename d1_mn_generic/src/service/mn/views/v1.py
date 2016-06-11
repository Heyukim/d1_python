#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2012 DataONE
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
''':mod:`views.v1`
==================

:Synopsis: REST call handlers for v1 of the DataONE Member Node APIs.
:Author: DataONE (Dahl)
'''
# Stdlib.
import datetime
import httplib
import logging
import os
import socket
import urlparse
import uuid

# Django.
import django.core.cache
from django.db.models import Sum
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseNotAllowed
from django.conf import settings

# DataONE APIs.
import d1_client.cnclient
import d1_client.object_format_info
import d1_common.checksum
import d1_common.const
import d1_common.date_time
import d1_common.types.exceptions
import d1_common.types.generated.dataoneTypes as dataoneTypes
#import d1_common.types.generated.dataoneErrors as dataoneErrors

# App.
import mn.auth
import mn.db_filter
import mn.event_log
import mn.models
import mn.node
import mn.psycopg_adapter
import mn.restrict_to_verb
import mn.sysmeta_store
import mn.sysmeta_validate
import mn.util
import mn.view_asserts
import mn.view_shared

# ==============================================================================
# Secondary dispatchers (resolve on HTTP verb)
# ==============================================================================


def dispatch_object_pid(request, pid):
  if request.method == 'GET':
    return get_object_pid(request, pid)
  elif request.method == 'HEAD':
    return head_object_pid(request, pid)
  elif request.method == 'PUT':
    return put_object_pid(request, pid)
  elif request.method == 'DELETE':
    return delete_object_pid(request, pid)
  else:
    return HttpResponseNotAllowed(['GET', 'HEAD', 'POST', 'PUT', 'DELETE'])


def dispatch_object(request):
  if request.method == 'GET':
    return get_object(request)
  elif request.method == 'POST':
    return object_post(request)
  else:
    return HttpResponseNotAllowed(['GET', 'POST'])

# ==============================================================================
# Public API
# ==============================================================================

# ------------------------------------------------------------------------------
# Public API: Tier 1: Core API
# ------------------------------------------------------------------------------


# Unrestricted access.
@mn.restrict_to_verb.get
def get_monitor_ping(request):
  '''MNCore.ping() → Boolean
  '''
  response = mn.view_shared.http_response_with_boolean_true_type()
  mn.view_shared.add_http_date_to_response_header(response, datetime.datetime.utcnow())
  return response


# Anyone can call getLogRecords but only objects to which they have read access
# or higher are returned. No access control is applied if called by trusted D1
# infrastructure.
@mn.restrict_to_verb.get
@mn.auth.assert_get_log_records_access
def get_log(request):
  '''MNCore.getLogRecords(session[, fromDate][, toDate][, pidFilter][, event]
  [, start=0][, count=1000]) → Log
  '''
  query = mn.models.EventLog.objects.order_by('-date_logged').select_related()
  if not mn.auth.is_trusted_subject(request):
    query = mn.db_filter.add_access_policy_filter(query, request, 'object__id')
  query = mn.db_filter.add_datetime_filter(
    query, request, 'date_logged', 'fromDate', 'gte'
  )
  query = mn.db_filter.add_datetime_filter(query, request, 'date_logged', 'toDate', 'lt')
  query = mn.db_filter.add_string_filter(query, request, 'event__event', 'event')
  query = mn.db_filter.add_string_begins_with_filter(
    query, request, 'object__pid', 'pidFilter'
  )
  query_unsliced = query
  query, start, count = mn.db_filter.add_slice_filter(query, request)
  return {
    'query': query,
    'start': start,
    'count': count,
    'total': query_unsliced.count(),
    'type': 'log'
  }


# Unrestricted access.
@mn.restrict_to_verb.get
def get_node(request):
  '''MNCore.getCapabilities() → Node
  '''
  n = mn.node.Node()
  return HttpResponse(n.get().toxml(), d1_common.const.CONTENT_TYPE_XML)

# ------------------------------------------------------------------------------
# Public API: Tier 1: Read API
# ------------------------------------------------------------------------------

# ObjectFormatInfo is expensive to create because it reads a csv file from
# disk. So it is created here, since this is not a class.
object_format_info = d1_client.object_format_info.ObjectFormatInfo()


def _content_type_from_format_id(format_id):
  try:
    return object_format_info.content_type_from_format_id(format_id)
  except KeyError:
    return d1_common.const.CONTENT_TYPE_OCTETSTREAM


def _add_object_properties_to_response_header(response, sciobj):
  response['Content-Length'] = sciobj.size
  response['Content-Type'] = _content_type_from_format_id(sciobj.format.format_id)
  response['Last-Modified'] = datetime.datetime.isoformat(sciobj.mtime)
  response['DataONE-formatId'] = sciobj.format.format_id
  response['DataONE-Checksum'] = '{0},{1}'.format(
    sciobj.checksum_algorithm.checksum_algorithm, sciobj.checksum
  )
  response['DataONE-SerialVersion'] = sciobj.serial_version
  mn.view_shared.add_http_date_to_response_header(response, datetime.datetime.utcnow())


@mn.auth.assert_read_permission
def get_object_pid(request, pid):
  '''MNRead.get(session, pid) → OctetStream
  '''
  mn.view_asserts.object_exists(pid)
  sciobj = mn.models.ScienceObject.objects.get(pid=pid)
  response = StreamingHttpResponse(
    _get_object_byte_stream(sciobj), _content_type_from_format_id(
      sciobj.format.format_id
    )
  )
  _add_object_properties_to_response_header(response, sciobj)
  # Log the access of this object.
  mn.event_log.read(pid, request)
  # Since the iterator that generates data for StreamingHttpResponse runs
  # after the view has returned, it is not protected by the implicit transaction
  # around a request. However, in the unlikely event that a request is made to
  # delete the object on disk that is being returned, Linux will only hide
  # the file this request releases its file handle.
  return response


def _get_object_byte_stream(sciobj):
  url_split = urlparse.urlparse(sciobj.url)
  if url_split.scheme in ('http', 'https'):
    return _get_object_byte_stream_remote(sciobj.url, url_split)
  return _get_object_byte_stream_local(sciobj.pid)


def _get_object_byte_stream_remote(url, url_split):
  # Handle 302 Found.
  try:
    conn = httplib.HTTPConnection(url_split.netloc, timeout=10)
    conn.connect()
    headers = {}
    mn.util.add_basic_auth_header_if_enabled(headers)
    conn.request('HEAD', url, headers=headers)
    remote_response = conn.getresponse()
    if remote_response.status == httplib.FOUND:
      url = remote_response.getheader('location')
  except httplib.HTTPException as e:
    raise d1_common.types.exceptions.ServiceFailure(
      0, 'HTTPException while checking for "302 Found"'
    )

  # Open the object to proxy.
  try:
    conn = httplib.HTTPConnection(url_split.netloc, timeout=10)
    conn.connect()
    headers = {}
    mn.util.add_basic_auth_header_if_enabled(headers)
    conn.request('GET', url, headers=headers)
    remote_response = conn.getresponse()
    if remote_response.status != httplib.OK:
      raise d1_common.types.exceptions.ServiceFailure(0,
        'HTTP server error while opening object for proxy. URL: {0} Error: {1}'\
        .format(url, remote_response.status))
  except httplib.HTTPException as e:
    raise d1_common.types.exceptions.ServiceFailure(
      0, 'HTTPException while opening object for proxy: {0}'.format(e)
    )

  # Return an iterator that iterates over the raw bytes of the object in chunks.
  return mn.util.fixed_chunk_size_iterator(remote_response)


def _get_object_byte_stream_local(pid):
  file_in_path = mn.util.store_path(settings.OBJECT_STORE_PATH, pid)
  # Can't use "with".
  file = open(file_in_path, 'rb')
  # Return an iterator that iterates over the raw bytes of the object in chunks.
  return mn.util.fixed_chunk_size_iterator(file)


@mn.restrict_to_verb.get
@mn.auth.assert_read_permission
def get_meta_pid(request, pid):
  '''MNRead.getSystemMetadata(session, pid) → SystemMetadata
  '''
  mn.view_asserts.object_exists(pid)
  mn.event_log.read(pid, request)
  sciobj = mn.models.ScienceObject.objects.get(pid=pid)
  return HttpResponse(
    mn.sysmeta_store.read_sysmeta_from_store(
      pid, sciobj.serial_version
    ),
    content_type=d1_common.const.CONTENT_TYPE_XML
  )


@mn.auth.assert_read_permission
def head_object_pid(request, pid):
  '''MNRead.describe(session, pid) → DescribeResponse
  '''
  mn.view_asserts.object_exists(pid)
  sciobj = mn.models.ScienceObject.objects.get(pid=pid)
  response = HttpResponse()
  _add_object_properties_to_response_header(response, sciobj)
  # Log the access of this object.
  mn.event_log.read(pid, request)
  return response


@mn.restrict_to_verb.get
@mn.auth.assert_read_permission
def get_checksum_pid(request, pid):
  '''MNRead.getChecksum(session, pid[, checksumAlgorithm]) → Checksum
  '''
  mn.view_asserts.object_exists(pid)
  # MNRead.getChecksum() requires that a new checksum be calculated. Cannot
  # simply return the checksum from the sysmeta.
  #
  # If the checksumAlgorithm argument was not provided, it defaults to
  # the system wide default checksum algorithm.
  algorithm = request.GET.get(
    'checksumAlgorithm', d1_common.const.DEFAULT_CHECKSUM_ALGORITHM
  )
  try:
    h = d1_common.checksum.get_checksum_calculator_by_dataone_designator(algorithm)
  except KeyError:
    raise d1_common.types.exceptions.InvalidRequest(0,
      'Invalid checksum algorithm, "{0}". Supported algorithms are: {1}'\
      .format(algorithm, ', '
        .join(d1_common.checksum.dataone_to_python_checksum_algorithm_map.keys())))
  # Calculate the checksum.
  sciobj = mn.models.ScienceObject.objects.get(pid=pid)
  for bytes in _get_object_byte_stream(sciobj):
    h.update(bytes)
  # Log the access of this object.
  # TODO: look into log type other than 'read'
  mn.event_log.read(pid, request)
  # Return the checksum.
  checksum_serializer = dataoneTypes.checksum(h.hexdigest())
  #checksum_serializer.checksum =
  checksum_serializer.algorithm = algorithm
  checksum_xml = checksum_serializer.toxml()
  return HttpResponse(checksum_xml, d1_common.const.CONTENT_TYPE_XML)


@mn.restrict_to_verb.get
@mn.auth.assert_list_objects_access
def get_object(request):
  '''MNRead.listObjects(session[, fromDate][, toDate][, formatId]
  [, replicaStatus][, start=0][, count=1000]) → ObjectList
  '''
  # The ObjectList is returned ordered by mtime ascending. The order has
  # been left undefined in the spec, to allow MNs to select what is optimal
  # for them.
  query = mn.models.ScienceObject.objects.order_by('mtime').select_related()
  if not mn.auth.is_trusted_subject(request):
    query = mn.db_filter.add_access_policy_filter(query, request, 'id')
  query = mn.db_filter.add_datetime_filter(query, request, 'mtime', 'fromDate', 'gte')
  query = mn.db_filter.add_datetime_filter(query, request, 'mtime', 'toDate', 'lt')
  query = mn.db_filter.add_string_filter(query, request, 'format__format_id', 'formatId')
  mn.db_filter.add_bool_filter(query, request, 'replica', 'replicaStatus')
  query_unsliced = query
  query, start, count = mn.db_filter.add_slice_filter(query, request)
  return {
    'query': query,
    'start': start,
    'count': count,
    'total': query_unsliced.count(),
    'type': 'object'
  }


@mn.auth.assert_trusted_permission
@mn.restrict_to_verb.post
def post_error(request):
  '''MNRead.synchronizationFailed(session, message)
  '''
  mn.view_asserts.post_has_mime_parts(request, (('file', 'message'), ))
  mn.view_asserts.xml_document_not_too_large(request.FILES['message'])
  synchronization_failed_xml = request.FILES['message'].read().decode('utf-8')
  try:
    synchronization_failed = d1_common.types.exceptions.deserialize(
      synchronization_failed_xml.encode('utf-8')
    )
  except d1_common.types.exceptions.DataONEExceptionException as e:
    # In v1, MNRead.synchronizationFailed() cannot return an InvalidRequest
    # to the CN. Can only log the issue and return a 200 OK.
    logging.error(
      'Received notification of synchronization error from CN but was unable '
      'to deserialize the DataONE Exception passed by the CN.\n'
      'Exception passed by CN: {0}\n'
      'Exception when deserializing: {1}\n'.format(
        synchronization_failed_xml.encode('utf-8'), str(e)
      )
    )
  else:
    logging.error(
      'Received notification of synchronization error from CN:\n{0}'
      .format(str(synchronization_failed))
    )
  return mn.view_shared.http_response_with_boolean_true_type()


@mn.restrict_to_verb.get
# Access control is performed within function.
def get_replica_pid(request, pid):
  '''MNReplication.getReplica(session, pid) → OctetStream
  '''
  mn.view_asserts.object_exists(pid)
  _assert_node_is_authorized(request, pid)
  sciobj = mn.models.ScienceObject.objects.get(pid=pid)
  response = HttpResponse()
  _add_object_properties_to_response_header(response, sciobj)
  response._container = _get_object_byte_stream(sciobj)
  response._is_str = False
  # Log the replication of this object.
  mn.event_log.replicate(pid, request)
  return response


def _assert_node_is_authorized(request, pid):
  try:
    client = d1_client.cnclient.CoordinatingNodeClient(settings.DATAONE_ROOT)
    client.isNodeAuthorized(request.primary_subject, pid)
  except socket.gaierror:
    raise d1_common.types.exceptions.ServiceFailure(
      0, 'getaddrinfo() failed for "{0}"'.format(settings.DATAONE_ROOT)
    )
  except d1_common.types.exceptions.DataONEException as e:
    raise d1_common.types.exceptions.NotAuthorized(
      0, 'A CN has not authorized the target MN, "{0}" to create a replica of "{1}".\n'
      'Exception received from the CN:\n{2}'.format(request.primary_subject, pid, str(e))
    )

# ------------------------------------------------------------------------------
# Public API: Tier 2: Authorization API
# ------------------------------------------------------------------------------


# Unrestricted.
@mn.restrict_to_verb.get
def get_is_authorized_pid(request, pid):
  '''MNAuthorization.isAuthorized(pid, action) -> Boolean
  '''
  if 'action' not in request.GET:
    raise d1_common.types.exceptions.InvalidRequest(
      0, 'Missing required parameter: "action"'
    )
  # Convert action string to action level. Raises InvalidRequest if the
  # action string is not valid.
  level = mn.auth.action_to_level(request.GET['action'])
  mn.auth.assert_allowed(request, level, pid)
  return mn.view_shared.http_response_with_boolean_true_type()


@mn.restrict_to_verb.post
@mn.auth.assert_trusted_permission
def post_refresh_system_metadata(request):
  '''MNStorage.systemMetadataChanged(session, pid, serialVersion,
                                     dateSysMetaLastModified) → boolean
  '''
  mn.view_asserts.post_has_mime_parts(
    request, (
      ('field', 'pid'),
      ('field', 'serialVersion'),
      ('field', 'dateSysMetaLastModified'),
    )
  )
  mn.view_asserts.object_exists(request.POST['pid'])
  refresh_queue = mn.models.SystemMetadataRefreshQueue()
  refresh_queue.object = mn.models.ScienceObject.objects.get(pid=request.POST['pid'])
  refresh_queue.serial_version = request.POST['serialVersion']
  refresh_queue.last_modified = d1_common.date_time.from_iso8601(
    request.POST['dateSysMetaLastModified']
  )
  refresh_queue.set_status('new')
  refresh_queue.save_unique()
  return mn.view_shared.http_response_with_boolean_true_type()

# ------------------------------------------------------------------------------
# Public API: Tier 3: Storage API
# ------------------------------------------------------------------------------

# Both create() and update() creates a new object. In both methods, the pid of
# the NEW object is passed in an MMP field (pid in create() and newPid in
# update()). Additionally, update() passes the pid of the OLD object (the one to
# be updated) in the URL.
#
# Locks and checks:
#
# create()
# - Check if subject is in whitelist for creating NEW objects on MN.
# - Obtain a write lock on the NEW pid
# - Check that the NEW pid does not already exist
# - Check that the caller has the right to create NEW objects on the MN
# - Check that the submitted SysMeta does NOT include obsoletes or obsoletedBy
#
# update()
# - If settings.REQUIRE_WHITELIST_FOR_UPDATE is True:
#   - Check if subject is in whitelist for creating NEW objects on MN.
# - Obtain a write lock on the NEW pid
# - Check that the OLD pid exists
# - Obtain a write lock on the OLD pid
# - Check that the caller has write permissions on the OLD object
# - If the submitted SysMeta includes obsoletes, check that it matches the
#   OLD pid.
#
# For convenience, the functions below do not perform the locking and checks
# in the same order as described above.
#
# At any point where an exception is raised, the changes made to the database
# are implicitly rolled back. Any files stored in the filesystem before the
# exception are orphaned and cleaned up later. Whenever a filesystem object
# (SysMeta) is updated, a new file is created, so that any subsequent exception
# and rollback does not cause the database and filesystem to fall out of sync.
#
# Exceptions when dealing with the filesystem are not handled. They will
# typically be caused by issues such as invalid filesystem permissions or the
# server having run out of disk space. Hence, they are considered to be internal
# server errors. In debug mode, GMN will forward the actual exceptions to the
# client, wrapped in DataONE ServiceFailure exceptions. In production, the
# actual exception is not included.


@mn.auth.decorator_assert_create_update_delete_permission
def object_post(request):
  '''MNStorage.create(session, pid, object, sysmeta) → Identifier
  '''
  mn.view_asserts.post_has_mime_parts(
    request, (('field', 'pid'), ('file', 'object'), ('file', 'sysmeta'))
  )
  sysmeta_xml = request.FILES['sysmeta'].read().decode('utf-8')
  sysmeta = mn.view_shared.deserialize_system_metadata(sysmeta_xml.encode('utf-8'))
  mn.view_asserts.obsoleted_by_not_specified(sysmeta)
  mn.view_asserts.obsoletes_not_specified(sysmeta)
  new_pid = request.POST['pid']
  _create(request, new_pid, sysmeta)
  return mn.view_shared.http_response_with_identifier_type(new_pid)


@mn.auth.assert_write_permission # OLD object
def put_object_pid(request, old_pid):
  '''MNStorage.update(session, pid, object, newPid, sysmeta) → Identifier
  '''
  if settings.REQUIRE_WHITELIST_FOR_UPDATE:
    mn.auth.assert_create_update_delete_permission(request)
  mn.util.coerce_put_post(request)
  mn.view_asserts.post_has_mime_parts(
    request, (('field', 'newPid'), ('file', 'object'), ('file', 'sysmeta'))
  )
  mn.view_asserts.pid_exists(old_pid)
  mn.view_asserts.pid_not_obsoleted(old_pid)
  mn.view_asserts.sci_obj_is_not_replica(old_pid)
  sysmeta_xml = request.FILES['sysmeta'].read().decode('utf-8')
  sysmeta = mn.view_shared.deserialize_system_metadata(sysmeta_xml.encode('utf-8'))
  mn.view_asserts.obsoletes_matches_pid_if_specified(sysmeta, old_pid)
  sysmeta.obsoletes = old_pid
  new_pid = request.POST['newPid']
  _create(request, new_pid, sysmeta)
  _set_obsoleted_by(old_pid, new_pid)
  return mn.view_shared.http_response_with_identifier_type(new_pid)


def _create(request, pid, sysmeta):
  mn.view_asserts.xml_document_not_too_large(request.FILES['sysmeta'])
  mn.view_asserts.obsoleted_by_not_specified(sysmeta)
  mn.sysmeta_validate.validate_sysmeta_against_uploaded(request, pid, sysmeta)
  mn.sysmeta_validate.update_sysmeta_with_mn_values(request, sysmeta)
  #d1_common.date_time.is_utc(sysmeta.dateSysMetadataModified)
  mn.view_shared.create(request, pid, sysmeta)


def _set_obsoleted_by(obsoleted_pid, obsoleted_by_pid):
  sciobj = mn.models.ScienceObject.objects.get(pid=obsoleted_pid)
  with mn.sysmeta_store.sysmeta(obsoleted_pid, sciobj.serial_version) as m:
    m.obsoletedBy = obsoleted_by_pid
    sciobj.serial_version = m.serialVersion
  sciobj.save()


# No locking. Public access.
@mn.restrict_to_verb.post
def post_generate_identifier(request):
  '''MNStorage.generateIdentifier(session, scheme[, fragment]) → Identifier
  '''
  mn.view_asserts.post_has_mime_parts(request, (('field', 'scheme'), ))
  if request.POST['scheme'] != 'UUID':
    raise d1_common.types.exceptions.InvalidRequest(
      0, 'Only the UUID scheme '
      'is currently supported'
    )
  fragment = request.POST.get('fragment', None)
  while True:
    pid = (fragment if fragment else '') + uuid.uuid4().hex
    if not mn.models.ScienceObject.objects.filter(pid=pid).exists():
      return mn.view_shared.http_response_with_identifier_type(pid)


@mn.auth.decorator_assert_create_update_delete_permission
def delete_object_pid(request, pid):
  '''MNStorage.delete(session, pid) → Identifier
  '''
  mn.view_asserts.object_exists(pid)
  sciobj = mn.models.ScienceObject.objects.get(pid=pid)
  url_split = urlparse.urlparse(sciobj.url)
  _delete_object_from_filesystem(url_split, pid)
  mn.sysmeta_store.delete_sysmeta_from_store(pid, sciobj.serial_version)
  _delete_object_from_database(sciobj)
  return mn.view_shared.http_response_with_identifier_type(pid)


def _delete_object_from_filesystem(url_split, pid):
  if url_split.scheme == 'file':
    sciobj_path = mn.util.store_path(settings.OBJECT_STORE_PATH, pid)
    try:
      os.unlink(sciobj_path)
    except EnvironmentError:
      pass


def _delete_object_from_database(sciobj):
  # By default, Django's ForeignKey emulates the SQL constraint ON DELETE
  # CASCADE. In other words, any objects with foreign keys pointing at the
  # objects to be deleted will be deleted along with them.
  #
  # TODO: This causes associated permissions to be deleted, but any subjects
  # that are no longer needed are not deleted. The orphaned subjects should
  # not cause any issues and will be reused if they are needed again.
  sciobj.delete()


@mn.restrict_to_verb.put
@mn.auth.assert_write_permission
def put_archive_pid(request, pid):
  '''MNStorage.archive(session, pid) → Identifier
  '''
  mn.view_asserts.object_exists(pid)
  mn.view_asserts.sci_obj_is_not_replica(pid)
  _set_archived_flag(pid)
  _remove_all_permissions_except_rights_holder(pid)
  return mn.view_shared.http_response_with_identifier_type(pid)


def _set_archived_flag(pid):
  sciobj = mn.models.ScienceObject.objects.get(pid=pid)
  with mn.sysmeta_store.sysmeta(pid, sciobj.serial_version) as m:
    m.archived = True
    sciobj.serial_version = m.serialVersion
    sciobj.archived = True
  sciobj.save()


def _remove_all_permissions_except_rights_holder(pid):
  mn.auth.set_access_policy(pid)

# ------------------------------------------------------------------------------
# Public API: Tier 4: Replication API.
# ------------------------------------------------------------------------------


@mn.restrict_to_verb.post
@mn.auth.assert_trusted_permission
def post_replicate(request):
  '''MNReplication.replicate(session, sysmeta, sourceNode) → boolean
  '''
  mn.view_asserts.post_has_mime_parts(
    request, (('field', 'sourceNode'), ('file', 'sysmeta'))
  )
  sysmeta_xml = request.FILES['sysmeta'].read().decode('utf-8')
  sysmeta = mn.view_shared.deserialize_system_metadata(sysmeta_xml)
  _assert_request_complies_with_replication_policy(sysmeta)
  mn.view_asserts.pid_does_not_exist(sysmeta.identifier.value())
  mn.view_asserts.pid_has_not_been_accepted_for_replication(sysmeta.identifier.value())
  _create_replication_work_item(request, sysmeta)
  return mn.view_shared.http_response_with_boolean_true_type()


def _assert_request_complies_with_replication_policy(sysmeta):
  if not settings.NODE_REPLICATE:
    raise d1_common.types.exceptions.InvalidRequest(
      0, 'This node does not currently accept replicas. Note that the replicate '
      'attribute in the node element of the Node document is set to false. '
      'To change, see NODE_REPLICATE in settings_site.py'
    )

  if settings.TIER < 4:
    raise d1_common.types.exceptions.InvalidRequest(
      0, 'This node has been set up as a tier {0} Node and so cannot accept '
      'replicas. Note that MNReplication is not included in the services '
      'list in the Node document. To change, see TIER in settings_site.py'
      .format(settings.TIER)
    )

  if settings.REPLICATION_MAXOBJECTSIZE != -1:
    if sysmeta.size > settings.REPLICATION_MAXOBJECTSIZE:
      raise d1_common.types.exceptions.InvalidRequest(
        0, 'This node does not allow objects of size larger than {0}. '
        'The size of this object is {1}. '
        'To change, see REPLICATION_MAXOBJECTSIZE in settings_site.py'
        .format(settings.REPLICATION_MAXOBJECTSIZE, sysmeta.size)
      )

  if settings.REPLICATION_SPACEALLOCATED != -1:
    total = _get_total_size_of_replicated_objects()
    if total > settings.REPLICATION_SPACEALLOCATED:
      raise d1_common.types.exceptions.InvalidRequest(
        0, 'The total size allowed for replicas on this node has been exceeded. '
        'Used: {0}. Allowed: {1}. '
        'To change, see REPLICATION_SPACEALLOCATED in settings_site.py'
        .format(total, settings.REPLICATION_MAXOBJECTSIZE)
      )

  if len(settings.REPLICATION_ALLOWEDNODE):
    if sysmeta.originMemberNode.value() not in settings.REPLICATION_ALLOWEDNODE:
      raise d1_common.types.exceptions.InvalidRequest(
        0, 'This node does not allow replicas from {0}. '
        'To change, see REPLICATION_ALLOWEDNODE in settings_site.py'
        .format(sysmeta.originMemberNode.value())
      )

  if len(settings.REPLICATION_ALLOWEDOBJECTFORMAT):
    if sysmeta.formatId.value() not in settings.REPLICATION_ALLOWEDOBJECTFORMAT:
      raise d1_common.types.exceptions.InvalidRequest(
        0, 'This node does not allow objects of format {0}. '
        'To change, see REPLICATION_ALLOWEDOBJECTFORMAT in settings_site.py'
        .format(sysmeta.formatId.value())
      )


def _get_total_size_of_replicated_objects():
  total = django.core.cache.cache.get('replicated_objects_total')
  if total is not None:
    return total
  total = mn.models.ScienceObject.objects.filter(replica=True)\
    .aggregate(Sum('size'))['size__sum']
  if total is None:
    total = 0
  django.core.cache.cache.set('replicated_objects_total', total)
  return total


def _create_replication_work_item(request, sysmeta):
  replication_item = mn.models.ReplicationQueue()
  replication_item.set_status('new')
  replication_item.set_source_node(request.POST['sourceNode'])
  replication_item.pid = sysmeta.identifier.value()
  replication_item.save()