import os
import shutil
import pypd
import pytest
import _pytest
import testutils
import unitutils


@testutils.parametrize(['no_dupes', 'one_dupe', 'multi_dupes'])
def pytest_funcarg__populate_args(request):
    if request.param == 'no_dupes':
        nfiles, ndupes = 5, 0
    elif request.param == 'one_dupe':
        nfiles, ndupes = 5, 1
    elif request.param == 'multi_dupes':
        nfiles, ndupes = 10, 3
    else:
        raise ValueError('Unknown parameter "%s"' % request.param)

    tmpdir = _pytest.tmpdir.pytest_funcarg__tmpdir(request)
    files = testutils.make_fake_files(str(tmpdir), nfiles, exts=['.pd'],
                                       ndupes=ndupes)

    return [str(tmpdir)], files, True


def test_site_populate(monkeypatch, populate_args):
    unitutils.FakePatch.clear()
    monkeypatch.setattr(pypd.site, 'Patch', unitutils.FakePatch)
    dirs, files, populate = populate_args
    site = pypd.Site(dirs, populate=populate)

    for patch in unitutils.FakePatch.instances['populate']:
        for path, ext in zip(patch.paths, patch.exts):
            f = os.path.join(path, patch.name + ext)
            files.remove(f)

    assert files == []
