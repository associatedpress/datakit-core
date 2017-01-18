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

    def initialize_app(self, argv):
        # Disable interactive mode
        self.interactive_mode = False
        self.LOG.info('You must supply a command, or try the --help flag.')


def main(argv=sys.argv[1:]):
    myapp = Datakit()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
