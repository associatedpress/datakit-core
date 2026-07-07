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

Datakit uses uv_ to manage its virtual environment and dependencies. Install
uv first if you don't have it (see its `installation docs
<https://docs.astral.sh/uv/getting-started/installation/>`_).

Here's how to set up Datakit for local development.

1. Clone `datakit-core`::

    $ git clone git@github.com:associatedpress/datakit-core.git
    $ cd datakit-core/

2. Create the virtual environment and install all dependencies (including the
   dev tools) from ``uv.lock``::

    $ uv sync

   uv will pick a supported interpreter automatically; Datakit supports Python
   3.10 through 3.13.

3. Run any command inside the managed environment with ``uv run``, for example::

    $ uv run datakit --help

4. When you're done making changes, check that your changes pass the linter and
   the tests. The Makefile wraps the common tasks::

    $ make lint       # uv run ruff check datakit tests
    $ make test       # uv run pytest
    $ make test-all   # uv run tox across Python 3.10-3.13



.. _creating-plugins:

Creating plugins
----------------

Quickstart
~~~~~~~~~~

To jump-start your next plugin, check out Cookiecutter_ and cookiecutter-datakit-plugin_.

Overview
~~~~~~~~

A typical plugin should apply the `entry points`_ strategy by defining `Cliff command classes`_ that are
linked to a unique plugin name and action in the plugin's *pyproject.toml*. [1]_

This allows Datakit plugins to be easily installed using standard Python package
installation techniques.

For example, to install a plugin called *datakit-data* alongside core::

    $ uv tool install datakit-core --with datakit-data

The `entry points`_ strategy lets Datakit easily discover and invoke plugin commands::

    $ datakit data push
    $ datakit data pull

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
    └── pyproject.toml

To make a custom command discoverable by the *datakit* command-line tool,
you must expose it in the plugin's *pyproject.toml*. See :ref:`example-plugin` for details.

Plugin configurations
~~~~~~~~~~~~~~~~~~~~~

Datakit uses a home directory to stash plugin configuration.

By default, this directory is set to :code:`~/.datakit`. It can be customized
by setting the :code:`DATAKIT_HOME` environment variable.

Plugins should store configuration files under a directory
that matches the name of the plugin's repo or package.

For example, the *datakit-data* plugin would store configs in::

  ~/.datakit/plugins/datakit-data/config.json

Declaring a config spec
~~~~~~~~~~~~~~~~~~~~~~~~~

Plugins can opt in to the generic ``datakit config`` command family (``list``,
``status``, ``set``, ``init`` and ``verify``) by declaring *what* configuration
they need, rather than writing their own config commands. Core discovers this
declaration across every installed plugin, so users configure any plugin the
same way.

To opt in, set two class attributes on your command class(es):

* ``plugin_slug`` — the plugin's slug (also used for the on-disk config path).
* ``config_spec`` — a list of :py:class:`datakit.config.ConfigField` describing
  each configurable value.

Each :py:class:`~datakit.config.ConfigField` names a key and can mark it as
``required`` or ``secret`` (secrets are masked in listings and entered hidden),
carry ``help`` text and a ``default``, and attach a ``validator`` callable that
``datakit config verify`` runs to confirm the value actually works (e.g. that a
token authenticates or a bucket is reachable). For example:

  .. code:: python

      from cliff.command import Command

      from datakit import CommandHelpers
      from datakit.config import ConfigField

      class Push(CommandHelpers, Command):
          plugin_slug = "datakit-data"
          config_spec = [
              ConfigField("bucket", required=True, help="S3 bucket name"),
              ConfigField(
                  "aws_secret_access_key",
                  required=True,
                  secret=True,
                  help="AWS secret access key",
              ),
          ]

If several commands in a plugin each carry the (same) ``config_spec``, core
merges them into a single deduplicated view per plugin, so it's fine to declare
the spec on whichever command(s) is convenient.


.. _example-plugin:

Example Plugin
~~~~~~~~~~~~~~

Let's say we have a *datakit-data* plugin with the below file structure::

    datakit-data
    ├── pyproject.toml
    ├── datakit_data
    │   ├── __init__.py
    │   ├── push.py # Contains a Push class to push data to S3
    │   ├── pull.py # contains a Pull class to pull down data from S3

To expose the *push* and *pull* commands to *datakit*, you would declare them
under the ``datakit.plugins`` `entry points`_ group in *pyproject.toml* as below:

  .. code:: toml

      [project.entry-points."datakit.plugins"]
      "data push" = "datakit_data.push:Push"
      "data pull" = "datakit_data.pull:Pull"

After installing the plugin, Datakit can discover and invoke these new commands::

  $ datakit data push
  $ datakit data pull


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
.. _uv: https://docs.astral.sh/uv/
.. _pytest: http://doc.pytest.org/en/latest/
.. _tox: https://tox.wiki/
