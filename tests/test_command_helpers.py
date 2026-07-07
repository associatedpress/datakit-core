import os

from cliff.command import Command
import pytest

from datakit import CommandHelpers
from datakit.utils import mkdir_p, read_json

from .helpers import datakit_home


@pytest.fixture(autouse=True)
def setup_environment(monkeypatch, tmpdir):
    monkeypatch.setenv('DATAKIT_HOME', datakit_home(tmpdir.strpath))


class FakeCommandManager:
    """Minimal stand-in for cliff's CommandManager (only the hook namespace)."""
    namespace = "datakit.plugins"


class FakeApp:
    """Minimal cliff app stub so Command can load (empty) hooks in cliff >= 4."""
    command_manager = FakeCommandManager()


class PlainCommand(CommandHelpers, Command):
    plugin_slug = "datakit-test-plugin"

    def take_action(self, parsed_args):
        pass


class SeededCommand(PlainCommand):
    @property
    def default_configs(self):
        return {'foo': 'bar'}


@pytest.fixture
def command():
    def make(cls=PlainCommand):
        return cls(FakeApp(), None, cmd_name='datakit-test fake')
    return make


def seed_config(cmd, text):
    mkdir_p(cmd.plugin_config_parent_dir)
    with open(cmd.plugin_config_path, 'w') as fh:
        fh.write(text)


def test_plugin_config_paths(command):
    cmd = command()
    assert cmd.plugin_config_parent_dir.endswith(
        os.path.join('.datakit', 'plugins', 'datakit-test-plugin'))
    assert cmd.plugin_config_path.endswith(
        os.path.join('.datakit', 'plugins', 'datakit-test-plugin', 'config.json'))


def test_plugin_config_parent_dir_requires_plugin_slug(command):
    class NoSlugCommand(PlainCommand):
        plugin_slug = None

    with pytest.raises(ValueError):
        command(NoSlugCommand).plugin_config_parent_dir


def test_default_configs_empty_unless_overridden(command):
    assert command().default_configs == {}


def test_default_configs_override_is_honored(command):
    assert command(SeededCommand).default_configs == {'foo': 'bar'}


def test_write_configs_persists_json(command):
    cmd = command()
    cmd.write_configs({'baz': 'bang'})
    assert read_json(cmd.plugin_config_path) == {'baz': 'bang'}


def test_update_configs_merges_into_existing(command):
    cmd = command()
    cmd.write_configs({'foo': 'bar'})
    cmd.update_configs({'baz': 'bang'})
    assert read_json(cmd.plugin_config_path) == {'foo': 'bar', 'baz': 'bang'}


def test_configs_reads_existing_file(command):
    cmd = command()
    cmd.write_configs({'foo': 'bar'})
    assert cmd.configs == {'foo': 'bar'}


def test_configs_absent_file_seeds_and_persists_defaults(command):
    cmd = command(SeededCommand)
    assert cmd.configs == {'foo': 'bar'}
    assert read_json(cmd.plugin_config_path) == {'foo': 'bar'}


def test_configs_corrupt_file_self_heals_to_defaults(command):
    cmd = command(SeededCommand)
    seed_config(cmd, '{ not valid json')
    assert cmd.configs == {'foo': 'bar'}
    assert read_json(cmd.plugin_config_path) == {'foo': 'bar'}
