import sys

from cliff.commandmanager import CommandManager

from .datakit_app import Datakit


def main(argv=sys.argv[1:]):
    if len(argv) == 0:
        print("You must invoke a command, or try --help")
    else:
        myapp = Datakit(
            description='datakit',
            version='0.3.0',
            command_manager=CommandManager('datakit.plugins'),
            deferred_help=True,
        )
        return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
