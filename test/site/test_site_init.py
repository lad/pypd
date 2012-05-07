import pytest
import _pytest
import os
import pypd
import testutils


@testutils.parametrize(['none', 'one', 'multi'])
def pytest_funcarg__init_dirs_args(request):
    tmpdir = str(_pytest.tmpdir.pytest_funcarg__tmpdir(request))

    if request.param == 'none':
        dirs = expected = []
    if request.param == 'one':
        dirs = [os.path.join(tmpdir, 'lib', 'pd-extended', 'extra')]
        expected = [os.path.normpath(d) for d in dirs]
    elif request.param == 'multi':
        parts_list = [['lib', 'pd-extended', 'extra'],
                      ['user', 'mypatches/'],
                      ['usr', 'local', 'pd', 'patches']]
        dirs = [os.path.join(tmpdir, *parts) for parts in parts_list]
        expected = [os.path.normpath(d) for d in dirs]

    testutils.make_dirs(dirs)
    return dirs, expected


def test_init_dirs_attr(init_dirs_args):
    dirs, expected = init_dirs_args
    assert pypd.Site(dirs).dirs == expected


@pytest.mark.parametrize('tf', [True, False])
def test_init_populated_attr(tf):
    site = pypd.Site(['.'], populate=tf)
    assert (tf and site.populated) or (not tf and not site.populated)


@testutils.parametrize(['none_populate', 'none_not_populate',
                        'one_populate', 'one_not_populate',
                        'multi_populate', 'multi_not_populate'])
def pytest_funcarg__patches_args(request):
    tmpdir = str(_pytest.tmpdir.pytest_funcarg__tmpdir(request))

    if request.param == 'none_populate':
        dirs, populate, expected = [tmpdir], True, False
    elif request.param == 'none_not_populate':
        dirs, populate, expected = [tmpdir], False, False
    elif request.param == 'one_populate':
        testutils.make_fake_files(tmpdir, 1, ['.pd'])
        dirs, populate, expected = [tmpdir], True, True
    elif request.param == 'one_not_populate':
        testutils.make_fake_files(tmpdir, 1, ['.pd'])
        dirs, populate, expected = [tmpdir], False, False
    elif request.param == 'multi_populate':
        testutils.make_fake_files(tmpdir, 10, ['.pd'])
        dirs, populate, expected = [tmpdir], True, True
    elif request.param == 'multi_not_populate':
        testutils.make_fake_files(tmpdir, 10, ['.pd'])
        dirs, populate, expected = [tmpdir], False, False
    else:
        raise ValueError('Unknown request parameter "%s"' % request.param)

    return dirs, populate, expected


def test_init_patches_attr(patches_args):
    dirs, populate, expected = patches_args
    site = pypd.Site(dirs, populate=populate)
    assert (expected and site._patches) or \
           (not expected and not site._patches)
