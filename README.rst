.. image:: https://img.shields.io/pypi/v/datakit-core.svg
        :target: https://pypi.python.org/pypi/datakit-core

.. image:: https://github.com/associatedpress/datakit-core/actions/workflows/main.yml/badge.svg
    :target: https://github.com/associatedpress/datakit-core/actions/workflows/main.yml
    :alt: Build status on Github Actions

.. image:: https://readthedocs.org/projects/datakit-core/badge/?version=latest
    :target: https://datakit-core.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

=======
Datakit
=======

Datakit is a pluggable command-line tool for managing the life cycle
of data projects.

The Associated Press Data Team uses Datakit to auto-generate project skeletons,
archive and share data on Amazon S3, and other routine tasks.

Datakit is a thin wrapper around the Cliff_ command-line framework and
is intended for use with a growing ecosystem of plugins.

Feel free to use `our plugins on Github`_, or fork and modify them
to suit your needs.

If you're comfortable programming in Python, you can create your
own plugins (see :ref:`creating-plugins`).

Installation
============

Datakit is distributed as a command-line tool. The recommended way to install
it is with uv_, which installs the ``datakit`` command into its own isolated
environment::

    $ uv tool install datakit-core

Plugins must live in the same environment as ``datakit`` so it can discover
them. Install them alongside core with ``--with``::

    $ uv tool install datakit-core --with datakit-project

To add a plugin to an existing install, re-run the command with the plugins you
want (uv will update the tool in place)::

    $ uv tool install datakit-core --with datakit-project --with datakit-data

If you don't have uv, see its `installation docs <https://docs.astral.sh/uv/getting-started/installation/>`_.

Usage
=====

After installing one or more plugins, Datakit can be used to invoke the
commands provided by those plugins.

To see which commands plugins provide, try the ``--help`` flag::

    $ datakit --help

Example: datakit-project
~~~~~~~~~~~~~~~~~~~~~~~~

Install ``datakit-project`` alongside core::

    $ uv tool install datakit-core --with datakit-project

The plugin provides a ``project create`` command. You need to specify a Cookiecutter_ template to use this command, for example the AP's R template:

.. image:: http://data.ap.org/projects/2019/datakit-docs/img/2.gif

That's the basic recipe for working with plugins: install, explore, and invoke! [1]_

Configuration
=============

Many plugins need configuration to work — API tokens, bucket names, default
paths, and the like. Datakit ships a generic ``config`` command family that
reads each installed plugin's declared configuration schema, so you use the
same commands no matter which plugin you're setting up. Configuration is stored
per plugin under ``~/.datakit/plugins/<plugin>/config.json``.

List every plugin's configuration and whether each value is set::

    $ datakit config list

``datakit config status`` is an alias for ``list``.

Interactively fill in any unset values (secrets are entered hidden). Pass a
plugin slug to limit it to one plugin::

    $ datakit config init
    $ datakit config init datakit-github

Set a single value. Omit the value to be prompted for it (hidden, if the field
is a secret)::

    $ datakit config set datakit-github github_api_key
    $ datakit config set datakit-project default_template gh:associatedpress/cookiecutter-r-project

Verify that configured values actually work — plugins can attach validators that
check a token authenticates or a bucket is reachable. A non-zero exit status
signals a failure, so this is handy in scripts::

    $ datakit config verify
    $ datakit config verify datakit-github

Credits
=======

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. [1] Plugins may also provide more robust docs, so don't forget to check those out when available.

.. _our plugins on Github: https://github.com/search?q=topic%3Adatakit-cli+org%3Aassociatedpress&type=Repositories
.. _uv: https://docs.astral.sh/uv/
.. _Cliff: http://docs.openstack.org/developer/cliff/index.html
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _datakit-project: http://datakit-project.readthedocs.io/en/latest/
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
