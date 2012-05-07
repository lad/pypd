import os
import pytest
import _pytest
import pypd
import testutils


@testutils.parametrize(['none', 'one', 'multi', 'with-non-pd'])
def pytest_funcarg__files_args(request):
    if request.param == 'none':
        num_files, exts = 0, ['.pd']
    if request.param == 'one':
        num_files, exts = 1, ['.pd']
    elif request.param == 'multi':
        num_files, exts = 5, ['.pd']
    elif request.param == 'with-non-pd':
        num_files, exts = 10, ['.pd', '.pdf', '.html']

    tmpdir = str(_pytest.tmpdir.pytest_funcarg__tmpdir(request))
    files = testutils.make_fake_files(tmpdir, num_files, exts)
    return tmpdir, files


# Simple values like this could have been done with
# @pytest.mark.parametrize, but the test output is harder to decipher
# on test failure. It's clearer hen the request parameters are strings or
# another more printable type. For example:
#     test_find_files_default[with-non-pd-pd_only] FAILED
# verses:
#     test_find_files_default[with-non-pd-.0] FAILED

@testutils.parametrize(['valid', 'pd_only', 'pdf'])
def pytest_funcarg__exts_args(request):
    if request.param == 'valid':
        return pypd.Ext.valid
    elif request.param == 'pd_only':
        return ['.pd']
    elif request.param == 'pdf':
        return ['.pdf']


def test_find_files_default(files_args, exts_args):
    root_dir, files = files_args
    exts = exts_args
    for path, name, ext in pypd.Site._find_files(root_dir, exts=exts):
        # this confirms the correct file was found
        f = os.path.join(path, name + ext)
        files.remove(f)

    # success is when we have no remaining files or any that do remain
    # must not have one of the known extensions passed in.
    assert not any([os.path.splitext(f)[1] in exts for f in files])
