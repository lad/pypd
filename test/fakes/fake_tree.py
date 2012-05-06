class FakeTree(object):
    def __init__(self, value, parent=None):
        self.value = value
        self.children = []
        self.parent = parent

    def add(self, value):
        tree = FakeTree(value, parent=self)
        self.children.append(tree)
        return tree

    def addChildren(self, children):
        nodes = [FakeTree(c, parent=self) for c in children]
        self.children.extend(nodes)
        return nodes

    def addBranch(self, tree):
        tree.parent = self
        self.children.append(tree)

    def __iter__(self):
        yield (self, 0)
        child_stack = [(c, 1)  for c in reversed(self.children)]
        while True:
            try:
                (child, depth) = child_stack.pop()
            except IndexError:
                raise StopIteration()

            # Yield each node
            yield (child, depth)
            if child.children:
                child_stack.extend([(c, depth + 1) for c in \
                                    reversed(child.children)])
