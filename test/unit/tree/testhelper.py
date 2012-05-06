from pypd import Tree


def make_tree(num_children, max_depth, rootval=None, extra_at_depth=None):
    """Create a SimpleTree with the given number of children at each depth.

    The internal _children attribute is created assembled here rather than
    relying on the correctness of the add() method."""

    node_num, depth = 0, 0
    if not rootval:
        rootval = '%d-%d' % (node_num, depth)
    tree = Tree(rootval)

    # Add request number of nodes at each depth
    this_level_nodes = [tree]
    for depth in range(1, max_depth):
        next_level_nodes = []
        for node in this_level_nodes:
            if extra_at_depth == depth:
                node._children = [Tree('%d-%d' % (node_num, node_num))]
            else:
                node._children = []

            for i in range(num_children):
                node._children.append(
                        Tree('%d-%d' % (node_num, node_num), node))
                node_num += 1
            next_level_nodes.extend(node._children)
        this_level_nodes = next_level_nodes

    return tree


def make_order(tree):
    """Return tuple (tree, depth-first-traversal-order).

    The second part of the tuple is a list of tuples (node.value, depth) in
    the order that a depth first traversal would yield."""

    def df(node, depth, order):
        order.append((node.value, depth))
        for child in node._children:
            df(child, depth + 1, order)

    order = []
    df(tree, 0, order)
    return tree, order
