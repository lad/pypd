from pypd import Tree
import testutils


@testutils.parametrize(['none', 'value'])
def pytest_funcarg__init_parent_args(request):
    if request.param == 'none':
        tree, parent = Tree(0), None
    elif request.param == 'value':
        parent = Tree(0)
        tree = Tree(1, parent)

    return tree, parent


@testutils.parametrize(['int-value', 'string-value'])
def pytest_funcarg__init_value_args(request):
    if request.param == 'int-value':
        tree, value = Tree(99), 99
    elif request.param == 'string-value':
        tree, value = Tree('str'), 'str'

    return tree, value


def test_init_parent(init_parent_args):
    tree, parent = init_parent_args
    assert tree.parent == parent


def test_init_value(init_value_args):
    tree, value = init_value_args
    assert tree.value == value
