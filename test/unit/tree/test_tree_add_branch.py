from pypd import Tree
import testhelper
import testutils


@testutils.parametrize(['one', 'multi'])
def pytest_funcarg__add_branch_args(request):
    tree = Tree(0)
    if request.param == 'one':
        children_to_add = [testhelper.make_tree(0, 0)]
    elif request.param == 'multi':
        children_to_add = [testhelper.make_tree(2, 2)]
    return tree, tree._children, children_to_add


def test_add_branch(add_branch_args):
    tree, internal_children, children_to_add = add_branch_args

    for child in children_to_add:
        tree.addBranch(child)
        assert child in internal_children
