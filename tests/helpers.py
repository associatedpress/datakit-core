import os

from datakit.utils import mkdir_p, write_json


def datakit_home(tmpdir):
    return os.path.join(tmpdir, '.datakit')


def create_plugin_config(root_dir, project_name, content):
    dkit_home = datakit_home(root_dir)
    plugin_dir = os.path.join(dkit_home, 'plugins', project_name)
    mkdir_p(plugin_dir)
    config_file = os.path.join(plugin_dir, 'config.json')
    write_json(config_file, content)
    return content
