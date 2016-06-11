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
''':mod:`workspace_solr_client`
===============================

:Synopsis:
 - Generate and run queries against Solr.
:Author:
  DataONE (Dahl)
'''

# Stdlib.
import HTMLParser
import httplib
import logging
import socket
import urllib
import urlparse

# 3rd party.
import requests

# D1.
import d1_common.const
import d1_common.date_time
import d1_common.url

# App.
import workspace_exception

# Replaced with the python.requests library.

## SolrConnection is a thin layer on top of HTTPSConnection that automatically
## retries queries and connection attempts.
#class SolrConnection(object):
#  def __init__(self, options,
#               solr_selector='/v1/query/solr/', n_tries=3):
#    self._options = options
#    self._base_url = options['base_url']
#    self._solr_host = self._get_hostname(options['base_url'])
#    self._solr_selector = self._get_solr_selector(options['base_url'], solr_selector)
#    self._connection = self._create_connection()
#    self._n_tries = n_tries
#
#
#  def get(self, query_url, headers=None):
#    if headers is None:
#      headers = {}
#    abs_query_url = self._solr_selector + '?' + query_url
#    for i in range(self._n_tries):
#      logging.debug(u'get({0}{1})'.format(self._solr_host, abs_query_url))
#      try:
#        self._connection.request('GET', abs_query_url, headers=headers)
#        response = self._connection.getresponse()
#      except (httplib.BadStatusLine,httplib.CannotSendRequest, socket.error,
#              httplib.HTTPException):
#        logging.exception(u'Solr query failed (attempt {0}: {1}: Exception:'.format(str(i), query_url))
#        self._connection.close()
#        self._connection = self._create_connection()
#      else:
#        self._assert_response_is_ok(response)
#        return eval(response.read())
#      logging.warn(u"Retrying get after connection failed (ntries = %s)" % str(i+1))
#
#    raise workspace_exception.WorkspaceException(u'Giving up Solr query after {0} tries: {1}'
#                                       .format(self._n_tries, query_url))
#
#
#  def _assert_response_is_ok(self, response):
#    if response.status not in (200, ):
#      try:
#        html_doc = response.read()
#      except:
#        html_doc = ''
#      #s = SimpleHTMLToText()
#      #txt_doc = s.get_text(html_doc)
#      logging.error(u'Error in Solr response: {0}\n{1}\n{2}'
#                .format(response.status, response.reason, html_doc))
#      raise workspace_exception.WorkspaceException(
#        u'Error in Solr response: {0}'.format(response.reason))
#      #raise Exception(msg)
#
#
#  def _create_connection(self):
#    #logging.debug('Creating new connection to Solr')
#    return httplib.HTTPSConnection(self._solr_host, timeout=self._options['solr_query_timeout'])
#
#
#  def _get_hostname(self, base_url):
#    return urlparse.urlsplit(base_url).netloc;
#
#
#  def _get_solr_selector(self, base_url, solr_selector):
#    base_selector = urlparse.urlsplit(base_url).path;
#    return d1_common.url.joinPathElementsNoStrip(base_selector, solr_selector)
#
##===============================================================================


class SolrClient(object):
  def __init__(
    self,
    base_url,
    solr_selector='/v1/query/solr/',
    max_retries=3,
    timeout=30,
    max_objects_for_query=50
  ):
    self._solr_endpoint = base_url + solr_selector
    self._session = requests.Session()
    self._session.mount('http://', requests.adapters.HTTPAdapter(max_retries=max_retries))
    self._session.mount(
      'https://', requests.adapters.HTTPAdapter(
        max_retries=max_retries
      )
    )
    self._timeout = timeout
    self._max_objects_for_query = max_objects_for_query

  def query(self, query, filter_queries=None, fields=None):
    if fields is None:
      fields = ['*']

    query_params = {
      'q': query,
      'fl': ','.join(fields),
      'rows': self._max_objects_for_query,
      'indent': 'on',
      'wt': 'json'
    }

    if filter_queries is not None:
      query_params.extend(self._make_query_param_tuples('fl', filter_queries))

    r = requests.get(
      self._solr_endpoint,
      timeout=self._timeout,
      params=query_params,
      verify=False
    )
    return r.json()

  def escape_query_term_string(self, term):
    '''Escape a query term string and wrap it in quotes.
    '''
    return u'"{0}"'.format(self._escape_query_term(term))

  # Private.

  def _make_query_param_tuples(self, query_type, terms):
    return [(query_type, t) for t in self.__escape_query_term_list(terms)]

  def __escape_query_term_list(self, terms):
    return [self._escape_query_term(term) for term in terms]

  def _escape_query_term(self, term):
    reserved = [
      '+',
      '-',
      '&',
      '|',
      '!',
      '(',
      ')',
      '{',
      '}',
      '[',
      ']',
      '^',
      '"',
      '~',
      '*',
      '?',
      ':',
    ]
    term = term.replace(u'\\', u'\\\\')
    for c in reserved:
      term = term.replace(c, u'\{0}'.format(c))
    return term

  #def prepare_query_term(self, field, term):
  #  '''
  #  Prepare a query term for inclusion in a query.  This escapes the term and
  #  if necessary, wraps the term in quotes.
  #  '''
  #  if term == "*":
  #    return term
  #  addstar = False
  #  if term[len(term)-1] == '*':
  #    addstar = True
  #    term = term[0:len(term)-1]
  #  term = self._escape_query_term(term)
  #  if addstar:
  #    term = '%s*' % term
  #  if self.getSolrType(field) in ['string', 'text', 'text_ws']:
  #    return '"%s"' % term
  #  return term

  #def escapeVal(self,val):
  #  val = val.replace(u"&", u"&amp;")
  #  val = val.replace(u"<", u"&lt;")
  #  val = val.replace(u"]]>", u"]]&gt;")
  #  return self.encoder(val)[0]  #to utf8

  #def escapeKey(self,key):
  #  key = key.replace(u"&", u"&amp;")
  #  key = key.replace(u'"', u"&quot;")
  #  return self.encoder(key)[0]  #to utf8

  #===============================================================================


class SimpleHTMLToText(HTMLParser.HTMLParser):
  def __init__(self):
    self.reset()
    self.fed = []
    super(SimpleHTMLToText, self).__init__()

  def get_text(self, html):
    self.feed(html)
    return self.get_data()

  def handle_data(self, d):
    self.fed.append(d)

  def get_data(self):
    return ''.join(self.fed)