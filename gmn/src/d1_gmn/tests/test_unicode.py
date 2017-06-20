# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2016 DataONE
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
"""Test handling of Unicode in D1 REST URLs and type elements
"""

from __future__ import absolute_import

import logging

import responses

import d1_gmn.tests.gmn_test_case

import d1_common
import d1_common.system_metadata


class TestUnicode(d1_gmn.tests.gmn_test_case.GMNTestCase):
  @responses.activate
  def test_1000(self, mn_client_v1_v2):
    """Unicode: GMN and libraries handle Unicode correctly"""
    with d1_gmn.tests.gmn_mock.disable_auth():
      tricky_unicode_str = self.load_sample_utf8_to_unicode(
        'tricky_identifiers_unicode.utf8.txt'
      )
      for line in tricky_unicode_str.splitlines():
        pid_unescaped, pid_escaped = line.split('\t')
        logging.debug(u'Testing PID: {}'.format(pid_unescaped))
        pid, sid, send_sciobj_str, send_sysmeta_pyxb = self.create_obj(
          mn_client_v1_v2, pid=pid_unescaped, sid=True
        )
        recv_sciobj_str, recv_sysmeta_pyxb = self.get_obj(mn_client_v1_v2, pid)
        assert d1_common.system_metadata.is_equivalent_pyxb(
          send_sysmeta_pyxb, recv_sysmeta_pyxb, ignore_timestamps=True
        )
        assert pid == pid_unescaped
        assert recv_sysmeta_pyxb.identifier.value() == pid_unescaped
        mn_client_v1_v2.delete(pid)
