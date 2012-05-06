class FakeObject(object):
    CANVAS = 'canvas'
    RESTORE = 'restore'
    STRUCT = 'struct'
    RESTORE_NAME = 'restore-name'

    def __init__(self, text, includes=[]):
        self.text = self.element = self._name = text
        if self.element == self.RESTORE:
            self._name = self.RESTORE_NAME
        self.includes = includes

    def name(self):
        return self._name

    def __eq__(self, other):
        return id(self) == id(other) or vars(self) == vars(other)

    def __str__(self):
        return str(vars(self))
