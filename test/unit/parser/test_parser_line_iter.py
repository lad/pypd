from itertools import chain, izip_longest
import pytest
import testutils
from pypd_parser import pd_line_iterator


@testutils.parametrize(['empty', 'one_line', 'multi_line'])
def pytest_funcarg__pd_line_iter_args(request):
    if request.param == 'empty':
        lines = expected = []
    elif request.param == 'one_line':
        lines = ['  one line only    ;\n']
        expected = [(0, 'one line only')]
    else:
        lines = ['first line\n', '   second part of first line;\n',
                'second logical line;\n',
                '\n',
                '   escaped line sep  \\;\n',
                '1st continued escaped line sep  \n',
                '      2nd continued escaped line sep\n',
                '   3rd and last continued escaped line sep  ;\n',
                'last line;\n']
        expected = [(0, 'first line second part of first line'),
                    (2, 'second logical line'),
                    (4, 'escaped line sep  \\; 1st continued escaped line sep '
                        '2nd continued escaped line sep '
                        '3rd and last continued escaped line sep'),
                    (8, 'last line')]
    return lines, expected


def test_parser_pd_line_iter(pd_line_iter_args):
    lines, expected = pd_line_iter_args
    for linetup, exptup in izip_longest(pd_line_iterator(lines), expected):
        assert linetup is not None
        assert exptup is not None
        assert linetup == exptup
