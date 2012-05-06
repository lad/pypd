#!/usr/bin/env python

from itertools import izip_longest

# TODO
#
# Use weakref for child to parent links. Otherwise we have a circular reference
# which will cause Python to use Garbage Collection, rather than ref-counting
# which is much slower.


class Tree(object):

    """A tree abstraction oriented towards storing PD patch data.

    This class dispenses with the notion of separate tree and node classes and
    uses a single class for both. All nodes in the tree are instances of
    Tree."""

    def __init__(self, value=None, parent=None):
        (self.parent, self.value, self._children) = (parent, value, [])

    def __len__(self):
        return len(self._children)

    def __getitem__(self, i):
        """Return the requested *immediate child* or slice."""
        if isinstance(i, slice):
            indices = i.indices(len(self._children))
            return [self._children[i] for i in range(*indices)]
        else:
            return self._children[i]

    def add(self, value):
        """Add the given value as a child of this node."""
        tree = Tree(value, parent=self)
        self._children.append(tree)
        return tree

    def addChildren(self, children):
        """Add a list of children to this node."""
        child_nodes = [Tree(c, parent=self) for c in children]
        self._children.extend(child_nodes)
        return child_nodes

    def addBranch(self, tree):
        """Add the given tree as a child of this node."""
        tree.parent = self
        self._children.append(tree)

    def leaf(self):
        """Return true if this node is a leaf node."""
        return self._children == []

    def __iter__(self):
        """Iteration is depth first as this is the only order that makes sense
        for a Pd patch. Each object is yielded in the order it appears in
        the original patch.  Each value yielded by the iterator is a tuple
        of the node value, and an integer indicating its depth in the tree."""

        # Yield the root
        yield (self, 0)

        # Use a stack instead of recursion. Each tuple in the stack is a node
        # and its level in the tree.
        child_stack = [(c, 1)  for c in reversed(self._children)]
        while True:
            try:
                (child, depth) = child_stack.pop()
            except IndexError:
                # stack is empty, we're done...
                raise StopIteration()

            # Yield each node
            yield (child, depth)

            if child._children:
                child_stack.extend([(c, depth + 1) for c in \
                                    reversed(child._children)])

    def __eq__(self, other):
        return id(self) == id(other) or self._eq_tree(other)

    def _eq_tree(self, other):
        try:
            for (node1, depth1), (node2, depth2) in izip_longest(self, other):
                if None in (node1, depth1, node2, depth2):
                    return False
                if len(node1._children) != len(node2._children):
                    return False
                if depth1 != depth2 or node1.value != node2.value:
                    return False
            return True
        except (TypeError, ValueError):
            # Other is not a Tree
            return False

    def __ne__(self, other):
        return not self == other

    def apply(self, fn):
        """Apply the given function to every node in the list.

        Iteration is depth first, each value being visited in the order it
        appears in the patch file."""
        for (node, depth) in self:
            fn(node, depth)
