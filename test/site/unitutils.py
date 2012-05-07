import testutils
from collections import defaultdict


class FakePatch(object):
    instances = defaultdict(list)

    @staticmethod
    def clear():
        FakePatch.instances = defaultdict(list)

    def __init__(self, name):
        self.name = name
        self.paths, self.exts = [], []
        # Save every instance created in a dictionary class variable keyed
        # by the function name that created this instance.
        self.instances[testutils.funcname(up=1)].append(self)

    def add(self, path_ext):
        self.paths.append(path_ext[0])
        self.exts.append(path_ext[1])

    def __eq__(self, other):
        return id(self) == id(other) or \
               self.name == getattr(other, 'name', str(other))

    def __hash__(self):
        return hash(self.name)
