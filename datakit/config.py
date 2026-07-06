"""Declarative configuration schema shared by all datakit plugins.

Each plugin declares *what* configuration it needs by attaching a ``config_spec``
(a list of :class:`ConfigField`) to its command class(es). The generic
``datakit config`` command (see :mod:`datakit.commands.config`) discovers those
specs across every installed plugin and drives listing, setting, verifying and
initializing the on-disk config without core needing to know about any specific
plugin.
"""
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .utils import home_dir, mkdir_p, read_json, write_json

MASK = "********"

# Field status values returned by :func:`field_status`.
SET = "set"
UNSET = "unset"
MISSING = "missing"  # required but unset


@dataclass
class ConfigField:
    """One configurable option a plugin exposes.

    :param name: the config key (as stored in ``config.json``).
    :param required: whether the plugin needs this value to function.
    :param secret: mask the value when displaying (e.g. API keys, tokens).
    :param help: human-readable description shown in prompts and listings.
    :param default: value offered when prompting; also seeds ``init``.
    :param validator: optional callable ``value -> bool | (bool, message)`` used
        by ``datakit config verify`` to check the value actually works (e.g.
        reach an S3 bucket, hit an API). May raise; exceptions are treated as a
        failed check.
    """

    name: str
    required: bool = False
    secret: bool = False
    help: str = ""
    default: Any = None
    validator: Optional[Callable[[Any], Any]] = None

    def is_set(self, value: Any) -> bool:
        return value is not None and value != ""

    def status(self, value: Any) -> str:
        if self.is_set(value):
            return SET
        return MISSING if self.required else UNSET

    def display(self, value: Any) -> Optional[str]:
        """Value as it should be shown to a human (secrets masked)."""
        if not self.is_set(value):
            return None
        if self.secret:
            return MASK
        return str(value)


class PluginConfig:
    """Read/write access to a single plugin's on-disk config, driven by its spec.

    Mirrors the ``~/.datakit/plugins/<slug>/config.json`` convention used by
    :class:`datakit.CommandHelpers`, but works standalone (no cliff/app
    instance required) so the config engine can operate on any discovered
    plugin.
    """

    def __init__(self, slug: str, spec: Optional[list[ConfigField]] = None) -> None:
        self.slug = slug
        self.spec: list[ConfigField] = list(spec) if spec else []

    @property
    def config_dir(self) -> str:
        return os.path.join(home_dir(), "plugins", self.slug)

    @property
    def config_path(self) -> str:
        return os.path.join(self.config_dir, "config.json")

    def read(self) -> dict[str, Any]:
        try:
            return read_json(self.config_path)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def write(self, configs: dict[str, Any]) -> None:
        mkdir_p(self.config_dir)
        write_json(self.config_path, configs)

    def set_value(self, key: str, value: Any) -> dict[str, Any]:
        configs = self.read()
        configs[key] = value
        self.write(configs)
        return configs

    def field(self, name: str) -> Optional[ConfigField]:
        for f in self.spec:
            if f.name == name:
                return f
        return None

    def merge_spec(self, spec: list[ConfigField]) -> None:
        """Add fields from ``spec`` not already present (dedup by name).

        A plugin's commands may each carry the (same) spec, or only one command
        may declare it; merging keeps a single deduplicated view per plugin.
        """
        existing = {f.name for f in self.spec}
        for f in spec:
            if f.name not in existing:
                self.spec.append(f)
                existing.add(f.name)


def discover_plugin_configs(command_manager: Any) -> dict[str, PluginConfig]:
    """Map ``slug -> PluginConfig`` for every installed plugin declaring a spec.

    Iterates the cliff command manager's entry points (the ``datakit.plugins``
    group), loads each command class and reads its ``plugin_slug`` /
    ``config_spec`` class attributes. Commands that fail to load, or that don't
    declare a spec, are skipped.
    """
    plugins: dict[str, PluginConfig] = {}
    for entry in command_manager:
        # cliff yields (name, entry_point) tuples when iterated.
        ep = entry[1] if isinstance(entry, tuple) else entry
        try:
            cls = ep.load()
        except Exception:
            continue
        slug = getattr(cls, "plugin_slug", None)
        spec = getattr(cls, "config_spec", None)
        if not slug or not spec:
            continue
        if slug in plugins:
            plugins[slug].merge_spec(spec)
        else:
            plugins[slug] = PluginConfig(slug, spec)
    return plugins


def run_validator(field: ConfigField, value: Any) -> tuple[bool, str]:
    """Run a field's validator, normalizing its result to ``(ok, message)``."""
    if field.validator is None:
        return True, ""
    try:
        result = field.validator(value)
    except Exception as err:  # a validator that raises is a failed check
        return False, str(err)
    if isinstance(result, tuple):
        ok, message = (result + ("",))[:2]
        return bool(ok), str(message)
    return bool(result), ""
