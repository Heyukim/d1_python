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

import psycopg2.extensions
import pyxb.binding.datatypes
import d1_common.types.generated.dataoneTypes as dataoneTypes

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)


def adapt_pyxb_binding(binding):
  return psycopg2.extensions.AsIs(u"'{0}'"\
    .format(unicode(binding).replace('\'', '\'\'')))
  # An example uses adapt() here, but I could not get that to work with
  # casting to unicode. It works with casting to str.
  #.format(psycopg2.extensions.adapt(str(binding))))


psycopg2.extensions.register_adapter(
  dataoneTypes.NonEmptyNoWhitespaceString800, adapt_pyxb_binding
)

psycopg2.extensions.register_adapter(dataoneTypes.NonEmptyString800, adapt_pyxb_binding)

psycopg2.extensions.register_adapter(dataoneTypes.ChecksumAlgorithm, adapt_pyxb_binding)

psycopg2.extensions.register_adapter(
  dataoneTypes.ObjectFormatIdentifier, adapt_pyxb_binding
)

psycopg2.extensions.register_adapter(dataoneTypes.NonEmptyString, adapt_pyxb_binding)

psycopg2.extensions.register_adapter(pyxb.binding.datatypes.string, adapt_pyxb_binding)

psycopg2.extensions.register_adapter(pyxb.binding.datatypes.boolean, adapt_pyxb_binding)