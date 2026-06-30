import errno
import json
import os
from typing import Any


def home_dir() -> str:
    try:
        return os.environ['DATAKIT_HOME']
    except KeyError:
        return os.path.join(os.path.expanduser('~'), '.datakit')


def mkdir_p(path: str) -> None:
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def read_json(path: str) -> Any:
    with open(path) as fh:
        return json.load(fh)


def write_json(path: str, data: Any, indent: int = 4) -> None:
    with open(path, 'w') as fh:
        json.dump(data, fh, indent=indent)


def dist_for_obj(obj: Any) -> str:
    try:
        dist = obj.dist.name
        version = obj.dist.version
        if version:
            dist += " ({})".format(version)
        return dist
    except AttributeError:
        # Raised for Cliff, which returns an
        # EntryPointWrapper object
        return 'cliff'
