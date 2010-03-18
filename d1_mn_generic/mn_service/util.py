#!/usr/bin/env python
# -*- coding: utf-8 -*-
""":mod:`models` -- Utilities
=============================

:module: util
:platform: Linux
:synopsis: Utilities

.. moduleauthor:: Roger Dahl
"""

# Stdlib.
import os
import sys
import re
import glob
import time
import datetime
import stat
import json
import hashlib
import uuid
import exceptions

# Django.
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.core.management.base import NoArgsCommand
from django.core.management.base import CommandError
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import Http404
from django.template import Context
from django.template import loader
from django.shortcuts import render_to_response
from django.utils.html import escape

# 3rd party.
try:
  import iso8601
except ImportError, e:
  sys_log.error('Import error: %s' % str(e))
  sys_log.error('Try: sudo apt-get install python-setuptools')
  sys_log.error(
    '     sudo easy_install http://pypi.python.org/packages/2.5/i/iso8601/iso8601-0.1.4-py2.5.egg'
  )
  sys.exit(1)

# App.
import models
import settings
import auth
import sys_log
import util
import sysmeta
import access_log


def update_sysmeta():
  """Update a sysmeta object and reverify it"""
  # Log the update of this metadata object.
  #access_log.log(guid, 'set_metadata', request.META['REMOTE_ADDR'])
  pass


class fixed_chunk_size_file_iterator(object):
  """Create a file iterator that iterates through file-like object using fixed
  size chunks.
  """

  def __init__(self, flo, chunk_size=1024**2):
    self.flo = flo
    self.chunk_size = chunk_size

  def next(self):
    data = self.flo.read(self.chunk_size)
    if data:
      return data
    else:
      raise StopIteration

  def __iter__(self):
    return self


def raise_sys_log_http_404_not_found(err_msg):
  """Log message to system log and raise 404 with message.
  """
  sys_log.warning(err_msg)
  raise Http404(err_msg)


def return_sys_log_http_403_forbidden(err_msg):
  """Log message to system log and raise 403 with message.
  """
  sys_log.warning(err_msg)
  return HttpResponseForbidden(err_msg)


def return_sys_log_http_500_server_error(err_msg):
  sys_log.error(err_msg)
  return HttpResponseServerError(err_msg)


def file_to_dict(path):
  """Convert a sample MN object to dictionary."""

  try:
    f = open(path, 'r')
  except IOError as (errno, strerror):
    err_msg = 'Internal server error: Could not open: %s\n' % path
    err_msg += 'I/O error({0}): {1}'.format(errno, strerror)
    return_sys_log_http_500_server_error(err_msg)

  d = {}

  for line in f:
    m = re.match(r'(.+?):(.+)', f)
    if m:
      d[m.group(1)] = m.group(2)

  f.close()

  return d


def add_header(response, last_modified, content_length, content_type):
  """Add Last-Modified, Content-Length and Content-Type headers to page that
  returns information about a specific object or that contains list of objects.
  For a page that contains a list of objects, Size is the combined size of all
  objects listed."""

  response['Last-Modified'] = last_modified
  response['Content-Length'] = content_length
  response['Content-Type'] = content_type


def insert_association(guid1, guid2):
  """Create an association between two objects, given their guids."""

  try:
    o1 = models.Repository_object.objects.filter(guid=guid1)[0]
    o2 = models.Repository_object.objects.filter(guid=guid2)[0]
  except IndexError:
    err_msg = 'Internal server error: Missing object(s): %s and/or %s' % (guid1, guid2)
    return_sys_log_http_500_server_error(err_msg)

  association = models.Repository_object_associations()
  association.from_object = o1
  association.to_object = o2
  association.save()


def insert_object(object_class_name, guid, path):
  """Insert object into db."""

  # How Django knows to UPDATE vs. INSERT
  #
  # You may have noticed Django database objects use the same save() method
  # for creating and changing objects. Django abstracts the need to use INSERT
  # or UPDATE SQL statements. Specifically, when you call save(), Django
  # follows this algorithm:
  #
  # * If the object's primary key attribute is set to a value that evaluates
  #   to True (i.e., a value other than None or the empty string), Django
  #   executes a SELECT query to determine whether a record with the given
  #   primary key already exists.
  # * If the record with the given primary key does already exist, Django
  #   executes an UPDATE query.
  # * If the object's primary key attribute is not set, or if it's set but a
  #   record doesn't exist, Django executes an INSERT.

  try:
    f = open(path, 'r')
  except IOError as (errno, strerror):
    # Skip any file we can't get read access to.
    sys_log.warning('Skipped file because it couldn\'t be opened: %s' % path)
    sys_log.warning('I/O error({0}): {1}'.format(errno, strerror))
    return

  # Get hash of file.
  hash = hashlib.sha1()
  hash.update(f.read())

  # Get mtime in datetime.datetime.
  mtime = os.stat(path)[stat.ST_MTIME]
  mtime = datetime.datetime.fromtimestamp(mtime)

  # Get size.
  size = os.stat(path)[stat.ST_SIZE]

  f.close()

  # Set up the object class.
  c = models.Repository_object_class()
  try:
    object_class = models.Repository_object_class.objects.filter(name=object_class_name
                                                                 )[0]
  except IndexError:
    object_class = models.Repository_object_class()
    object_class.name = object_class_name

  # Build object for this file and store it.
  o = models.Repository_object()
  o.path = path
  o.guid = guid
  o.repository_object_class = c
  o.hash = hash.hexdigest()
  o.object_mtime = mtime
  o.size = size
  o.save()


