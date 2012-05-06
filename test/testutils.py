import os
import inspect
import errno
import tempfile
from itertools import cycle
import fakes


# The parametrize decorator populates this list. It is then used in
# conftest.py:pytest_generate_tests() to generate the parameters for each
# test.
args_params = []


# Each funcarg function starts with this signature. The remaining portion
# of the function name is the name of the argument being generated.
FN_STARTSWITH = 'pytest_funcarg__'
STARTSWITH_LEN = len(FN_STARTSWITH)


def parametrize(params):
    """A decorator factory for funcarg functions to track parameter names.

    Funcarg functions provide the input args for each test function. By
    using pytest "parameters" multiple test runs can be generated for a
    single test function. In order to cut down on the boilerplate we can
    define a decorator passing a list of the parameter names. These are
    stored along with the name of the argument that the decorated funcarag
    function is generating.  The resulting list "args_params" should
    ultimately be used in a pytest_generate_tests() function as the input
    arguments to metafunc.parametrize().

    This allows us to specify the parameter names alongside the funcarg
    function rather than in a separate conftest.py file."""

    def decorator(fn):
        # This is the decorator we return. It saves the parameter details
        # and return the original (unwrapped) function.
        if not fn.__name__.startswith(FN_STARTSWITH):
            raise ValueError('%s is not a pytest funcarg function. ' \
                             'Must start with "%s"' % \
                             (fn.__name__, FN_STARTSWITH))

        arg_name = fn.__name__[STARTSWITH_LEN:]
        args_params.append((arg_name, params))

        # No need to wrap the function, we only wanted the function name
        # and parameters
        return fn

    return decorator


def splitdrive(path):
    if os.pathsep in path:
        drive, rpath = path.split(os.pathsep)
        return drive, rpath
    else:
        return '', path


def joindrive(drive, path):
    return os.path.pathsep.join([drive, path])


def funcname(up=0):
    """Return the name of the caller function or any parent."""
    return inspect.stack()[1 + up][3]


def make_fake_files(root, num, exts=[''], ndupes=0):
    if not num:
        return []
    if ndupes >= num:
        raise ValueError('Total number of files (%d) must be greater than '
                         'the number of duplicates (%d). The number of '
                         'unique files will be num-total less '
                         'num-duplicates' % (num, ndupes))

    paths = []
    for name in xfake_names(num - ndupes, exts):
        path = os.path.join(root, name)
        mknod(path)
        paths.append(path)

    for _, srcpath, dstdir in zip(range(ndupes),
                                  cycle(paths), fake_dirs('tmp')):
        srcfile = os.path.split(srcpath)[1]
        dstfile = os.path.join(root, dstdir, srcfile)
        mknod(dstfile)
        paths.append(dstfile)

    return paths


def make_dir_files(root, dirs, files):
    make_dirs(dirs)
    for dirs, files in dirs_files:
        for d in dirs:
            os.mkdir(os.path.join(root, d))
        for f in files:
            os.mknod(os.path.join(root, f))


def make_dirs(paths):
    for path in paths:
        mkdir(path)


def make_files(paths):
    for path in paths:
        mknod(path)


def mkdir(path):
    # split the path in one go
    parts = os.path.normpath(path).split(os.path.sep)
    parent, ex = '', None
    for part in parts:
        if part == '':
            # skip leading path sep
            parent = os.path.sep
            continue

        dir_path = os.path.join(parent, part)
        ex = None
        try:
            os.mkdir(dir_path)
        except OSError, ex:
            pass
        parent = dir_path
    if ex:
        raise ex


def mknod(path):
    dirname, _ = os.path.split(path)
    try:
        mkdir(dirname)
    except OSError, ex:
        if ex.errno != errno.EEXIST:
            raise
    os.mknod(path)


def fake_dirs(prefix=''):
    dirs = ['extra/la-kitchen', 'extra/mapping', 'cyclone',
            'dir1/dir2/dir3/dir2']
    for d in cycle(dirs):
        yield os.path.join(prefix, d)


def xfake_names(num, exts=[''], with_dir=True):
    """A generator for PD object names.

    The names are not ordinary PD names, they are auto-generated. A
    list of extensions may be passed in which will be used in turn in
    generating the names."""

    for _, root, ext in zip(range(num), fake_dirs(), cycle(exts)):
        filename = tempfile.mktemp(suffix=ext, prefix='pd_', dir='')
        val_list = with_dir and [root, filename] or [filename]
        yield '/'.join(val_list)


def fake_names(*args, **kwargs):
    return [n for n in xfake_names(*args, **kwargs)]


#def xfake_paths_exts(num, root=''):
    #for _, path, ext in zip(range(num), fake_dirs(), cycle(pypd.Ext.valid)):
        #yield os.path.join(root, path), ext


def fake_paths_exts(*args, **kwargs):
    return [pe for pe in xfake_paths_exts(*args, **kwargs)]
