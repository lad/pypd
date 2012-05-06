from pypd import Tree
import testhelper
import testutils


@testutils.parametrize(['root', 'depth1', 'depth2', 'depth3'])
def pytest_funcarg__apply_args(request):
    if request.param == 'root':
        tree, order = Tree(0), [(0, 0)]
    elif request.param == 'depth1':
        tree, order = Tree(0), [(3, 1)]
    elif request.param == 'depth2':
        tree, order = Tree(0), [(3, 2)]
    elif request.param == 'depth3':
        tree, order = Tree(0), [(10, 3)]

    return testhelper.make_order(tree)


def test_apply(apply_args):
    tree, expected_order = apply_args
    actual_order = []

    def fn(node, depth):
        print node.value, depth
        actual_order.append((node.value, depth))

    tree.apply(fn)
    assert actual_order == expected_order
