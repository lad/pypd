import testhelper
import testutils


@testutils.parametrize(['root', 'depth1', 'depth2'])
def pytest_funcarg__iter_args(request):
    """Generate different test arguments for iteration tests."""

    if request.param == 'root':
        tree_order = testhelper.make_order(testhelper.make_tree(0, 0))
    elif request.param == 'depth1':
        tree_order = testhelper.make_order(testhelper.make_tree(3, 1))
    elif request.param == 'depth2':
        tree_order = testhelper.make_order(testhelper.make_tree(2, 2))

    return tree_order


def test_iter(iter_args):
    tree, expected_order = iter_args
    assert [(n.value, d) for n, d in tree] == expected_order
