import pytest
import _pytest
import pypd
import testutils
import unitutils


@testutils.parametrize(['no-match', 'no-paths', 'one-path', 'multi-paths'])
def pytest_funcarg__site_get_args(request):
    tmpdir = str(_pytest.tmpdir.pytest_funcarg__tmpdir(request))
    patch = unitutils.FakePatch(testutils.fake_names(1)[0])


def test_site_get(site_get_args):
    pass
