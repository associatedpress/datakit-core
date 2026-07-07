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


# --- prompt plumbing ------------------------------------------------------

def test_prompt_wraps_builtin_input(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda msg: f'echo:{msg}')
    assert config_cmds.prompt('name? ') == 'echo:name? '


def test_prompt_secret_wraps_getpass(monkeypatch):
    monkeypatch.setattr('getpass.getpass', lambda msg: f'hidden:{msg}')
    assert config_cmds.prompt_secret('token? ') == 'hidden:token? '


def test_prompt_field_falls_back_to_default_when_blank(monkeypatch):
    monkeypatch.setattr(config_cmds, 'prompt', lambda msg: '')
    field = ConfigField('region', default='us-east-1')
    assert config_cmds._prompt_field(field) == 'us-east-1'


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


def test_set_secret_dedupes_double_paste(monkeypatch):
    class GitlabCmd:
        plugin_slug = 'datakit-gitlab'
        config_spec = [
            ConfigField('api_key', required=True, secret=True,
                        dedupe_prefix='glpat-', help='GitLab token'),
        ]

    # Terminal concatenates a token pasted twice into one line.
    monkeypatch.setattr(config_cmds, 'prompt_secret',
                        lambda msg: 'glpat-abc123glpat-abc123')
    app = FakeApp([('gitlab integrate', FakeEntryPoint(GitlabCmd))])
    run(config_cmds.ConfigSet, ['datakit-gitlab', 'api_key'], app)
    assert PluginConfig('datakit-gitlab').read()['api_key'] == 'glpat-abc123'


def test_dedupe_paste_variants():
    d = config_cmds._dedupe_paste
    # single paste is untouched
    assert d('glpat-abc123', 'glpat-') == 'glpat-abc123'
    # triple paste collapses to first token
    assert d('glpat-Xglpat-Xglpat-X', 'glpat-') == 'glpat-X'
    # whitespace/newline between pastes is trimmed off
    assert d('glpat-X\nglpat-X', 'glpat-') == 'glpat-X'
    # value not starting with the prefix is left alone
    assert d('sometoken', 'glpat-') == 'sometoken'


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


def test_verify_set_without_validator_reports_set(tmpdir):
    create_plugin_config(tmpdir.strpath, 'datakit-github',
                         {'github_api_key': 'tok', 'org': 'ap'})
    out, _ = run(config_cmds.ConfigVerify, [], make_app())
    assert 'org: set' in out


def test_verify_failed_validator_reports_message_and_exits(tmpdir):
    class ValidatedCmd:
        plugin_slug = 'datakit-val'
        config_spec = [
            ConfigField('endpoint', required=True,
                        validator=lambda v: (False, 'unreachable')),
        ]

    create_plugin_config(tmpdir.strpath, 'datakit-val', {'endpoint': 'http://x'})
    app = FakeApp([('val cmd', FakeEntryPoint(ValidatedCmd))])
    with pytest.raises(SystemExit):
        run(config_cmds.ConfigVerify, ['datakit-val'], app)
    assert 'FAILED (unreachable)' in app.stdout.getvalue()


def test_verify_single_plugin_filter(tmpdir):
    create_plugin_config(tmpdir.strpath, 'datakit-github',
                         {'github_api_key': 'tok'})
    out, _ = run(config_cmds.ConfigVerify, ['datakit-github'], make_app())
    assert 'datakit-github' in out


def test_verify_unknown_plugin_exits():
    with pytest.raises(SystemExit):
        run(config_cmds.ConfigVerify, ['nope'], make_app())


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


def test_init_single_plugin_filter(monkeypatch):
    monkeypatch.setattr(config_cmds, 'prompt', lambda msg: 'ap')
    monkeypatch.setattr(config_cmds, 'prompt_secret', lambda msg: 'tok')
    app = make_app()
    run(config_cmds.ConfigInit, ['datakit-github'], app)
    assert PluginConfig('datakit-github').read() == {'github_api_key': 'tok',
                                                     'org': 'ap'}


def test_init_unknown_plugin_exits():
    with pytest.raises(SystemExit):
        run(config_cmds.ConfigInit, ['nope'], make_app())


def test_init_skips_fully_configured_plugin(tmpdir, monkeypatch):
    create_plugin_config(tmpdir.strpath, 'datakit-github',
                         {'github_api_key': 'tok', 'org': 'ap'})

    def refuse(msg):
        raise AssertionError('should not prompt when everything is set')

    monkeypatch.setattr(config_cmds, 'prompt', refuse)
    monkeypatch.setattr(config_cmds, 'prompt_secret', refuse)
    out, _ = run(config_cmds.ConfigInit, [], make_app())
    assert out == ''
