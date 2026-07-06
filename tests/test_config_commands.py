import io

import pytest

from datakit.commands import config as config_cmds
from datakit.config import ConfigField, PluginConfig

from .helpers import create_plugin_config, datakit_home


@pytest.fixture(autouse=True)
def setup_environment(monkeypatch, tmpdir):
    monkeypatch.setenv('DATAKIT_HOME', datakit_home(tmpdir.strpath))


class FakeEntryPoint:
    def __init__(self, cls):
        self._cls = cls

    def load(self):
        return self._cls


class FakeCommandManager:
    namespace = 'datakit.plugins'

    def __init__(self, entry_points):
        self._entry_points = entry_points

    def __iter__(self):
        return iter(self._entry_points)


class FakeApp:
    def __init__(self, entry_points):
        self.command_manager = FakeCommandManager(entry_points)
        self.stdout = io.StringIO()


class GithubCmd:
    plugin_slug = 'datakit-github'
    config_spec = [
        ConfigField('github_api_key', required=True, secret=True,
                    help='GitHub token'),
        ConfigField('org', help='Default org'),
    ]


def make_app():
    return FakeApp([('github integrate', FakeEntryPoint(GithubCmd))])


def run(command_cls, argv, app):
    cmd = command_cls(app, None, cmd_name=command_cls.__name__)
    parser = cmd.get_parser(command_cls.__name__)
    parsed = parser.parse_args(argv)
    result = cmd.take_action(parsed)
    return app.stdout.getvalue(), result


# --- list -----------------------------------------------------------------

def test_list_shows_missing_and_masks(tmpdir):
    create_plugin_config(tmpdir.strpath, 'datakit-github',
                         {'github_api_key': 'secret-token'})
    out, _ = run(config_cmds.ConfigList, [], make_app())
    assert 'datakit-github' in out
    assert '[set]' in out
    assert '********' in out
    assert 'secret-token' not in out
    # org is optional and unset
    assert '[unset]' in out


def test_list_no_plugins():
    out, _ = run(config_cmds.ConfigList, [], FakeApp([]))
    assert 'No installed plugins' in out


# --- set ------------------------------------------------------------------

def test_set_with_value_persists():
    app = make_app()
    out, _ = run(config_cmds.ConfigSet, ['datakit-github', 'org', 'ap'], app)
    assert PluginConfig('datakit-github').read()['org'] == 'ap'
    assert 'ap' in out


def test_set_secret_prompts_and_masks(monkeypatch):
    monkeypatch.setattr(config_cmds, 'prompt_secret', lambda msg: 'typed-token')
    app = make_app()
    out, _ = run(config_cmds.ConfigSet, ['datakit-github', 'github_api_key'], app)
    assert PluginConfig('datakit-github').read()['github_api_key'] == 'typed-token'
    assert 'typed-token' not in out
    assert '********' in out


def test_set_unknown_plugin_exits():
    with pytest.raises(SystemExit):
        run(config_cmds.ConfigSet, ['nope', 'k', 'v'], make_app())


def test_set_unknown_key_exits():
    with pytest.raises(SystemExit):
        run(config_cmds.ConfigSet, ['datakit-github', 'bogus', 'v'], make_app())


# --- verify ---------------------------------------------------------------

def test_verify_required_missing_exits(tmpdir):
    with pytest.raises(SystemExit):
        run(config_cmds.ConfigVerify, [], make_app())


def test_verify_runs_validator(tmpdir, monkeypatch):
    checked = []

    class ValidatedCmd:
        plugin_slug = 'datakit-val'
        config_spec = [
            ConfigField('endpoint', required=True,
                        validator=lambda v: checked.append(v) or True),
        ]

    create_plugin_config(tmpdir.strpath, 'datakit-val', {'endpoint': 'http://x'})
    app = FakeApp([('val cmd', FakeEntryPoint(ValidatedCmd))])
    out, _ = run(config_cmds.ConfigVerify, [], app)
    assert checked == ['http://x']
    assert 'OK' in out


# --- init -----------------------------------------------------------------

def test_init_prompts_unset_fields(monkeypatch):
    answers = iter(['ap'])          # org (optional)
    secrets = iter(['tok'])         # github_api_key (secret, required)
    monkeypatch.setattr(config_cmds, 'prompt', lambda msg: next(answers))
    monkeypatch.setattr(config_cmds, 'prompt_secret', lambda msg: next(secrets))
    app = make_app()
    run(config_cmds.ConfigInit, [], app)
    saved = PluginConfig('datakit-github').read()
    assert saved == {'github_api_key': 'tok', 'org': 'ap'}


def test_init_reprompts_required_when_blank(monkeypatch):
    secrets = iter(['', 'finally'])   # blank first, then a value
    monkeypatch.setattr(config_cmds, 'prompt', lambda msg: '')      # org left blank
    monkeypatch.setattr(config_cmds, 'prompt_secret', lambda msg: next(secrets))
    app = make_app()
    run(config_cmds.ConfigInit, [], app)
    saved = PluginConfig('datakit-github').read()
    assert saved['github_api_key'] == 'finally'
    assert 'org' not in saved  # optional + blank stays unset
