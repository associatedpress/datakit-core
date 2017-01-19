import sys

from cliff.app import App
from cliff.commandmanager import CommandManager


class Datakit(App):

    def __init__(self):
        super(Datakit, self).__init__(
            description='datakit',
            version='0.1',
            command_manager=CommandManager('datakit.plugins'),
            deferred_help=True,
            )


def main(argv=sys.argv[1:]):
    if len(argv) == 0:
        print("You must invoke a command, or try --help")
    else:
        myapp = Datakit()
        return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
