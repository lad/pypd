#!/usr/bin/env python

import os
import sys
import collections
import config
from patch import Patch
from ext import Ext


class Site(object):

    """Abstraction for searching the available Pure Data patches.

    Given a list of directories a mapping is generated between the
    Pure Data patch name (its object name) and its location on disk.
    Since the same patch name may appear in multiple directories, the
    mapping maintains a list of directories for each patch name.

    To access the patch names a simple object name like "abs~" can be used:

        >>> site = Site(['/usr/lib/pd-extended/extra'])
        >>> print site['abs~']
        set(['/usr/lib/pd-extended/extra/markex', '/usr/lib/pd-extended/
        extra/vanilla', '/usr/lib/pd-extended/extra/zexy', '/usr/lib/
        pd-extended/extra/creb', '/usr/lib/pd-extended/extra/cyclone'])

    To access a patch in a specific library a path and path name can
    be used:

        >>> site = Site(['/usr/lib/pd-extended/extra'])
        >>> print includes['cyclone/abs~']
        ['/usr/lib/pd-extended/extra/cyclone']

    Only the rightmost part of the path and name need to match enough to
    uniquely identify a patch on disk.

    Note that the object names are not paths, they are always separated by
    a '/' character regardless of platform, and they cannot start with
    a leading '/'.
    """

    def __init__(self, dirs, populate=True):
        """Construct a Site object to track available patches.

        The given iterable of directories is traversed and a mapping of
        patch names to their location on disk is generated."""

        self.dirs = [os.path.normpath(d) for d in dirs]
        self._patches = {}
        self.populated = False

        if populate:
            self.populate()

    def populate(self):
        if self.populated:
            return

        for d in self.dirs:
            for path, name, ext in self._find_files(d):
                p = self._patches.get(name)
                if not p:
                    p = Patch(name)
                    self._patches[p] = p
                p.add((path, ext))

        self.populated = True

    def get(self, name):
        """Return the list of directories where the given name can be found."""
        patch = self._patches.get(name)
        if patch:
            return [p.path for p in patch.paths]
        else:
            return []

    def __iter__(self):
        """Iterate over the known object names."""
        for patch in self._patches:
            yield patch.name

    def __items__(self):
        """Iterate over all known patches.

        Each value yielded is: (object-name, path, ext)"""

        for patch in self._patches:
            for val in patch:
                return val

    def __nonzero__(self):
        """Return True if any objects where found on disk."""
        return bool(self._patches)

    def __contains__(self, name):
        """Check whether the given name is known."""
        return name in self._patches

    def __getitem__(self, name):
        """Return list of directories where the given patch can be found."""
        val = self.get(name)
        if not val:
            raise KeyError('%s' % str(name))
        return val

    @staticmethod
    def _find_files(root_dir, exts=Ext.valid):
        for path, dirs, files in os.walk(os.path.normpath(root_dir)):
            for f in files:
                (name, ext) = os.path.splitext(f)
                # check it has an extension we want
                if ext in exts:
                    yield path, name, ext
