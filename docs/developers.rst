.. highlight:: shell

==========
Developers
==========

Overview
--------

Datakit is a light-weight framework for creating custom data science workflows.

It relies on the cliff_ command-line toolkit to provide an extensible system for customized plugins
tailored to a given person or organization's workflow.

Get Started!
------------

Here's how to set up `datakit` for local development.

1. Install Python 3.5 using pyenv_ and pyenv-virtualenv_::

    $ pyenv install 3.5.1

2. Clone `datakit`::

   $ git clone git@ctcinteract-svn01.ap.org:datakit-core.git

3. Create and activiate a virtual environment `datakit`::

    $ pyenv virtualenv datakit
    $ pyenv activate datakit
    $ cd datakit/

4. Install dependencies::

   $ pip install -r requirements.txt
   $ pip install -r requirements-dev.txt

5. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox_::

    $ flake8 datakit tests
    $ python setup.py test
    $ tox

Creating plugins
~~~~~~~~~~~~~~~~

A typical plugin should implement cliff_'s *entry points* strategy by defining command classes that are exposed under a sensible,
unique namespace. For example, a plugin to push and pull data between a local dev machine and an S3 bucket might 
be invoked as below::

    $ datakit data:push data/

Correctly configred plugins are installed using standard Python package installation techniques. For example,
to install a plugin called *datakit-data*::

    $ pip install datakit-data

The cliff documentation details how to use the entry points strategy in a plugin,
and contains a `demo app <http://docs.openstack.org/developer/cliff/demoapp.html>`_ for a simple plugin.

Datait plugins should have the following structure::

    plugin-name # root of git repo
    ├── setup.py
    ├── tox.ini
    ├── LICENSE.txt
    ├── plugin_name
    │   ├── __init__.py
    │   ├── command1.py
    │   ├── command2.py
    │   ├── library_module.py
    ├── tests
    │   ├── test_command1.py
    │   ├── test_command2.py
    │   └── test_library_module.py
    ├── requirements.txt
    ├── test-requirements.txt
    └── tox.ini

* *setup.py* should use *entry points* strategy
* *plugin_name/\_\_init_\_\.py* imports all command classes to simplify namespace


.. _cliff: http://docs.openstack.org/developer/cliff/
.. _pyenv: https://github.com/yyuu/pyenv#installation
.. _pyenv-virtualenv: https://github.com/yyuu/pyenv-virtualenv
.. _tox: http://codespeak.net/tox
