from pypd import ObjectName
import pytest
import testutils


@testutils.parametrize(['no_path', 'one_path', 'multi_path'])
def pytest_funcarg__object_name(request):
    args = {'no_path':    'abs',
            'one_path':   'cyclone/abs',
            'multi_path': 'lib/dir1/dir2/name'}
    return args[request.param]


@testutils.parametrize(['no_path', 'one_path', 'multi_path'])
def pytest_funcarg__set_name_args(request):
    args = {'no_path':    ('abs', 'abs'),
            'one_path':   ('cyclone/abs', 'abs'),
            'multi_path': ('dir1/dir2/name', 'name')}
    return args[request.param]


@testutils.parametrize(['no_path', 'one_path', 'multi_path'])
def pytest_funcarg__match_rpath_args(request):
    args = {'no_path':    ('abs', '/usr/lib/'),
            'one_path':   ('cyclone/abs', '/usr/lib/cyclone/'),
            'multi_path': ('dir1/dir2/name', '/usr/local/lib/dir1/dir2')}
    return args[request.param]


@testutils.parametrize(['one_path', 'multi_path'])
def pytest_funcarg__object_name_with_path(request):
    args = {'one_path':   'cyclone/abs',
            'multi_path': 'lib/dir1/dir2/name'}
    return args[request.param]


@testutils.parametrize(['no_path', 'one_path', 'multi_path'])
def pytest_funcarg__object_name_rname(request):
    args = {'no_path':    ('abs', 'abs'),
            'one_path':   ('cyclone/abs', 'abs'),
            'multi_path': ('lib/dir1/dir2/name', 'name')}
    return args[request.param]


def test_name_init(object_name):
    assert ObjectName(object_name)._name == object_name


@pytest.mark.parametrize('bad_name', ['/a/b', 'a/b/', '/a/b/'])
def test_name_bad_init_name(bad_name):
    with pytest.raises(ValueError):
        ObjectName(bad_name)


def test_name_init_none():
    with pytest.raises(AttributeError):
        ObjectName(None)


def test_name_str(object_name):
    assert str(ObjectName(object_name)) == object_name


def test_name_not_str(object_name):
    assert str(ObjectName(object_name)) != object_name + 'xx'


def test_name_init_name_attr(object_name):
    assert ObjectName(object_name).name == object_name


def test_name_set_name_attr(set_name_args):
    object_name, rname = set_name_args
    pdname = ObjectName('dummy')
    pdname.name = object_name
    assert pdname.rname == rname


def test_name_init_rname_attr(object_name_rname):
    full_name, rname = object_name_rname
    assert ObjectName(full_name).rname == rname


def test_name_rname_read_only():
    with pytest.raises(AttributeError):
        ObjectName('name').rname = 'xx'


def test_name_self_eq(object_name):
    pdname = ObjectName(object_name)
    assert pdname == pdname


def test_name_str_eq(object_name):
    pdname = ObjectName(object_name)
    assert pdname == object_name


def test_name_str_neq(object_name):
    pdname = ObjectName(object_name)
    assert pdname != object_name + 'xx'


def test_name_instance_neq(object_name):
    pdname1 = ObjectName(object_name)
    pdname2 = ObjectName(object_name)
    assert pdname1 == pdname2


def test_match_rpath(match_rpath_args):
    object_name, path = match_rpath_args
    pdname = ObjectName(object_name)
    assert pdname.match_path(path)
