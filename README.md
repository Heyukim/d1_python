## d1_python

Python components for DataONE clients and servers.

See the [documentation on ReadTheDocs](http://dataone-python.readthedocs.io/en/latest/).

[![Build Status](https://travis-ci.org/DataONEorg/d1_python.svg?branch=master)](https://travis-ci.org/DataONEorg/d1_python)
[![Coverage Status](https://coveralls.io/repos/github/DataONEorg/d1_python/badge.svg?branch=master)](https://coveralls.io/github/DataONEorg/d1_python?branch=master)
[![Documentation Status](https://readthedocs.org/projects/dataone-python/badge/?version=latest)](http://dataone-python.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/dataone.common.svg)](https://badge.fury.io/py/dataone.common)

### v2 and v1 API

* DataONE Generic Member Node:
[PyPI](https://pypi.python.org/pypi/dataone.gmn) &ndash;
[Docs](http://dataone-python.readthedocs.io/en/latest/gmn/index.html)
* DataONE Client Library for Python:
[PyPI](https://pypi.python.org/pypi/dataone.libclient) &ndash;
[Docs](http://dataone-python.readthedocs.io/en/latest/client/index.html)
* DataONE Common Library for Python: &ndash;
[PyPI](https://pypi.python.org/pypi/dataone.common) &ndash;
[Docs](http://dataone-python.readthedocs.io/en/latest/common/index.html)
* DataONE Test Utilities:
[PyPI](https://pypi.python.org/pypi/dataone.test_utilities) &ndash;
[Docs](http://dataone-python.readthedocs.io/en/latest/test/index.html)

### v1 API

* DataONE Command Line Client (CLI):
[PyPI](https://pypi.python.org/pypi/dataone.cli) &ndash;
[Docs](http://dataone-python.readthedocs.io/en/latest/cli/index.html)
* DataONE ONEDrive:
[PyPI](https://pypi.python.org/pypi/dataone.onedrive) &ndash;
[Docs](http://dataone-python.readthedocs.io/en/latest/onedrive/index.html)
* DataONE Certificate Extensions:
[PyPI](https://pypi.python.org/pypi/dataone.certificate_extensions)
* DataONE Gazetteer:
[PyPI](https://pypi.python.org/pypi/dataone.gazetteer)
* DataONE Ticket Generator:
[PyPI](https://pypi.python.org/pypi/dataone.ticket_generator)
* Google Foresite Toolkit:
[PyPI](https://pypi.python.org/pypi/google.foresite-toolkit)

### Contributing

Pull Requests (PRs) are welcome! Before you start coding, feel free to reach out to us and let us know what you plan to implement. We might be able to point you in the right direction.

We try to follow [PEP8](https://www.python.org/dev/peps/pep-0008/).

To help keep the style consistent and commit logs, blame/praise and other code annotations accurate, we autoformat all source with Black, isort and docformatter. A script that wraps up the formatting is available at `./dev_tools/src/d1_dev/src-format.py`. Simply call it before commit.

* [Black](https://black.readthedocs.io/en/stable/) - Standardized source formatting
* [isort](https://github.com/timothycrosley/isort) - Sort and group imports
* [docformatter](https://github.com/myint/docformatter) - PEP257 format docstrings 
* [Flake8](http://flake8.pycqa.org/en/latest/) - Lint, code and style validation

Configuration files for isort (`./.isort.cfg`) and Flake8 (`./.style.yapf`) are included, and show the formatting options we have selected.

### Unit tests

Testing is based on the [pytest](https://docs.pytest.org/en/latest/) unit test framework.

I have found the following aliases handy for running the tests. If using the `bash` shell, these can be added to `~/.bashrc`.

* Run tests serially. If the test uses one or more samples, and the result of the test has changed since the last time the sample was updated, open a diff between the current result and the sample in the PyCharm diff viewer and prompt the user for how to handle the mismatch. Options are to update the sample to match the current result and continue, ignore the mismatch for now and continue, or fail the test. When a test fails, stop the test run and open the location of the test failure in PyCharm, with the cursor set to the last line that was executed before the error and is part of d1_python.

      alias p='pytest --exitfirst --random-order-bucket=none --sample-ask --pycharm'

* Same as `p`, but more verbose and disabled capturing of console output. Capturing causes output from tests that passed to be hidden, making it easier to find the output from tests that failed. However, it makes debugging harder, as no output is displayed while stepping through tests that have not yet failed.

      alias pc='pytest --exitfirst --random-order-bucket=none --sample-ask --pycharm -vv --capture=no'

* Run tests in parallel using all available CPU cores, and create a coverage report. This greatly speeds up test execution but cannot be used with the PyCharm integration and interactive sample updates. 

      alias pn='pytest -n auto --cov=. --cov-report=term --cov-report=xml'

pytest searches for and runs all tests below the current directory, so starting pytest directly or via one of the aliases from the d1_python directory will run all tests.

To run a specific test module, add a path to the test module. E.g.:

    $ p d1_python/lib_common/src/d1_common/tests/test_checksum.py
 
To run only a single test, add a filter on the test number. E.g.:

    $ p d1_python/lib_common/src/d1_common/tests/test_checksum.py -k 1050

 
#### Sample files

Most of our tests work by serializing objects generated by the code being tested and comparing them with reference samples stored in files. This allows us to check all properties of generated objects without having to write asserts that check individual properties, eliminating a time consuming and repetitive part of the test writing process.

When writing comparisons manually, one will often select a few properties to check, and when those are determined to be valid, the remaining values are assumed to be correct as well. By comparing complete serialized versions of the objects, we avoid such assumptions.

By storing the expected serialized objects in files instead of in the unit tests themselves, we avoid embedding hard coded documents inside the unit test modules and make it simple to automatically update the expected contents of objects as the code evolves.

When unit tests are being run as part of CI or as a normal guard against regressions in a local development environment, any mismatches between actual and expected serialized versions of objects simply trigger test failures. However, when a test is initially created or the serialized version of an object is expected to change, tests can automatically write or update the sample files they use. This function is enabled by starting `pytest` with the `--sample-ask` switch. When enabled, missing or mismatched sample files will not trigger test failures, instead starting an interactive process where differences are displayed together with yes/no prompts for writing or updating the samples. By default, differences are displayed in a GUI window using `kdiff3`, which provides a nice color coded view of the differences.

The normal procedure for writing a sample based unit test is to just write the test as if the sample already exists, then running the test with `--sample-ask` and viewing and approving the resulting sample, which is then automatically written to a file. The sample file name is displayed, making it easy to find the file in order to add it to tracking so that it can be committed along with the test module.

When working on large changes that cause many samples to become outdated, reviewing and approving samples can be deferred until the new code approaches stability. This is done by running the tests with `--sample-update`, which automatically writes or updates samples to match the current results. Then, view and approve the tests with `--sample-review` before committing.

Typically, it is not desirable to track generated files in Git. However, although the sample files are generated, they are an integral part of the units tests, and should be tracked just like the unit tests themselves.

Also implemented is a simple process for cleaning out unused sample files. Sample files are often orphaned when their corresponding tests are removed or refactored. The process is activated with the `--sample-tidy` switch. When active, the test session starts by moving all sample files from their default directory, `test_docs`, to `test_docs_tidy`. As the sample files are accessed by tests, they are automatically moved back to `test_docs`, and any files remaining in `test_docs_tidy` after a complete test run can be untracked and deleted.

When staging `test_docs`, stage the directory, so that new files are included, and deleted files get deleted on the server:

    $ git add test_utilities/src/d1_test/test_docs
    $ git commit -m 'Update samples'

#### DataONE Client to Django test adapter

GMN tests are based on an adapter that enables using d1_client with the Django test framework. The adapter mocks Requests to issue requests through the Django test client.

Django includes a test framework with a test client that provides an interface that's similar to that of an HTTP client, but calls Django internals directly. The client enables testing of most functionality of a Django app without actually starting the app as a network service.

For testing GMN's D1 REST interfaces, we want to issue the test requests via the D1 MN client. Without going through the D1 MN client, we would have to reimplement much of what the client does, related to formatting and parsing D1 REST requests and responses.

This module is typically used in tests running under django.test.TestCase and requires an active Django context, such as the one provided by `./manage.py test`.

#### Command line switches

We have added some custom functionality to pytest which can be enabled by launching pytest with the following switches:

  * `--sample-ask`: Enable a mode that display diffs and, after user confirmation, can automatically update or write new test sample documents on mismatches.

  * `--pycharm`:
   
    * Automatically open files where errors occur and move the cursor to the line of the error
    
    * Show syntax highlighted diffs for scripts and data files using PyCharm's powerful diff viewer
    
    * Also requires the path to the PyCharm binary to be configured in `DEBUG_PYCHARM_BIN_PATH` in `./conftest.py`. 

  * See `./conftest.py` for implementation and notes.

  * `parameterize_dict`: Support for parameterizing test functions by adding a dict class member containing parameter sets.

Note: None of these switches can be used when running tests in parallel with xdist (`-n`, `--dist`, `--tx`).

#### Debugging tests with PyCharm

* By default, the PyCharm `Run context configuration (Ctrl+Shift+F10)` will generate test configurations and run the tests under the native unittest framework in Python's standard library. This will cause the tests to fail, as they require pytest. To generate pytest configurations by default, set `Settings > Tools > Python Integrated Tools > Default test runner` to pytest. See the [documentation](https://www.jetbrains.com/help/pycharm/2017.1/testing-frameworks.html) for details.

* Generate and run a configuration for a specific test by placing the cursor on a test function name and running `Run context configuration (Ctrl+Shift+F10)`.

* After generating the configuration, debug with `Debug (Shift-F9)`.

* If running the tests outside of PyCharm, launching `pytest` with the `--pycharm` switch will cause `pytest` to attempt to move the cursor in PyCharm to the location of any tests failures as they occur. This should be used with the `--exitfirst` (`-x`) switch.

* Stopping a test that has hit a breakpoint in PyCharm can cause the test database to be left around. On the next run, Django will then prompt the user to type "yes" to remove the database. The prompt appears in the PyCharm debug console output. To disable the prompt, go to `Run / Debug Configurations > Edit Configurations > Defaults > Django tests > Options` and add `--noinput`. See the [question on SO](https://stackoverflow.com/questions/34244171) for details.

* `pytest` by default captures `stdout` and `stderr` output for the tests and only shows the output for the tests that failed after all tests have been completed. Since a test that hits a breakpoint has not yet failed, this hides any output from tests being debugged and also hides output from the debug console prompt (where Python script can be evaluated in the current context). To see the output while debugging, go to `Run / Debug Configurations > Edit Configurations > Defaults > pytest > Additional Arguments` and add `--capture=no`. Also add an environment variable `JB_DISABLE_BUFFERING` and set it to `--capture=no --exitfirst --verbose`. Verbosity can also be increased by adding one or more `-v`.

* Each unit test is implicitly wrapped in a database transaction and I have not found a way around this. The effect is that it's cumbersome to check the current state of the database while at a breakpoint or stepping through tests. PyCharm's database tools will only see the database as it was before the test was started. The only workaround I've found is to manually issue queries from within the current context, using the PyCharm console. While stepping through the test, bring up the console,`View > Tool Windows > Python Console`, and click `Show Python Prompt`. Then submit queries with, e.g., `> self.run_django_sql('select count(*) from app_scienceobject')`. Write them in the database console to get the code completion and other features, then copy it into a call in the Python console. If an invalid query is submitted, the current database transaction will be lost. If there is no output when running commands in the console, it's due to the output being captured by pytest. See above.

* The settings in `settings_test.py` are optimized for testing and debugging, while the settings in `settings_template.py` are optimized for production. To use `settings_test.py` when debugging tests in PyCharm, go to `Run / Debug Configurations > Edit Configurations > Defaults > pytest > Environment variables`, add `DJANGO_SETTINGS_MODULE` and set it to `d1_gmn.settings_test`.

* If the `requirements.txt` file is out of date, the `Package requirements` inspection in PyCharm will display a list of missing packages at the top of the screen. Do not follow PyCharm's suggestion to install the missing packages as it's probably the `requirements.txt` file that should be updated instead.  See the section describing how to update dependencies for more information.
 

### Django

* Testing of the GMN Django web app is based on pytest and [pytest-django](https://pytest-django.readthedocs.io/en/latest/).

* The tests use `settings_test.py` for GMN and Django configuration.

* pytest-django forces `settings.DEBUG` to `False` in `pytest_django/plugin.py`. To set `settings.DEBUG`, override it close to where it will be read, e.g., wit `@django.test.override_settings(DEBUG=True)`.


#### Django database test fixture

The GMN tests run in the context of a database that has been prepopulated with randomized data. The fixture file for the database is a JSON file stored in

    ./test_utilities/src/d1_test/test_docs/json/db_fixture.json.bz2

After changing any of the ORM classes in models.py, the database test fixture must be regenerated. This will often cause sample files to have to be updated as well, by running the tests with `--sample-update`.

Generate the fixture file with:

    $ ./dev/d1_python/gmn/src/d1_gmn/tests/mk_db_fixture.py

Fixtures can be loaded directly into the test database from the JSON files but it's much faster to keep an extra copy of the db as a template and create the test db as needed with Postgres' "create database from template" function. So we only load the fixtures into a template database and reuse the template. This is implemented in `./conftest.py`.

Science object bytes are stored on disk, so they are not captured in the db fixture. If a test needs get(), getChecksum() and replica() to work, it must first create the correct file in GMN's object store or mock object store reads. The bytes are predetermined for a given test PID. See `d1_test.d1_test_case.generate_reproducible_sciobj_str()` and `d1_gmn.app.util.sciobj_file_path()`.


### Setting up the development environment

These instructions are tested on Linux Mint 18 and should also work on close derivatives.

#### Install packaged dependencies

  $ sudo apt update
  $ sudo apt -fy dist-upgrade
  $ sudo apt install -y python-setuptools libssl-dev postgresql postgresql-server-dev-all git

##### Python 3

  $ sudo apt install -y python3-dev python3-venv
  $ python3 -m venv venv

##### Python 2

  $ sudo apt install -y python-dev python-virtualenv

##### Python 3 and Python 2

  $ . ./venv/bin/activate

Download the source from GitHub:

    $ git clone https://github.com/DataONEorg/d1_python.git

Add the DataONE packages to the Python path, and install their dependencies:

    cd ~/d1_python
    sudo ./dev_tools/src/d1_dev/setup-all.py --root . develop

#### Postgres

:

    $ sudo apt install --yes postgresql

Set the password of the postgres superuser account:

    $ sudo passwd -d postgres
    $ sudo su postgres -c passwd

When prompted for the password, enter a new superuser password (and remember it :-).

:

    $ sudo -u postgres createdb -E UTF8 gmn2
    $ sudo -u postgres createuser --superuser `whoami`

PyCharm (and other IntelliJ based platforms), are not able to connect to database with local (UNIX) sockets. Postgres' convenient "peer" authentication type only works over local sockets. A convenient workaround for this is to set Postgres up to trust local connections made over TCP/IP.

:

    $ sudo editor /etc/postgresql/10/main/pg_hba.conf

Add line:

:

    host all all 127.0.0.1/32 trust

A similar line for MD5 may already be present and, if so, must be commented out.


#### Certificates

Run the following commands (all sections), except, change the location for openssl.cnf, so the line that copies it becomes:

    $ sudo cp <your_d1_python_path>/d1_mn_generic/src/deployment/openssl.cnf .

#### Tests

Run the tests and verify that they all pass:

    $ pytest

#### PyPI

Set up credentials for working with the DataONE account on PyPI:

Edit `~/.pypirc`:

    [server-login]
    username: dataone
    password: <secret>

### Creating a new release

#### Updating dependencies

Update all packages managed by pip:

    $ ./dev_tools/src/d1_dev/pip-update-all.py

The DataONE Python stack specifies the versions that were tested in CI builds before release as the lowest required versions, and allows any later versions to be installed as part of regular maintenance.

Check that there are no package version conflicts:

    $ pip check 

As updating the versions in the `setup.py` files manually is time consuming and error prone, a script is included that automates the task. The script updates the version information for the dependencies in the `setup.py` files to match the versions of the currently installed dependencies. Update the `setup.py` files with:

    $ ./dev_tools/src/d1_dev/src-sync-dependencies.py . <version>

The `<version>` argument specifies what the version will be for the release. E.g., `"2.3.1"`. We keep the version numbers in sync between all of the packages in the d1_python git repository, so only one version string needs to be specified.

The current version can be found in any of the `setup.py` files and in the `VERSION` string in `./lib_common/src/d1_common/const/.py`

Run the tests, ensure that they pass and update sample files as necessary.

The `requirements.txt` file contains a list of packages and pinned versions that will be used in CI builds. It designates the exact Python environment in which the unit tests will run in CI builds.

Update the `requirements.txt` file:

    $ ./dev_tools/src/d1_dev/update-requirements-txt.py


Commit and push the changes, and check the build on Travis.

#### Building the release packages

After successful build, clone a fresh copy, which will be used for building the release packages:

Building the release packages from a fresh clone is a simple way of ensuring that only tracked files are released. It is a workaround for the way setuptools works, which is basically that it vacuums up everything that looks like a Python script in anything that looks like a package, which makes it easy to publish local files by accident.

Build and publish the packages:

    $ cd
    $ rm -rf ~/d1_python_build
    $ git clone git@github.com:DataONEorg/d1_python.git d1_python_build
    $ cd ~/d1_python_build
    
    $ pyenv versions
      * Pick a version that is close or the same as the version of Python used for testing on Travis
    
    $ pyenv virtualenv x.y.z venv_build
    $ pyenv activate venv_build
    $ pip install --upgrade pip
    $ pip install wheel    
    
    $ python ./dev_tools/src/d1_dev/setup-all.py --root . bdist_wheel upload

### Building the documentation

When `d1_python` is pushed to GitHub, a signal is sent by GitHub to [ReadTheDocs.org](https://readthedocs.org/), which automatically retrieves the new version of the project from GitHub, builds the documentation and makes it available at

http://dataone-python.readthedocs.io/en/latest/

So it is not absolutely necessary to have a local build environment set up for the documentation, but building locally provides faster feedback when making changes that need to be checked before publishing.

### Troubleshooting

Clear out the installed libraries and reinstall:

    $ sudo rm -rf /usr/local/lib/python2.7/dist-packages/d1_*
    $ sudo nano /usr/local/lib/python2.7/dist-packages/easy-install.pth
    Remove all lines that are: dataone.*.egg and that are paths to your d1_python.

