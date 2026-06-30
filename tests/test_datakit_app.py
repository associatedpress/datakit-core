from unittest import mock

from datakit.datakit_app import Datakit
from datakit.main import main as dk_main


def test_interactive_mode_override(capsys):
    """
    Datakit should default to displaying simple help text
    when no command line arguments are supplied.

    This short-circuits Cliff's potentially confusing
    default behavior of dropping into interactive mode.
    """
    dk_main([])
    out, err = capsys.readouterr()
    assert 'You must invoke a command' in out


def test_main_reads_argv_from_sys_when_none_given(mocker, capsys):
    mocker.patch('sys.argv', ['datakit'])
    dk_main()
    out, err = capsys.readouterr()
    assert 'You must invoke a command' in out


def test_main_dispatches_to_app_run(mocker):
    """
    Datakit should build a real Datakit app and hand off argv
    when arguments are supplied.
    """
    run_mock = mocker.patch.object(Datakit, 'run', return_value=0)
    result = dk_main(['help'])
    run_mock.assert_called_once_with(['help'])
    assert result == 0


def test_print_help_if_requested_exits_when_deferred_and_requested():
    app = Datakit(
        description='datakit',
        version='1',
        command_manager=mock.Mock(),
        deferred_help=True,
    )
    app.options = mock.Mock(deferred_help=True)
    with mock.patch('datakit.help.HelpAction.__call__') as call_mock:
        app.print_help_if_requested()
    call_mock.assert_called_once()


def test_print_help_if_requested_noop_when_not_requested():
    app = Datakit(
        description='datakit',
        version='1',
        command_manager=mock.Mock(),
        deferred_help=True,
    )
    app.options = mock.Mock(deferred_help=False)
    with mock.patch('datakit.help.HelpAction.__call__') as call_mock:
        app.print_help_if_requested()
    call_mock.assert_not_called()
