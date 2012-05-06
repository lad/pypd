from pypd import Tree
import pytest
import testhelper
import testutils


@testutils.parametrize(['root', 'depth1', 'depth2', 'depth3'])
def pytest_funcarg__value_equality_args(request):
    if request.param == 'root':
        # test trees with root nodes only
        tree1, tree2 = testhelper.make_tree(0, 0), testhelper.make_tree(0, 0)
    elif request.param == 'depth1':
        # test trees with three nodes 1 level deep
        tree1, tree2 = testhelper.make_tree(3, 1), testhelper.make_tree(3, 1)
    elif request.param == 'depth2':
        # test trees with two nodes two levels
        tree1, tree2 = testhelper.make_tree(2, 2), testhelper.make_tree(2, 2)
    elif request.param == 'depth3':
        # test trees with two nodes three levels
        tree1, tree2 = testhelper.make_tree(2, 3), testhelper.make_tree(2, 3)

    return tree1, tree2


def test_instance_eq():
    tree = Tree(0)
    assert tree == tree


def test_value_equality(value_equality_args):
    tree1, tree2 = value_equality_args
    assert tree1 == tree2


@testutils.parametrize(['root', 'len1', 'values1', 'len2', 'values2'])
def pytest_funcarg__value_inequality_args(request):
    if request.param == 'root':
        # Second tree has a different root value
        tree1, tree2 = testhelper.make_tree(2, 3), \
                       testhelper.make_tree(2, 3, rootval=999)

    # Second tree has an extra child at depth 1
    elif request.param == 'len1':
        tree1, tree2 = testhelper.make_tree(2, 3), \
                       testhelper.make_tree(2, 3, extra_at_depth=1)

    # Second tree has one child at depth 1 with a different value
    elif request.param == 'values1':
        tree1, tree2 = testhelper.make_tree(3, 3), testhelper.make_tree(3, 3)
        tree2._children[1].value = 99

    # Second tree has an extra child at depth 2
    elif request.param == 'len2':
        tree1, tree2 = testhelper.make_tree(3, 3), \
                       testhelper.make_tree(3, 3, extra_at_depth=2)

    # Second tree has one child at depth 2 with a different value
    elif request.param == 'values2':
        tree1, tree2 = testhelper.make_tree(3, 3), testhelper.make_tree(3, 3)
        tree2._children[1]._children[1].value = 99

    return tree1, tree2


@testutils.parametrize(['num', 'text', 'seq'])
def pytest_funcarg__type_neq_arg(request):
    args = dict(num=0, text='asd', seq=['a', 'b'])
    return args[request.param]


def test_type_inequality(type_neq_arg):
    assert Tree(0) != type_neq_arg


def test_value_inequality(value_inequality_args):
    tree1, tree2 = value_inequality_args
    assert tree1 != tree2
