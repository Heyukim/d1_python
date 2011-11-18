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
'''Module d1_client_cli.tests.test_access_control
=================================================

Unit tests for access_control.

:Created: 2011-11-10
:Author: DataONE (Dahl)
:Dependencies:
  - python 2.6
'''

# Stdlib.
import unittest
import logging
import sys

# D1.
import d1_common.const
import d1_common.testcasewithurlcompare
import d1_common.types.exceptions
import d1_common.xmlrunner

# App.
sys.path.append('../d1_client_cli/')
import access_control
import cli_exceptions

#===============================================================================


class TESTCLIAccessControl(d1_common.testcasewithurlcompare.TestCaseWithURLCompare):
  def setUp(self):
    pass

  def test_010(self):
    '''The access_control object can be instantiated'''
    a = access_control.access_control()
    self.assertEqual(len(a.allow), 0)

  def test_015(self):
    '''clear() removes all allowed subjects'''
    a = access_control.access_control()
    a.add_allowed_subject('subject_1', None)
    a.add_allowed_subject('subject_2', None)
    a.add_allowed_subject('subject_3', None)
    a.clear()
    self.assertEqual(len(a.allow), 0)

  def test_020(self):
    '''Single subject added without specified permission is retained and defaults to read'''
    a = access_control.access_control()
    a.add_allowed_subject('subject_1', None)
    self.assertEqual(len(a.allow), 1)
    self.assertTrue('subject_1' in a.allow)
    self.assertEqual(a.allow['subject_1'], 'read')

  def test_030(self):
    '''Adding subject that already exists updates its permission'''
    a = access_control.access_control()
    a.add_allowed_subject('subject_1', None)
    self.assertEqual(len(a.allow), 1)
    self.assertTrue('subject_1' in a.allow)
    self.assertEqual(a.allow['subject_1'], 'read')
    a.add_allowed_subject('subject_1', 'write')
    self.assertEqual(len(a.allow), 1)
    self.assertTrue('subject_1' in a.allow)
    self.assertEqual(a.allow['subject_1'], 'write')

  def test_040(self):
    '''Subject added with invalid permission raises exception InvalidArguments'''
    a = access_control.access_control()
    self.assertRaises(
      cli_exceptions.InvalidArguments, a.add_allowed_subject, 'subject_1',
      'invalid_permission'
    )
    self.assertEqual(len(a.allow), 0)

  def test_050(self):
    '''Multiple subjects with different permissions are correctly retained'''
    a = access_control.access_control()
    a.add_allowed_subject('subject_1', None)
    a.add_allowed_subject('subject_2', 'write')
    a.add_allowed_subject('subject_3', 'changePermission')
    self.assertEqual(len(a.allow), 3)
    self.assertTrue('subject_1' in a.allow)
    self.assertEqual(a.allow['subject_1'], 'read')
    self.assertTrue('subject_2' in a.allow)
    self.assertEqual(a.allow['subject_2'], 'write')
    self.assertTrue('subject_3' in a.allow)
    self.assertEqual(a.allow['subject_3'], 'changePermission')

  def test_150(self):
    '''repr() returns comma separated string representation'''
    a = access_control.access_control()
    a.add_allowed_subject('subject_1', None)
    a.add_allowed_subject('subject_2', 'write')
    a.add_allowed_subject('subject_3', 'changePermission')
    p = 'subject_1=read,subject_2=write,subject_3=changePermission'
    self.assertEquals(repr(a), p)

  def test_160(self):
    '''Populate object with comma separated string'''
    a = access_control.access_control()
    a.from_comma_string('subject_1=read,subject_2=write,subject_3=changePermission')
    self.assertEqual(len(a.allow), 3)
    self.assertTrue('subject_1' in a.allow)
    self.assertEqual(a.allow['subject_1'], 'read')
    self.assertTrue('subject_2' in a.allow)
    self.assertEqual(a.allow['subject_2'], 'write')
    self.assertTrue('subject_3' in a.allow)
    self.assertEqual(a.allow['subject_3'], 'changePermission')

  def test_200(self):
    '''str() returns formatted string representation'''
    a = access_control.access_control()
    a.add_allowed_subject('subject_1', None)
    a.add_allowed_subject('subject_2', 'write')
    a.add_allowed_subject('subject_3', 'changePermission')
    p = 'access:\n  submitter'
    self.assertEquals(str(a)[:19], p)

  def test_400(self):
    '''XML serialization / deserialization round trip'''
    a = access_control.access_control()
    a.add_allowed_subject('subject_1', None)
    a.add_allowed_subject('subject_2', 'write')
    a.add_allowed_subject('subject_3', 'changePermission')
    xml = a.to_xml()
    b = access_control.access_control()
    b.from_xml(xml)
    self.assertEqual(len(b.allow), 3)
    self.assertTrue('subject_1' in b.allow)
    self.assertEqual(b.allow['subject_1'], 'read')
    self.assertTrue('subject_2' in b.allow)
    self.assertEqual(b.allow['subject_2'], 'write')
    self.assertTrue('subject_3' in b.allow)
    self.assertEqual(b.allow['subject_3'], 'changePermission')


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  unittest.main()
