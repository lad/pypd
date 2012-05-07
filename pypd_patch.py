import collections
from pypd_object import Object
import pypd_parser

class Patch(object):
    LINE_ENDING = ';\r\n'

    """This is a container type abstraction for a Pure Data patch or sub-patch.

       These are represented by the Pd "canvas" type. All patch files start
       with a top-level canvas declaration, and may contain further canvas
       declarations to indicate sub-patches.

       Objects are accessed via their object-ids, which can change if objects
       are inserted or deleted. This is an unfortunate side-effect of the
       Pd patch file format. An additional problem is that object-ids are
       only unique within their own patch or sub-patch. Since all sub-patches
       restart object-ids at zero, there will be many objects with the same
       Pd object-id.

       An easier way to access specific objects is use the select() method
       specifying the attributes of the objects to match. Alternatively the
       filter built-in can be used with any callable to select objects.  See
       example in the documentation for the select() method."""

    def __init__(self, path, includes=[]):
        """Create a Patch object from the given textual description."""
        self.path = path
        self.includes = includes
        self.tree, self.structs = pypd_parser.parse(path, includes)

    def __len__(self):
        return len(self.tree)

    def __getitem__(self, key):
        """Access object by object-id.

        Objects within a patch are accessed using their object IDs.  IDs
        start at zero for the first object in the patch, excluding the
        starting canvas definition.

        The first object in a sub-patch starts at ID zero again. The IDs in
        the parent patch take up where they left off when the sub-patch
        returns to its parent.

        To locate an object in a sub-patch you must first locate the
        canvas object for that sub-patch. See select() for an easier way to
        access objects.

        Slices are not supported, since in Pure Data terms a part of a
        patch would not be a valid patch. It would not start with a canvas
        definition and would not have correctly numbered object IDs. The
        exception would be a slice starting at the beginning of the patch,
        but this is not a common or useful way of accessing parts of a Pd
        patch."""

        if isinstance(key, slice):
            raise NotImplementedError('Patch does not support slices')
        return self.tree[key]

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            raise NotImplementedError('Patch does not support slices')
        else:
            self.tree[key] = value

    def __delitem__(self, key):
        raise NotImplementedError('delitem not implemented yet')

    def __reversed__(self):
        """There's no point in reversing a patch."""

        raise NotImplementedError('Patch does not support reversed()')

    def __contains__(self, obj):
        for (node, obj_id, level) in self.tree:
            if node.value == obj:
                return True
        return False

    def __str__(self):
        return self.LINE_ENDING.join(str(node.value) for node in self)

    def __iter__(self):
        # The object ids must be generated dynamically, as they change when
        # the tree is modified. The root node (a canvas object) and connect
        # object are given the id of -1 as they don't actually have ids in Pd
        # patches.
        obj_id = -1

        it = iter(self.tree)
        (node, level) = it.next()
        yield (node, obj_id, level)

        # Need to keep track of the object id as we move up and down levels
        # in the tree
        obj_id_stack = collections.deque()
        last_level = 1

        for (node, level) in it:
            if node.value.element == Object.CONNECT:
                # Connect objects have no valid id
                yield (node, -1, level)
            else:
                # Work out the object-id
                if level == last_level:
                    obj_id += 1
                elif level == (last_level - 1):
                    # returning from sub-patch
                    obj_id = obj_id_stack.pop() + 1
                else:
                    # entering sub-patch
                    obj_id_stack.append(obj_id)
                    obj_id = 0

                last_level = level
                yield (node, obj_id, level)

    def apply(self, fn):
        return self.tree.apply(fn)

    def add(self, key, value):
        raise NotImplementedError('add() Not implemented yet')

    def insert(self, i, key, value):
        raise NotImplementedError('insert() Not implemented yet')

    def select(self, **kwargs):
        selected = []
        for (node, obj_id, level) in iter(self):
            if all([node.value.get(k) == v for k, v in kwargs.iteritems()]):
                selected.append((node, obj_id, level))

        return selected
