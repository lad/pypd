from collections import defaultdict
import sys
import os
from pypd_objectname import ObjectName


class PatchFiles(object):
    """A list of patch files on disk with additional access method."""

    win32_exts  = ['.pd', '.dll']
    linux2_exts = ['.pd', '.pd_linux']
    all_exts    = {'win32': win32_exts, 'linux2': linux2_exts,
                   'default': linux2_exts}
    valid_exts = all_exts.get(sys.platform, all_exts['default'])

    def __init__(self):
        # This is keyed by object name (filename, no path, no extension)
        self._files = defaultdict(list)

    def add(self, path):
        name, ext = os.path.splitext(os.path.split(path)[1])
        if ext not in self.valid_exts:
            raise ValueError("%s is not a valid extension" % ext)
        self._files[ObjectName(name)].append(path)

    def get(self, objname):
        """Return matching file paths for the given name.

        The name may be a simple name (e.g. 'abs') or have a partial
        path to the patch file (e.g. 'cyclone/abs~')."""

        pdname = ObjectName(objname)
        return [path for path in self._files[pdname] \
                if pdname.match_path(os.path.split(path)[0])]
