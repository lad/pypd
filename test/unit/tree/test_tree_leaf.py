from pypd import Tree
import testhelper
import testutils


@testutils.parametrize(['root', '1_left', '1_right', '2_left', '2_right'])
def pytest_funcarg__leaf_args(request):
    if request.param == 'root':
        leaf = Tree(0)
    elif request.param == '1_left':
        tree = testhelper.make_tree(3, 2)
        leaf = tree._children[0]
    elif request.param == '1_right':
        tree = testhelper.make_tree(3, 2)
        leaf = tree._children[2]
    elif request.param == '2_left':
        tree = testhelper.make_tree(3, 3)
        leaf = tree._children[0]._children[0]
    elif request.param == '2_right':
        tree = testhelper.make_tree(3, 3)
        leaf = tree._children[2]._children[2]
    return leaf


def test_leaf(leaf_args):
    node = leaf_args
    assert node.leaf()


@testutils.parametrize(['root', '1_left', '1_right', '2_left', '2_right'])
def pytest_funcarg__not_leaf_args(request):
    if request.param == 'root':
        not_leaf = testhelper.make_tree(1, 2)
    elif request.param == '1_left':
        not_leaf = testhelper.make_tree(3, 3)._children[0]
    elif request.param == '1_right':
        not_leaf = testhelper.make_tree(3, 3)._children[2]
    elif request.param == '2_left':
        not_leaf = testhelper.make_tree(3, 4)._children[0]._children[0]
    elif request.param == '2_right':
        not_leaf = testhelper.make_tree(3, 4)._children[2]._children[2]
    return not_leaf


def test_not_leaf(not_leaf_args):
    node = not_leaf_args
    assert not node.leaf()
