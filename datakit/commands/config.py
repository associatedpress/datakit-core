"""The generic ``datakit config`` command family.

These commands drive every installed plugin's declarative ``config_spec`` (see
:mod:`datakit.config`). Core stays pluggable: it discovers specs through the
``datakit.plugins`` entry-point group rather than hardcoding any plugin.
"""
import getpass
from typing import Optional

from cliff.command import Command

from datakit.config import (
    ConfigField,
    PluginConfig,
    discover_plugin_configs,
    run_validator,
)


# Indirection so tests can monkeypatch prompting without patching builtins.
def prompt(message: str) -> str:
    return input(message)


def prompt_secret(message: str) -> str:
    return getpass.getpass(message)


def _prompt_field(field: ConfigField) -> str:
    """Prompt once for a field, using getpass for secrets and showing default."""
    label = field.help or field.name
    suffix = f" [{field.default}]" if field.default not in (None, "") else ""
    message = f"  {label}{suffix}: "
    value = (prompt_secret(message) if field.secret else prompt(message)).strip()
    if not value and field.default not in (None, ""):
        return str(field.default)
    return value


class _ConfigCommand(Command):
    """Shared helpers for the config subcommands."""

    def discover(self) -> dict[str, PluginConfig]:
        return discover_plugin_configs(self.app.command_manager)

    def out(self, message: str = "") -> None:
        self.app.stdout.write(message + "\n")


class ConfigList(_ConfigCommand):
    "List configuration status for every installed plugin"

    def take_action(self, parsed_args):
        plugins = self.discover()
        if not plugins:
            self.out("No installed plugins declare a config spec.")
            return
        for slug in sorted(plugins):
            plugin = plugins[slug]
            configs = plugin.read()
            self.out(slug)
            width = max((len(f.name) for f in plugin.spec), default=0)
            for f in plugin.spec:
                status = f.status(configs.get(f.name))
                display = f.display(configs.get(f.name))
                flags = []
                if f.required:
                    flags.append("required")
                if f.secret:
                    flags.append("secret")
                flag_str = f" ({', '.join(flags)})" if flags else ""
                value_str = f" {display}" if display is not None else ""
                self.out(f"  {f.name.ljust(width)}  [{status}]{value_str}{flag_str}")
            self.out()


class ConfigStatus(ConfigList):
    "Alias for `config list`"


class ConfigSet(_ConfigCommand):
    "Set a configuration value for a plugin"

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument("plugin", help="plugin slug (e.g. datakit-github)")
        parser.add_argument("key", help="config key to set")
        parser.add_argument(
            "value",
            nargs="?",
            help="value to set; prompted for (hidden, if secret) when omitted",
        )
        return parser

    def take_action(self, parsed_args):
        plugins = self.discover()
        plugin = plugins.get(parsed_args.plugin)
        if plugin is None:
            self.out(f"ERROR: unknown plugin '{parsed_args.plugin}'.")
            if plugins:
                self.out("Known plugins: {}".format(", ".join(sorted(plugins))))
            raise SystemExit(1)
        field = plugin.field(parsed_args.key)
        if field is None:
            self.out(f"ERROR: '{parsed_args.key}' is not a config key for {plugin.slug}.")
            keys = ", ".join(f.name for f in plugin.spec)
            if keys:
                self.out(f"Valid keys: {keys}")
            raise SystemExit(1)
        value = parsed_args.value
        if value is None:
            value = _prompt_field(field)
        plugin.set_value(field.name, value)
        shown = field.display(value)
        self.out(f"Set {plugin.slug}.{field.name} = {shown}")


class ConfigVerify(_ConfigCommand):
    "Run validators for configured values, checking they actually work"

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "plugin",
            nargs="?",
            help="limit verification to a single plugin slug",
        )
        return parser

    def take_action(self, parsed_args):
        plugins = self._selected(parsed_args.plugin)
        failures = 0
        for slug in sorted(plugins):
            plugin = plugins[slug]
            configs = plugin.read()
            self.out(slug)
            for f in plugin.spec:
                value = configs.get(f.name)
                if not f.is_set(value):
                    if f.required:
                        failures += 1
                        self.out(f"  {f.name}: MISSING (required)")
                    else:
                        self.out(f"  {f.name}: unset (optional)")
                    continue
                if f.validator is None:
                    self.out(f"  {f.name}: set")
                    continue
                ok, message = run_validator(f, value)
                if ok:
                    self.out(f"  {f.name}: OK")
                else:
                    failures += 1
                    detail = f" ({message})" if message else ""
                    self.out(f"  {f.name}: FAILED{detail}")
            self.out()
        if failures:
            raise SystemExit(1)

    def _selected(self, plugin: Optional[str]) -> dict[str, PluginConfig]:
        plugins = self.discover()
        if plugin is None:
            return plugins
        if plugin not in plugins:
            self.out(f"ERROR: unknown plugin '{plugin}'.")
            raise SystemExit(1)
        return {plugin: plugins[plugin]}


class ConfigInit(_ConfigCommand):
    "Interactively fill in unset configuration values"

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "plugin",
            nargs="?",
            help="limit init to a single plugin slug",
        )
        return parser

    def take_action(self, parsed_args):
        plugins = self.discover()
        if parsed_args.plugin is not None:
            if parsed_args.plugin not in plugins:
                self.out(f"ERROR: unknown plugin '{parsed_args.plugin}'.")
                raise SystemExit(1)
            plugins = {parsed_args.plugin: plugins[parsed_args.plugin]}
        for slug in sorted(plugins):
            self._init_plugin(plugins[slug])

    def _init_plugin(self, plugin: PluginConfig) -> None:
        configs = plugin.read()
        unset = [f for f in plugin.spec if not f.is_set(configs.get(f.name))]
        if not unset:
            return
        self.out(f"Configuring {plugin.slug}:")
        updated = dict(configs)
        for f in unset:
            value = _prompt_field(f)
            # Keep asking required fields until we get something usable.
            while not value and f.required:
                self.out(f"  {f.name} is required.")
                value = _prompt_field(f)
            if value:
                updated[f.name] = value
        plugin.write(updated)
        self.out(f"Saved {plugin.config_path}")
        self.out()
