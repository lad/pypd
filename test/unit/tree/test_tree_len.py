from pypd import Tree
import testutils


@testutils.parametrize(['init', 'one', 'multi'])
def pytest_funcarg__len_args(request):
    if request.param == 'init':
        tree, expected_len = Tree(0), 0
    elif request.param == 'one':
        tree = Tree(0)
        tree._children = [Tree(1)]
        expected_len = 1
    elif request.param == 'multi':
        tree = Tree(0)
        expected_len = 10
        tree._children = [Tree(n) \
                          for n in range(1, expected_len + 1)]

    return tree, expected_len


def test_len(len_args):
    tree, expected_len = len_args
    assert len(tree) == expected_len
