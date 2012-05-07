import os
import pytest
import _pytest
import pypd_parser
import testutils


@testutils.parametrize(['unix', 'dos'])
def pytest_funcarg__readlines_args(request):
    os_line_seps = {'unix':  '\n',
                    'dos':   '\r\n'}
    os_line_sep = os_line_seps[request.param]
    # all lines returned by pypd_parser.readlines() should end in \n
    expected_line_sep = '\n'

    lines = ['  ', 'some line     ', '     ',
             '  another   line    ', '', '   ', '', '', ' ']

    tmpdir = _pytest.tmpdir.pytest_funcarg__tmpdir(request)
    path = os.path.join(str(tmpdir), 'test_readlines.txt')
    with open(path, 'wb') as f:
        f.writelines(['%s%s' % (line, os_line_sep) for line in lines])

    return path, ['%s%s' % (line, expected_line_sep) for line in lines]


def test_readlines(readlines_args):
    path, expected = readlines_args
    lines = pypd_parser.readlines(path)
    assert lines == expected
