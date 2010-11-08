# Stdlib.
import csv
import datetime
import glob
import hashlib
import os
import re
import stat
import sys
import time
import uuid
import urllib
import urlparse
import httplib

import pickle

# Django.
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.http import Http404
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.utils.html import escape
from django.db.models import Avg, Max, Min, Count
from django.core.urlresolvers import *

from django.db import models
from django.http import HttpResponse
from django.db.models import Avg, Max, Min, Count

# 3rd party.
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
import d1common.exceptions
import d1pythonitk.systemmetadata
import d1pythonitk.client
import d1common.types.objectlocationlist_serialization

# App.
import mn_service.models
import settings


class ObjectLocationList(
  d1common.types.objectlocationlist_serialization.ObjectLocationList
):
  def deserialize_db(self, obj):
    cfg = lambda key: mn_service.models.Node.objects.get(key=key).val

    objectLocation = d1common.types.generated.objectlocationlist.ObjectLocation()

    objectLocation.nodeIdentifier = cfg('identifier')
    objectLocation.baseURL = cfg('base_url')
    objectLocation.url = '{0}/object/{1}'.format(cfg('base_url'), obj.guid)

    self.object_location_list.objectLocation.append(objectLocation)

    self.object_location_list.identifier = obj.guid


class NodeList(d1common.types.nodelist_serialization.NodeList):
  def deserialize_db(self):
    '''
    :param:
    :return:
    '''
    cfg = lambda key: mn_service.models.Node.objects.get(key=key).val

    # Node

    # El.
    node = d1common.types.generated.nodelist.Node()
    node.identifier = cfg('identifier')
    node.name = cfg('version')
    node.description = cfg('description')
    node.baseURL = cfg('base_url')
    # Attr
    node.replicate = cfg('replicate')
    node.synchronize = cfg('synchronize')
    node.type = cfg('node_type')

    # Services

    services = d1common.types.generated.nodelist.Services()

    svc = d1common.types.generated.nodelist.Service()
    svc.name = cfg('service_name')
    svc.version = cfg('service_version')
    svc.available = cfg('service_available')

    # Methods

    methods = []

    method = d1common.types.generated.nodelist.ServiceMethod()
    method.name = 'session'
    method.rest = 'session/'
    method.implemented = 'true'
    methods.append(method)

    method = d1common.types.generated.nodelist.ServiceMethod()
    method.name = 'object_collection'
    method.rest = 'object'
    method.implemented = 'true'
    methods.append(method)

    method = d1common.types.generated.nodelist.ServiceMethod()
    method.name = 'get_object'
    method.rest = 'object/'
    method.implemented = 'true'
    methods.append(method)

    method = d1common.types.generated.nodelist.ServiceMethod()
    method.name = 'get_meta'
    method.rest = 'meta/'
    method.implemented = 'true'
    methods.append(method)

    # Log

    method = d1common.types.generated.nodelist.ServiceMethod()
    method.name = 'log_collection'
    method.rest = 'log'
    method.implemented = 'true'
    methods.append(method)

    # Health

    method = d1common.types.generated.nodelist.ServiceMethod()
    method.name = 'health_ping'
    method.rest = 'health/ping'
    method.implemented = 'true'
    methods.append(method)

    method = d1common.types.generated.nodelist.ServiceMethod()
    method.name = 'health_status'
    method.rest = 'health/status'
    method.implemented = 'true'
    methods.append(method)

    # Monitor

    method = d1common.types.generated.nodelist.ServiceMethod()
    method.name = 'monitor_object'
    method.rest = 'monitor/object'
    method.implemented = 'true'
    methods.append(method)

    method = d1common.types.generated.nodelist.ServiceMethod()
    method.name = 'monitor_event'
    method.rest = 'monitor/event'
    method.implemented = 'true'
    methods.append(method)

    # Node

    method = d1common.types.generated.nodelist.ServiceMethod()
    method.name = 'node'
    method.rest = 'node'
    method.implemented = 'true'
    methods.append(method)

    # Diagnostics, debugging and testing.
    # inject_log
    # get_ip

    # Admin.
    # admin/doc
    # admin

    svc.method = methods

    services.append(svc)

    node.services = services

    self.node_list.append(node)


def resolve(request, guid):
  if request.method == 'GET':
    return resolve_get(request, guid, head=False)

  if request.method == 'HEAD':
    return object_collection_get(request, guid, head=True)

  # Only GET and HEAD accepted.
  return HttpResponseNotAllowed(['GET', 'HEAD'])


def resolve_get(request, guid, head):
  try:
    obj = mn_service.models.Object.objects.get(guid=guid)
  except: # mn_service.models.DoesNotExist
    raise d1common.exceptions.NotFound(0, 'Non-existing object was requested', guid)

  object_location_list = ObjectLocationList()
  object_location_list.deserialize_db(obj)

  response = HttpResponse(object_location_list.serialize_xml(pretty=True))
  response['Content-Type'] = 'text/xml'

  return response


def node(request):
  '''
  '''
  if request.method == 'GET':
    return node_get(request)

  # Only GET accepted.
  return HttpResponseNotAllowed(['GET'])


def node_get(request):
  node = NodeList()
  node.deserialize_db()

  response = HttpResponse(node.serialize_xml(pretty=True))
  response['Content-Type'] = 'text/xml'

  return response
