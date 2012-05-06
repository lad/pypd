from pypd import Tree
import testutils


@testutils.parametrize(['one', 'multi'])
def pytest_funcarg__add_args(request):
    if request.param == 'one':
        tree, values = Tree(0), [1]
    elif request.param == 'multi':
        tree, values = Tree(0), [1, 2, 3, 4, 5]

    tree._children = internal_children = []
    return tree, internal_children, values


def test_add(add_args):
    tree, internal_children, values = add_args

    for value in values:
        tree.add(value)
        assert value in [c.value for c in internal_children]
