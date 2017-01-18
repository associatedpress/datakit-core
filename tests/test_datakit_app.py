
from datakit.main import Datakit


def test_interactive_mode_override(caplog):
    """
    Datakit should short-circuit Cliff's potentially confusing
    default behavior of dropping into interactive
    mode when no command-line arguments are specified.
    """
    app = Datakit()
    app.run([''])
    msg = "You must supply a command, or try the --help flag."
    assert app.interactive_mode == False
    assert msg in caplog.text
