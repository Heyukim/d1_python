#!/usr/bin/env python
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
"""Test MNCore.getCapabilities()
"""

from __future__ import absolute_import

import responses

import gmn.tests.gmn_mock
import gmn.tests.gmn_test_case


class TestGetCapabilities(gmn.tests.gmn_test_case.GMNTestCase):
  @responses.activate
  def test_1850_v1(self):
    """MNCore.getCapabilities(): Returns a valid Node Registry document"""

    def test(client):
      node = client.getCapabilities()
      assert isinstance(node, client.bindings.Node)

    with gmn.tests.gmn_mock.disable_auth():
      test(self.client_v1)
      test(self.client_v2)