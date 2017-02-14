import errno
import json
import os


def home_dir():
    try:
        return os.environ['DATAKIT_HOME']
    except KeyError:
        return os.path.join(os.path.expanduser('~'), '.datakit')


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def makedirs(basepath, dirs=[]):
    return [mkdir_p(os.path.join(basepath, pth)) for pth in dirs]


def read_json(path):
    with open(path) as fh:
        return json.load(fh)


def write_json(path, data):
    with open(path, 'w') as fh:
        json.dump(data, fh)
