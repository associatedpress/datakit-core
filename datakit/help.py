#  THIS IS A MODIFIED COPY OF THE SOURCE FILE FROM CLIFF, UPDATED
#  TO PROVIDE A CUSTOM DISPLAY MENU FOR DATAKIT

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import argparse
import inspect
import sys
import traceback

from cliff import command

from datakit.utils import dist_for_obj


class HelpAction(argparse.Action):
    """Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        self.app = self.default
        parser.print_help(self.app.stdout)
        self.app.stdout.write('\nCommands:\n')
        command_manager = sorted(self.app.command_manager)
        # Group commands by plugin name
        grouped_cmds = {}
        for name, ep in command_manager:
            grouped_cmds\
                .setdefault(dist_for_obj(ep), [])\
                .append(ep)
        # Print built-in Cliff commands first *without* the header
        cliff_cmds = grouped_cmds.pop('cliff')
        for ep in cliff_cmds:
            self._handle_call(ep, parser, namespace, values, option_string)
        self.current_dist = None
        for plugin_dist_name, plugin_commands in sorted(grouped_cmds.items()):
            self._log_header(plugin_dist_name)
            for ep in plugin_commands:
                self._handle_call(ep, parser, namespace, values, option_string)
        self.app.stdout.write('\n')
        sys.exit(0)

    def _handle_call(self, ep, parser, namespace, values, option_string=None):
        name = ep.name
        try:
            factory = ep.load()
        except Exception:
            self.app.stdout.write('Could not load %r\n' % ep)
            if namespace.debug:
                traceback.print_exc(file=self.app.stdout)
            return
        try:
            kwargs = {}
            if 'cmd_name' in inspect.getfullargspec(factory.__init__).args:
                kwargs['cmd_name'] = name
            cmd = factory(self.app, None, **kwargs)
            if cmd.deprecated:
                return
        except Exception as err:
            self.app.stdout.write('Could not instantiate %r: %s\n' % (ep, err))
            if namespace.debug:
                traceback.print_exc(file=self.app.stdout)
            return
        one_liner = cmd.get_description().split('\n')[0]
        self._log_cmd(name, one_liner)

    def _log_header(self, dist_name):
        underline = "-" * len(dist_name)
        self.app.stdout.write('\n%s\n%s\n' % (dist_name, underline))

    def _log_cmd(self, name, one_liner):
        self.app.stdout.write('  %-13s  %s\n' % (name, one_liner))


class HelpCommand(command.Command):
    """print detailed help for another command
    """

    def get_parser(self, prog_name):
        parser = super(HelpCommand, self).get_parser(prog_name)
        parser.add_argument('cmd',
                            nargs='*',
                            help='name of the command',
                            )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.cmd:
            try:
                the_cmd = self.app.command_manager.find_command(
                    parsed_args.cmd,
                )
                cmd_factory, cmd_name, search_args = the_cmd
            except ValueError:
                # Did not find an exact match
                cmd = parsed_args.cmd[0]
                fuzzy_matches = [k[0] for k in self.app.command_manager
                                 if k[0].startswith(cmd)
                                 ]
                if not fuzzy_matches:
                    raise
                self.app.stdout.write('Command "%s" matches:\n' % cmd)
                for fm in sorted(fuzzy_matches):
                    self.app.stdout.write('  %s\n' % fm)
                return
            self.app_args.cmd = search_args
            kwargs = {}
            if 'cmd_name' in inspect.getfullargspec(cmd_factory.__init__).args:
                kwargs['cmd_name'] = cmd_name
            cmd = cmd_factory(self.app, self.app_args, **kwargs)
            full_name = (cmd_name
                         if self.app.interactive_mode
                         else ' '.join([self.app.NAME, cmd_name])
                         )
            cmd_parser = cmd.get_parser(full_name)
            cmd_parser.print_help(self.app.stdout)
        else:
            action = HelpAction(None, None, default=self.app)
            action(self.app.parser, self.app.options, None, None)
        return 0
