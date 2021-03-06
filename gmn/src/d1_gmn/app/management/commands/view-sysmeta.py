# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2019 DataONE
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

"""View the System Metadata for a local Science Object"""
import d1_common.xml

import d1_gmn.app.did
import d1_gmn.app.mgmt_base
import d1_gmn.app.sysmeta
import d1_gmn.app.views.decorators


class Command(d1_gmn.app.mgmt_base.GMNCommandBase):
    def __init__(self, *args, **kwargs):
        super().__init__(__doc__, __name__, *args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("did", help="PID or SID of a Science Object on this GMN")

    def handle_serial(self):
        did = self.opt_dict["did"]
        sysmeta_pyxb = d1_gmn.app.sysmeta.model_to_pyxb(
            d1_gmn.app.did.resolve_sid_v2(did)
        )
        self.log.info(d1_common.xml.serialize_to_xml_str(sysmeta_pyxb))
