import os
import re
import shutil
import subprocess
from unittest import mock

from cliff.command import Command
import pytest

from datakit import CommandHelpers
from datakit.utils import read_json

from .helpers import (
    create_plugin_config,
    datakit_home
)


@pytest.fixture(autouse=True)
def setup_environment(monkeypatch, tmpdir):
    tmp_dir = tmpdir.strpath
    monkeypatch.setenv('DATAKIT_HOME', datakit_home(tmp_dir))


class FakeCommand(CommandHelpers, Command):

    plugin_slug = "datakit-test-plugin"

    def take_action(self, parsed_args):
        print("command invoked")


class FakeCommand2(CommandHelpers, Command):

    plugin_slug = "datakit-test-plugin2"

    def take_action(self, parsed_args):
        print("command invoked")

    @property
    def default_configs(self):
        return {'foo': 'bar'}


def test_default_properties():
    """
    Test CLI warning when project:create invoked for the first time
    without specifying a template
    """
    cmd = FakeCommand(None, None, cmd_name='my_plugin:fake_command')
    assert cmd.plugin_config_parent_dir.endswith('.datakit/plugins/datakit-test-plugin')
    assert cmd.plugin_config_path.endswith('.datakit/plugins/datakit-test-plugin/config.json')
    assert cmd.default_configs == {}


def test_default_configs_override():
    """
    Test CLI warning when project:create invoked for the first time
    without specifying a template
    """
    cmd = FakeCommand2(None, None, cmd_name='my_plugin:fake_command')
    configs = {'foo': 'bar'}
    assert cmd.default_configs == configs


def test_write_configs():
    cmd = FakeCommand(None, None, cmd_name='my_plugin:fake_command')
    configs = {'baz' : 'bang'}
    cmd.write_configs(configs)
    assert read_json(cmd.plugin_config_path) == configs


def test_update_configs(tmpdir):
    create_plugin_config(tmpdir.strpath, 'datakit-test-plugin', {'foo': 'bar'})
    cmd = FakeCommand(None, None, cmd_name='my_plugin:fake_command')
    assert cmd.configs == {'foo': 'bar'}
    cmd.update_configs({'baz': 'bang'})
    assert read_json(cmd.plugin_config_path) == {'foo': 'bar', 'baz': 'bang'}


def test_configs_no_file():
    cmd = FakeCommand(None, None, cmd_name='my_plugin:fake_command')
    assert cmd.configs == {}


def test_configs_with_file(tmpdir):
    create_plugin_config(tmpdir.strpath, 'datakit-test-plugin', {'foo': 'bar'})
    cmd = FakeCommand(None, None, cmd_name='my_plugin:fake_command')
    assert cmd.configs == {'foo': 'bar'}
