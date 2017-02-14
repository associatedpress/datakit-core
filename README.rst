.. image:: https://img.shields.io/pypi/v/datakit-core.svg
        :target: https://pypi.python.org/pypi/datakit-core


.. image:: https://img.shields.io/travis/associatedpress/datakit-core.svg
    :target: https://travis-ci.org/associatedpress/datakit-core
    :alt: Linux build status on Travis CI


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

For a system-wide install, from the command line::

    $ sudo pip install datakit-core

Usage
=====

Command-line
~~~~~~~~~~~~

After installing one or more plugins, Datakit can be used to invoke the
commands provided by those plugins.

Let's say you installed a plugin to create project skeletons.

To see which commands the plugin provides, try the ``--help`` flag::

    $ datakit --help

The plugin provides a ``project:create`` command, which sounds like it fits the bill.

To see which flags are available or required, try using the ``--help`` flag again::

    $ datakit project:create --help

It appears you need to specify a Cookiecutter_ template to use this command. Let's
try it::

    $ datakit project:create --template https://github.com/associatedpress/cookiecutter-r-project.git

That's the basic recipe for working with plugins: install, explore, and invoke! [1]_


Code
~~~~~
To use Datakit in a project::

    import datakit


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. [1] Plugins may also provide more robust docs, so don't forget to check those out when available.

.. _our plugins on Github: https://github.com/associatedpress
.. _Cliff: http://docs.openstack.org/developer/cliff/index.html
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
