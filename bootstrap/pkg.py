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

"""d1_python package paths and related information.
"""
import importlib
import importlib.util
import logging
import os

# Absolute path to root of d1_python.
D1_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

_abs = lambda *p: os.path.join(D1_ROOT, *p)

# List of relative package paths.
# This should be the only such list in d1_python and the only place to edit when adding,
# removing or renaming packages.
_rel_pkg_path_list = [
    "client_cli/src/d1_cli",
    "client_onedrive/src/d1_onedrive",
    "lib_csw/src/d1_csw",
    "dev_tools/src/d1_dev",
    "gmn/src/d1_gmn",
    "lib_client/src/d1_client",
    "lib_common/src/d1_common",
    "lib_scimeta/src/d1_scimeta",
    "test_utilities/src/d1_test",
    "utilities/src/d1_util",
]

# List of paths to the root directory of each package.
# E.g. /dev/d1_python/lib_client
ROOT_PATH_LIST = [_abs(p.split(os.path.sep)[0]) for p in _rel_pkg_path_list]

# List of paths to the d1_* package directory of each package.
# E.g. /dev/d1_python/lib_client/src/d1_client
PKG_PATH_LIST = [_abs(p) for p in _rel_pkg_path_list]

# List of package name of each package.
# E.g.: d1_client
PKG_NAME_LIST = [p.split(os.path.sep)[-1] for p in _rel_pkg_path_list]

# List of paths to setup.py files for all packages in d1_python.
SETUP_PATH_LIST = [_abs(p, 'src/setup.py') for p in ROOT_PATH_LIST]

def get_setup_py_arg_dict(setup_py_path):
    try:
        spec = importlib.util.spec_from_file_location(".", setup_py_path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m.setup_dict
    except (ImportError, AttributeError, EnvironmentError):
        logging.debug(
            'Unable to get setup arg dict. cwd="{}" path="{}"'.format(
                os.getcwd(), setup_py_path
            )
        )
        return {}

# If importable, dict of root name to setup.py arguments for all packages in d1_python.
# setup.py files should all import only setuptools and built-in libraries, so should
# always be importable.
SETUP_ARG_DICT = {_abs(p.split(os.path.sep)[-3]): get_setup_py_arg_dict(p) for p in SETUP_PATH_LIST}
