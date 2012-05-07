from itertools import izip_longest
import pytest
import _pytest
import pypd_parser
# should we fake the exception classes too?
from pypd_exceptions import *
import testutils
from fakes import FakeObject, FakeTree


@testutils.parametrize(['canvas_only', 'one_level', 'two_levels',
                        'canvas_only.structs', 'one_level.structs'])
def pytest_funcarg__parse_lines_args(request):

    args = {'canvas_only':          ['canvas;'],
            'canvas_only.structs':  ['struct;', 'struct;', 'struct;',
                                     'canvas;'],
            'one_level':            ['canvas;', 'obj1;', 'obj2;'],
            'one_level.structs':    ['struct;', 'canvas;', 'obj1;', 'obj2;'],
            'two_levels':           ['canvas;', 'obj1.1;',
                                     'canvas;', 'obj2.1;', 'restore;',
                                     'obj1.2;'],
            'two_levels.structs':   ['struct;', 'struct;',
                                     'canvas;', 'obj1.1;',
                                     'canvas;', 'obj2.1;', 'restore;',
                                     'obj1.2;']}
    # chops off the linesep
    _s = lambda s: s[:-1]

    lines = args[request.param]
    tree = FakeTree(FakeObject('canvas'))
    structs = []

    if request.param == 'canvas_only.structs':
        structs = [FakeObject(_s(lines[i])) for i in (0, 1, 2)]
    elif request.param == 'one_level':
        tree.add(FakeObject(_s(lines[1])))
        tree.add(FakeObject(_s(lines[2])))
    if request.param == 'one_level.structs':
        tree.add(FakeObject(_s(lines[2])))
        tree.add(FakeObject(_s(lines[3])))
        structs = [FakeObject(_s(lines[0]))]
    elif request.param == 'two_levels':
        tree.add(FakeObject(_s(lines[1])))
        b = tree.add(FakeObject(_s(lines[2])))
        b.add(FakeObject(_s(lines[3])))
        b.add(FakeObject(_s(lines[4])))
        tree.add(FakeObject(_s(lines[5])))
    elif request.param == 'two_levels.structs':
        tree.add(FakeObject(_s(lines[3])))
        b = tree.add(FakeObject(_s(lines[4])))
        b.add(FakeObject(_s(lines[5])))
        b.add(FakeObject(_s(lines[6])))
        tree.add(FakeObject(_s(lines[7])))
        structs = [FakeObject(_s(lines[i])) for i in (0, 1)]

    return lines, structs, tree


def test_parser_parse_lines(monkeypatch, parse_lines_args):
    lines, exp_structs, exp_tree = parse_lines_args

    monkeypatch.setattr(pypd_parser, 'Object', FakeObject)
    monkeypatch.setattr(pypd_parser, 'Tree', FakeTree)

    tree, structs = pypd_parser.parse_lines(lines)

    for struct, exp_struct in izip_longest(structs, exp_structs):
        assert struct == exp_struct

    for (child, depth), (exp_child, exp_depth) in izip_longest(tree, exp_tree):
        assert depth == exp_depth
        assert child.value == exp_child.value


def test_parser_invalid_start_line(monkeypatch):
    monkeypatch.setattr(pypd_parser, 'Object', FakeObject)
    monkeypatch.setattr(pypd_parser, 'Tree', FakeTree)

    with pytest.raises(InvalidLine):
        pypd_parser.parse_lines(['line1;'])


def test_parser_no_canvas(monkeypatch):
    monkeypatch.setattr(pypd_parser, 'Object', FakeObject)
    monkeypatch.setattr(pypd_parser, 'Tree', FakeTree)

    with pytest.raises(InvalidPatch):
        pypd_parser.parse_lines(['struct;'])
