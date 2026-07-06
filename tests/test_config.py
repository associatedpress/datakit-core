import pytest

from datakit.config import (
    MASK,
    MISSING,
    SET,
    UNSET,
    ConfigField,
    PluginConfig,
    discover_plugin_configs,
    run_validator,
)

from .helpers import create_plugin_config, datakit_home


@pytest.fixture(autouse=True)
def setup_environment(monkeypatch, tmpdir):
    monkeypatch.setenv('DATAKIT_HOME', datakit_home(tmpdir.strpath))


# --- ConfigField ----------------------------------------------------------

def test_field_status():
    required = ConfigField('key', required=True)
    optional = ConfigField('key')
    assert required.status('value') == SET
    assert required.status('') == MISSING
    assert required.status(None) == MISSING
    assert optional.status(None) == UNSET


def test_field_display_masks_secrets():
    secret = ConfigField('token', secret=True)
    plain = ConfigField('bucket')
    assert secret.display('s3kr3t') == MASK
    assert plain.display('my-bucket') == 'my-bucket'
    assert plain.display(None) is None


# --- PluginConfig ---------------------------------------------------------

def test_plugin_config_read_missing_returns_empty():
    assert PluginConfig('datakit-test').read() == {}


def test_plugin_config_read_existing(tmpdir):
    create_plugin_config(tmpdir.strpath, 'datakit-test', {'foo': 'bar'})
    assert PluginConfig('datakit-test').read() == {'foo': 'bar'}


def test_plugin_config_set_value_roundtrip():
    plugin = PluginConfig('datakit-test')
    plugin.set_value('foo', 'bar')
    plugin.set_value('baz', 'bang')
    assert plugin.read() == {'foo': 'bar', 'baz': 'bang'}


def test_plugin_config_field_lookup():
    field = ConfigField('foo')
    plugin = PluginConfig('datakit-test', [field])
    assert plugin.field('foo') is field
    assert plugin.field('nope') is None


def test_merge_spec_dedups_by_name():
    plugin = PluginConfig('datakit-test', [ConfigField('a')])
    plugin.merge_spec([ConfigField('a'), ConfigField('b')])
    assert [f.name for f in plugin.spec] == ['a', 'b']


# --- discovery ------------------------------------------------------------

class FakeEntryPoint:
    def __init__(self, cls):
        self._cls = cls

    def load(self):
        return self._cls


class BrokenEntryPoint:
    def load(self):
        raise ImportError('boom')


class FakeCommandManager:
    def __init__(self, entry_points):
        self._entry_points = entry_points

    def __iter__(self):
        return iter(self._entry_points)


def test_discover_groups_and_skips():
    class GithubCmd:
        plugin_slug = 'datakit-github'
        config_spec = [ConfigField('github_api_key', required=True, secret=True)]

    class GithubOther:
        plugin_slug = 'datakit-github'
        config_spec = [ConfigField('github_api_key'), ConfigField('org')]

    class NoSpec:
        plugin_slug = 'datakit-nope'
        config_spec = []

    cm = FakeCommandManager([
        ('github integrate', FakeEntryPoint(GithubCmd)),
        ('github other', FakeEntryPoint(GithubOther)),
        ('no spec', FakeEntryPoint(NoSpec)),
        ('broken', BrokenEntryPoint()),
    ])
    plugins = discover_plugin_configs(cm)
    assert set(plugins) == {'datakit-github'}
    # merged, deduped by name
    assert [f.name for f in plugins['datakit-github'].spec] == ['github_api_key', 'org']


# --- validators -----------------------------------------------------------

def test_run_validator_none_passes():
    assert run_validator(ConfigField('k'), 'v') == (True, '')


def test_run_validator_bool():
    ok = ConfigField('k', validator=lambda v: v == 'good')
    assert run_validator(ok, 'good') == (True, '')
    assert run_validator(ok, 'bad')[0] is False


def test_run_validator_tuple_message():
    field = ConfigField('k', validator=lambda v: (False, 'nope'))
    assert run_validator(field, 'x') == (False, 'nope')


def test_run_validator_exception_is_failure():
    def boom(value):
        raise RuntimeError('unreachable')

    ok, message = run_validator(ConfigField('k', validator=boom), 'x')
    assert ok is False
    assert 'unreachable' in message
