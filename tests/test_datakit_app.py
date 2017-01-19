
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
