import logging
import json
import os

import datakit.utils

from .utils import read_json, write_json


class CommandHelpers:

    """
    Mixin class containing common helper methods for Datakit plugins.
    Intended to be sub-classed alongside Cliff Command.

    :Usage:

    * Create a plugin command that subclasses both CommandHelpers and Cliff's `Command class <http://docs.openstack.org/developer/cliff/classes.html#command>`_.
    * Define :py:attr:`CommandHelpers.plugin_slug` (i.e. the root of plugin's repo).
    * Optionally, customize the :py:attr:`CommandHelpers.default_configs` property (which must
        return a dictionary)

    .. note:: *default_configs* is a `property <https://docs.python.org/3/library/functions.html#property>`_.
        Please do not forget to use the decorator when you override in a subclass!


    :Example:


    .. code::

        from cliff.command import Command
        from datakit import CommandHelpers

        class SomeCommand(CommandHelpers, Command):

            plugin_slug = 'my-plugin'

            def take_action(self, parsed):
                print('do stuff')

            @property
            def default_configs(self):
                return { 'foo' : 'bar' }

    """

    log = logging.getLogger(__name__)
    plugin_slug = None

    def update_configs(self, new_configs):
        configs = self.configs
        configs.update(new_configs)
        self.write_configs(configs)
        return configs

    def write_configs(self, configs):
        datakit.utils.mkdir_p(self.plugin_config_parent_dir)
        write_json(self.plugin_config_path, configs)

    @property
    def configs(self):
        try:
            configs = read_json(self.plugin_config_path)
        except FileNotFoundError:
            configs = self.default_configs
            self.write_configs(configs)
        return configs

    @property
    def plugin_config_parent_dir(self):
        return os.path.join(
            datakit.utils.home_dir(),
            'plugins',
            self.plugin_slug
        )

    @property
    def plugin_config_path(self):
        return os.path.join(
            self.plugin_config_parent_dir,
            'config.json'
        )

    @property
    def default_configs(self):
        return {}
