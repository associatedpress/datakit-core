.. highlight:: shell

==========
Developers
==========

Overview
--------

Datakit is a light-weight framework for creating custom data science workflows.

It relies on the Cliff_ command-line toolkit to provide an extensible system of plugins
to support custom workflows.

Core development
----------------

Here's how to set up Datakit for local development.

1. Install Python 3.5 using pyenv_ and pyenv-virtualenv_::

    $ pyenv install 3.5.1

2. Clone `datakit-core`::

   $ git clone git@github.com:associatedpress/datakit-core.git

3. Create and activate a virtual environment::

    $ pyenv virtualenv datakit-core
    $ pyenv activate datakit-core
    $ cd datakit-core/

4. Install dependencies::

   $ pip install -r requirements.txt
   $ pip install -r requirements-dev.txt

5. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox_::

    $ flake8 datakit tests
    $ python setup.py test
    $ tox



.. _creating-plugins:

Creating plugins
----------------

Quickstart
~~~~~~~~~~

To jump-start your next plugin, check out Cookiecutter_ and cookiecutter-datakit-plugin_.

Overview
~~~~~~~~

A typical plugin should apply the `entry points`_ strategy by defining `Cliff command classes`_ that are 
linked to a unique plugin name and action in the plugin's *setup.py*. [1]_

This allows Datakit plugins to be easily installed using standard Python package 
installation techniques.

For example, to install a plugin called *datakit-data*::

    $ pip install datakit-data

The `entry points`_ strategy lets Datakit easily discover and invoke plugin commands::

    $ datakit data:push
    $ datakit data:pull

The Cliff_ documentation details how to use `entry points`_ in a plugin,
and contains a `demo app <http://docs.openstack.org/developer/cliff/demoapp.html>`_ for a simple plugin.

You can also check out our :ref:`example-plugin` below for the basics of wiring up a plugin.

Plugin structure
~~~~~~~~~~~~~~~~

Datakit plugins should have the following structure::

    plugin-name # root of git repo
    ├── plugin_name
    │   ├── __init__.py
    │   └── some_command.py
    └── setup.py

To make a custom command discoverable by the *datakit* command-line tool,
you must expose it in the plugin's *setup.py*. See :ref:`example-plugin` for details.

Plugin configurations
~~~~~~~~~~~~~~~~~~~~~

Datakit uses a home directory to stash plugin configuration.

By default, this directory is set to :code:`~/.datakit`. It can be customized
by setting the :code:`DATAKIT_HOME` environment variable.

Plugins should store configuration files under a directory
that matches the name of the plugin's repo or package.

For example, the *datakit-data* plugin would store configs in::

  ~/.datakit/plugins/datakit-data/config.json


.. _example-plugin:

Example Plugin
~~~~~~~~~~~~~~

Let's say we have a *datakit-data* plugin with the below file structure::

    datakit-data
    ├── setup.py
    ├── datakit_data
    │   ├── __init__.py
    │   ├── push.py # Contains a Push class to push data to S3
    │   ├── pull.py # contains a Pull class to pull down data from S3

To expose the *push* and *pull* commands to *datakit*, you would
configure the `entry points`_ variable in *setup.py* as below:

  .. code:: python

      ....
       entry_points={
          'datakit.plugins': [
            'data:push= datakit_data.push:Push',
            'data:pull= datakit_data.pull:Pull',
          ]
      }
      ....

After installing the plugin, Datakit can discover and invoke these new commands::

  $ datakit data:push
  $ datakit data:pull


Plugin Mixins
~~~~~~~~~~~~~~

Datakit provides the :py:class:`datakit.command_helpers.CommandHelpers` mixin class
to help build plugin commands.

This mixin contains basic configuration methods and attributes such as
default locations for plugin-specific configuration files.


Testing
~~~~~~~

Datakit does not require you to use a particular testing framework. Because
each plugin is technically a stand-alone Python package, you're free to
use whatever testing framework you prefer.

Datakit itself uses the pytest_ framework. We highly recommend it!

.. [1] As a convention, Datakit entry points should follow
  the ``plugin:command`` format. For example ``data:push`` in the :ref:`example-plugin`.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _cookiecutter-datakit-plugin: https://github.com/associatedpress/cookiecutter-datakit-plugin
.. _Cliff: http://docs.openstack.org/developer/cliff/
.. _Cliff command classes: http://docs.openstack.org/developer/cliff/classes.html#cliff.command.Command
.. _entry points: https://setuptools.readthedocs.io/en/latest/pkg_resources.html#entry-points
.. _pyenv: https://github.com/yyuu/pyenv#installation
.. _pyenv-virtualenv: https://github.com/yyuu/pyenv-virtualenv
.. _pytest: http://doc.pytest.org/en/latest/
.. _tox: http://codespeak.net/tox
