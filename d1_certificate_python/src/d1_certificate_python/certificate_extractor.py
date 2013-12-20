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
:mod:`certificate_extractor`
============================

:Synopsis: Extract the subject and subject_info from a certificate.
:Created: 2012-05-01
:Author: DataONE (Dahl)
'''

import d1_x509v3_certificate_extractor


def extract_from_file(path):
  '''Returns the tuple: (subject, subject_info)'''
  with open(path, 'rb') as f:
    return extract_from_buffer(f.read())


def extract_from_buffer(certificate_buffer):
  '''Returns the tuple: (subject, subject_info)'''
  return d1_x509v3_certificate_extractor.extract(certificate_buffer)
