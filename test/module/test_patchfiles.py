from pypd import PatchFiles
import pytest
import testutils


@testutils.parametrize(['no_path', 'one_path', 'two_path', 'three_path'])
def pytest_funcarg__patchfiles_get_args(request):
    paths = ['abs.pd',
             '/b/c/abs.pd',
             '/a/b/c/abs.pd',
             '/a/x/c/abs.pd',
             '/a/b/c/notabs.pd']
    args = {'no_path':    ('abs', paths, [0, 1, 2, 3]),
            'one_path':   ('c/abs', paths, [1, 2, 3]),
            'two_path':   ('b/c/abs', paths, [1, 2]),
            'three_path': ('a/b/c/abs', paths, [2])}
    return args[request.param]


@testutils.parametrize(['single', 'multi'])
def pytest_funcarg__patchfiles_add_args(request):
    paths = ['abs.pd',
             '/a/b/c/abs.pd',
             '/a/b/svf~.pd_linux']
    args = {'single':   ('svf~', paths, [paths[2]]),
            'multi':    ('abs',  paths, paths[:2])}
    return args[request.param]


def test_patchfiles_add(patchfiles_add_args):
    object_name, paths, matches = patchfiles_add_args
    pfiles = PatchFiles()
    for path in paths:
        pfiles.add(path)
    assert pfiles._files[object_name] == matches


def test_patchfiles_get(patchfiles_get_args):
    object_name, paths, matches = patchfiles_get_args
    pfiles = PatchFiles()
    for path in paths:
        pfiles.add(path)

    results = pfiles.get(object_name)
    for i in matches:
        results.remove(paths[i])

    assert results == []
