import os
import pytest
import _pytest
import pypd.pypd_known_reader
import testutils


def pytest_funcarg__known_parse_args(request):
    lines = """
        [elements]
        key1   val1-1, val1-2, val1-3
        # comment - this should get removed
        key2     v2,          v21,   v22, v23, v24, \\
        v25

        key3

        # another comment
        [objects]
        clip~          \\
                lower, \\
                upper
        closebang"""

    elem_kvs = {'key1': ['val1-1', 'val1-2', 'val1-3'],
                'key2': ['v2', 'v21', 'v22', 'v23', 'v24', 'v25'],
                'key3': []}

    obj_kvs = {'clip~': ['lower', 'upper'],
              'closebang': []}

    expected = {'elements': elem_kvs,
                'objects':  obj_kvs}

    tmpdir = _pytest.tmpdir.pytest_funcarg__tmpdir(request)
    path = os.path.join(str(tmpdir), 'test_known_reader.txt')
    with open(path, 'w') as f:
        f.writelines(lines)

    return path, expected


def test_parse(known_parse_args):
    path, expected = known_parse_args
    results = pypd.pypd_known_reader.read(path)

    for section, keyvals in expected.items():
        assert results and results[section] == keyvals
