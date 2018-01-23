from cliff import _argparse
from cliff.app import App

from datakit import help


class Datakit(App):

    def __init__(self, *args, **kwargs):
        super(Datakit, self).__init__(*args, **kwargs)
        self.command_manager.add_command('help', help.HelpCommand)

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        """Return an argparse option parser for this application.
        Subclasses may override this method to extend
        the parser with more global options.
        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        :param argparse_kwargs: extra keyword argument passed to the
                                ArgumentParser constructor
        :paramtype extra_kwargs: dict
        """
        argparse_kwargs = argparse_kwargs or {}
        parser = _argparse.ArgumentParser(
            description=description,
            add_help=False,
            **argparse_kwargs
        )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
        )
        verbose_group = parser.add_mutually_exclusive_group()
        verbose_group.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )
        verbose_group.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='Suppress output except warnings and errors.',
        )
        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='Specify a file to log output. Disabled by default.',
        )
        if self.deferred_help:
            parser.add_argument(
                '-h', '--help',
                dest='deferred_help',
                action='store_true',
                help="Show help message and exit.",
            )
        else:
            parser.add_argument(
                '-h', '--help',
                action=help.HelpAction,
                nargs=0,
                default=self,  # tricky
                help="Show help message and exit.",
            )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Show tracebacks on errors.',
        )
        return parser

    def print_help_if_requested(self):
        """Print help and exits if deferred help is enabled and requested.
        '--help' shows the help message and exits:
         * without calling initialize_app if not self.deferred_help (default),
         * after initialize_app call if self.deferred_help,
         * during initialize_app call if self.deferred_help and subclass calls
           explicitly this method in initialize_app.
        """
        if self.deferred_help and self.options.deferred_help:
            action = help.HelpAction(None, None, default=self)
            action(self.parser, self.options, None, None)
