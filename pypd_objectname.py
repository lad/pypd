from itertools import izip_longest
import os

class ObjectName(object):

    sep = '/'

    @staticmethod
    def split_valid_name(objname):
        parts = objname.split(ObjectName.sep)
        if len(parts) > 1:
            if not parts[0] or not parts[-1]:
                raise ValueError('Object name "%s" should not start or end '
                                 'with a "%s" character' % \
                                 (objname, ObjectName.sep))
            return parts[:-1], parts[-1]
        else:
            return [], parts[0]

    def set_name(self, objname):
        self._name = objname
        self._path_parts, self._rname = self.split_valid_name(objname)

    # TODO: maybe this should be read-only after all
    name = property(lambda self: self._name, set_name)
    # read-only properties derived from name
    rname = property(lambda self: self._rname)

    def __init__(self, objname):
        # assigning to self.name will derive self._path_parts and self.rname
        self.name = objname

    def __eq__(self, other):
        return id(self) == id(other) or \
               self._name == getattr(other, '_name', str(other)) or \
               (self.rname == getattr(other, 'rname', None) and \
                self.match_path_parts(getattr(other, '_path_parts', [])))

    def match_path(self, mpath):
        if not mpath:
            return not self._path_parts

        if mpath.startswith(os.path.sep):
            mpath = mpath[1:]
        if mpath.endswith(os.path.sep):
            mpath = mpath[:-1]

        return self.match_path_parts(mpath.split(self.sep))

    def match_path_parts(self, mpath_parts):
        for part, mpart in izip_longest(reversed(self._path_parts),
                                        reversed(mpath_parts)):
            if part is None:
                return True
            elif mpart is None:
                return False
            elif part != mpart:
                return False

        # We matched everything
        return True

    def __hash__(self):
        return hash(self.rname)

    def __str__(self):
        return self._name