def add_range_operator_filter(query, request, col_name, name):
  filter_kwargs = {}

  operator_translation = {
    '': 'exact',
    'eq': 'exact',
    'lt': 'lt',
    'le': 'lte',
    'gt': 'gt',
    'ge': 'gte',
  }

  # Keep track of if if any filters were added.
  changed = False

  # Last modified date filter.
  for get in request.GET:
    m = re.match('%s(_(.+))?' % name, get)
    if not m:
      continue
    operator = m.group(2)
    if operator not in operator_translation:
      raise_sys_log_http_404('Invalid argument: %s' % get)
    try:
      date = iso8601.parse_date(request.GET[get])
    except TypeError, e:
      raise_sys_log_http_404('Invalid date format: %s' % request.GET[get])
    filter_kwargs['%s__%s' % (col_name, operator_translation[operator])] = date
    changed = True
    #res[get] = datetime.datetime.isoformat(date)

  return query.filter(**filter_kwargs), changed


def add_wildcard_filter(query, col_name, value):
  """Add wildcard filter to query. Support only a single * at start OR end"""

  # Make sure there are no wildcards except at beginning and/or end of value.
  if re.match(r'.+\*.+$', value):
    raise_sys_log_http_404(
      'Wildcard is only supported at start OR end of value: %s' % value
    )

  value_trimmed = re.match(r'\*?(.*?)\*?$', value).group(1)

  wild_beginning = False
  wild_end = False

  filter_kwargs = {}

  if re.match(r'\*(.*)$', value):
    filter_kwargs['%s__endswith' % col_name] = value_trimmed
    wild_beginning = True

  if re.match(r'(.*)\*$', value):
    filter_kwargs['%s__startswith' % col_name] = value_trimmed
    wild_end = True

  if wild_beginning == True and wild_end == True:
    raise_sys_log_http_404(
      'Wildcard is only supported at start OR end of value: %s' % value
    )
  # If no wildcards are used, we add a regular "equals" filter.
  elif wild_beginning == False and wild_end == False:
    filter_kwargs[col_name] = value

  return query.filter(**filter_kwargs)

## Django doesn't support "complex" LIKE queries, so we have to inject it.
## THIS CODE MAY BREAK SINCE IT USES FIXED TABLE NAMES
#where_str = 'mn_service_access_requestor_identity.id = mn_service_access_log.requestor_identity_id and requestor_identity like %s'
#query = query.extra(where=[where_str], params=[requestor], tables=['mn_service_access_requestor_identity'])
## Filter by operation type.
##  query = query.filter(repository_object_class__name = oclass)
#if 'operation_type' in request.GET:
#  requestor = request.GET['operation_type']
#  # Translate from DOS to SQL style wildcards.
#  requestor = re.sub(r'\?', '_', requestor)
#  requestor = re.sub(r'\*', '%', requestor)


def add_slice_filter(query, request):
  """Create a slice of a query based on request start and count parameters."""

  # Skip top 'start' objects.
  try:
    start = int(request.GET['start'])
    if start < 0:
      raise ValueError
  except KeyError:
    start = 0
  except ValueError:
    raise_sys_log_http_404('Invalid start value: %s' % request.GET['start'])

  # Limit the number objects returned to 'count'.
  # None = All remaining objects.
  # 0 = No objects
  try:
    count = int(request.GET['count'])
    # Enforce max count of 1000.
    if count > 1000:
      raise ValueError
  except KeyError:
    count = None
  except ValueError:
    raise_sys_log_http_404(
      'Invalid count value: %s (count must be 0 <= count >= 1000' % request.GET['count']
    )

  # If both start and count are present but set to 0, we just tweak the query
  # so that it won't return any results.
  if start == 0 and count == 0:
    query = query.none()
  # Handle variations of start and count. We need these because Python does not
  # support three valued logic in expressions(which would cause an expression
  # that includes None to be valid and evaluate to None). Note that a slice such
  # as [value : None] is valid and equivalent to [value:]
  elif start and count:
    query = query[start:start + count]
  elif start:
    query = query[start:]
  elif count:
    query = query[:count]

  return query, start, count
