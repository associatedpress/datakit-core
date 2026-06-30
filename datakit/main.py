import sys
from typing import Sequence

from cliff.commandmanager import CommandManager

from . import __version__
from .datakit_app import Datakit


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) == 0:
        print("You must invoke a command, or try --help")
        return 1
    myapp = Datakit(
        description='datakit',
        version=__version__,
        command_manager=CommandManager('datakit.plugins'),
        deferred_help=True,
    )
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
