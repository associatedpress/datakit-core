import errno
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
    build_pth = lambda directory: os.path.join(basepath, directory)
    [mkdir_p(build_pth(pth)) for pth in dirs]
