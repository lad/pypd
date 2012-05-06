import os
import pytest
import _pytest
import pypd
import testutils


CFG_TEXT = """[install]
include_1 = /usr/lib/pd-extended/extra
"""


@testutils.parametrize(['not_exists', 'exists'])
def pytest_funcarg__filename(request):
    if request.param == 'exists':
        tmpdir = _pytest.tmpdir.pytest_funcarg__tmpdir(request)
        filename = os.path.join(str(tmpdir), 'test_init_pdconfig.cfg')
        with open(filename, 'w') as f:
            # TODO encoding
            f.write(CFG_TEXT)
    else:
        filename = pytest_funcarg__not_exists_filename(request)

    return filename


def pytest_funcarg__not_exists_filename(request):
    tmpdir = _pytest.tmpdir.pytest_funcarg__tmpdir(request)
    return os.path.join(str(tmpdir), 'init_filename.cfg')


@testutils.parametrize(['not_exists', 'exists'])
def pytest_funcarg__filename_with_flag(request):
    return pytest_funcarg__filename(request), request.param == 'exists'


@testutils.parametrize([True, False])
def pytest_funcarg__flush_tf(request):
    return request.param


def test_init_filename(filename):
    cfg = pypd.Config(filename)
    assert cfg.filename == filename


def test_init_flush_attr(filename, flush_tf):
    cfg = pypd.Config(filename, flush=flush_tf)
    assert cfg.flush == flush_tf


def test_init_flush_file(not_exists_filename, flush_tf):
    cfg = pypd.Config(not_exists_filename, flush=flush_tf)
    if flush_tf:
        assert os.path.isfile(not_exists_filename)
    else:
        assert not os.path.isfile(not_exists_filename)


def test__config(filename):
    config = pypd.Config(filename)
    assert config._config


def test__items(filename_with_flag):
    filename, exists = filename_with_flag
    cfg = pypd.Config(filename)
    if exists:
        assert cfg._items
    else:
        assert not cfg._items
