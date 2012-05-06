import testhelper
import testutils


@testutils.parametrize(['one', 'multi'])
def pytest_funcarg__getitem_args(request):
    if request.param == 'one':
        tree = testhelper.make_tree(1, 1)
    elif request.param == 'multi':
        tree = testhelper.make_tree(5, 1)
    return tree, tree._children


def test_getitem(getitem_args):
    tree, children = getitem_args

    for i, child in enumerate(children):
        assert tree[i] == child
