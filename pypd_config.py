#!/usr/bin/env python

import ConfigParser


class Config(object):

    """Get/Set preference values in a PyPD config file."""

    SECTION = 'install'

    def __init__(self, filename, flush=True):
        """Read and parse a PyPD config file."""
        self.filename = filename
        self._config = None
        self._flush = flush
        self._config = ConfigParser.RawConfigParser()
        self._config.read(self.filename)

        if self._config.has_section(self.SECTION):
            self._items = dict(self._config.items(self.SECTION))
        else:
            self._config.add_section(self.SECTION)
            self._items = {}
            if self._flush:
                self.write()

    def _set_flush(self, newval):
        if newval != self._flush:
            self._flush = newval
            if newval and self._config:
                self.write()

    flush = property(lambda self: self._flush, _set_flush, doc="""\
    When flush is true changes are written to the config file immediately.

    When false the changes can be written with an explicit call to
    write(). When toggled from false to true, any pending changes
    will be written to the config file immediately.""")

    def get(self, key):
        """Return the value for the given key or None if not found.

        Values may be single valued or a list of values depending
        on what was set previously."""
        return self._get(key, doex=False)

    def _get(self, key, doex=False):
        try:
            return self._items[key]
        except KeyError, ex:
            keyex = ex

        val = [self._items[k] for k in self._items.keys() \
               if k.startswith('%s_' % key)]
        if val:
            return val
        elif doex:
            raise keyex
        else:
            return None

    def __getitem__(self, key):
        """Return the value for the given key. Raises KeyError if not found.

        Values may be single valued or a list of values depending
        on what was set previously."""
        return self._get(key, doex=True)

    def __setitem__(self, key, value):
        """Set the given key/value, write out if flush is on.

        Value may be single valued or a list of values."""
        if isinstance(value, basestring):
            self._config.set(self.SECTION, key, value)
            self._items[key] = value
        else:
            # Treat value as a sequence of values, each written with a separate
            # key. This is easier than parsing a config file for lists.
            #   Each key is named "key_i" for i in 1...n where n is the number
            # of values passed in. The integers used may be larger to
            # accomidate existing keys of the same prefix. Each value is
            # saved in a separate key, which removes the need to parse a
            # multi-valued string when reading them back in.

            # Find the number of existing keys that start with the given key
            n = sum([k.startswith('%s_' % key) \
                    for k in self._items.keys()]) + 1

            for i, v in enumerate(value):
                k = '%s_%d' % (key, i + n)
                self._config.set(self.SECTION, k, v)
                self._items[k] = v

        if self._flush:
            self.write()

    def _delete(self, key, doex=False):
        # We may have a single key, or multiple keys of the form key_%d
        try:
            del self._items[key]
            self._config.remove_option(self.SECTION, key)
            keyex = None
        except KeyError, ex:
            keyex = ex

        def rm(k):
            if k.startswith('%s_' % key):
                del self._items[k]
                self._config.remove_option(self.SECTION, k)
                return True
            else:
                return False

        changed = any(map(rm, self._items.keys()))
        if keyex and not changed:
            # No single or multiple keys found
            if doex:
                raise keyex
            else:
                return False

        if self._flush:
            self.write()
        return True

    def __delitem__(self, key):
        """Remove a key from the config file. Raises KeyError if not found."""
        self._delete(key, doex=True)

    def delete(self, key):
        """Remove key from config file. Return T/F for found/not found."""
        return self._delete(key, doex=False)

    def write(self):
        """Write the config data out to the config file."""
        fd = None
        try:
            fd = open(self.filename, 'w')
            self._config.write(fd)
        finally:
            if fd:
                fd.close()
