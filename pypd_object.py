import pypd_element

class Object(object):

    # Some constants we need to recognize in the patch file
    NCHUNK = '#N'
    CCHUNK = '#C'
    ACHUNK = '#A'
    XCHUNK = '#X'
    CANVAS = 'canvas'       # Since there are two different canvas definitions
    CANVAS5 = 'canvas5'     # we need to distinguish them. CANVAS5/CANVAS6 are
    CANVAS6 = 'canvas6'     # internal names only, never exposed.
    RESTORE = 'restore'
    CONNECT = 'connect'
    STRUCT = 'struct'
    OBJ = 'obj'
    ARRAY_DATA = 'array-data'

    """Abstraction for all Pure Data object types."""

    chunk = None
    element = None
    attr_names = []
    attrs = []
    extra_params = []
    vanilla = False
    include = []

    def __init__(self, text, includes=None):
        params = text.split(' ')

        self.chunk, self.element, params = self._parse_chunk(params)

        (self.attr_names, self.attrs, self.extra_params, self.vanilla) = \
                                    pypd_element.get(self.element, params)

        if self.vanilla:
            self.include = []
        else:
            typ = self.attrs.get('type')
            if typ and includes:
                self.include = includes.get(typ)
            else:
                self.include = []

    @staticmethod
    def _parse_chunk(params):
        try:
            chunk = params[0]
            params = params[1:]

            # "#N canvas" or "#N struct"
            if chunk == Object.NCHUNK:
                element = params[0]
                params = params[1:]
            # "#C restore"
            elif chunk == Object.CCHUNK:
                element = params[0]
                params = params[1:]
                if element != Object.RESTORE:
                    raise ValueError('Invalid chunk element combination: ' \
                                     '"%s %s"' % (chunk, element))
            # "#A array-data"
            elif chunk == Object.ACHUNK:
                # Array data definitions don't have an element name, so we
                # use this as a placeholder
                element = Object.ARRAY_DATA
            # "#X ..."
            elif chunk == Object.XCHUNK:
                # every other object
                element = params[0]
                params = params[1:]
            else:
                raise ValueError('Unrecognized chunk type: "%s"' % self.chunk)
        except IndexError:
            raise ValueError('Too few values to parse in "%s"' % text)

        return chunk, element, params

    def known(self):
        return self.vanilla or bool(self.include)

    def __getitem__(self, attr_name):
        """Access Pd attributes by name. Raises exception if not found."""
        if attr_name == 'element':
            return self.element
        elif attr_name == 'chunk':
            return self.chunk
        elif attr_name == 'vanilla':
            return self.vanilla
        elif attr_name == 'known':
            return self.known()
        else:
            return self.attrs[attr_name]

    def __setitem__(self, attr_name, attr_value):
        """First draft of a simple setitem.

        We may need a lot of contraints here to prevent the patch becoming
        invalid.

        May also allow the constaints to be relaxed, perhaps in a
        transaction for bundling up a bunch of changes that would
        otherwise result in an invalid patch during the intermediate
        changes, but would be valid once all changes are complete."""

        if attr_name == 'element':
            self.element = attr_value
        elif attr_name == 'chunk':
            self.chunk = attr_value
        elif attr_name == 'vanilla':
            raise AttributeError('Cannot set Object.vanilla. It is a ' \
                                 'read-only value')
        else:
            self.attrs[attr_name] = attr_value
        return self

    def get(self, attr_name):
        """Access Pd attributes by name. Returns None if not found."""
        if attr_name == 'element':
            return self.element
        elif attr_name == 'chunk':
            return self.chunk
        elif attr_name == 'vanilla':
            return self.vanilla
        elif attr_name == 'known':
            return self.known()
        else:
            return self.attrs.get(attr_name)

    def __str__(self):
        """Return a representation suitable for storing in a Pd patch file."""

        vals = [self.attrs[k] for k in self.attr_names \
                              if self.attrs[k] is not None]
        if self.extra_params:
            vals += self.extra_params

        # Special case for canvas and array-data
        if self.chunk == self.ACHUNK:
            return ' '.join([self.chunk] + vals)
        else:
            return ' '.join([self.chunk, self.element] + vals)

    def name(self):
        """Return the element name or object name if the element is an 'obj'"""

        if self.element == self.OBJ:
            return self.attrs.get('type') or self.element
        elif self.element == self.CANVAS:
            return 'canvas %s' % self.get('name')
        elif self.element == self.RESTORE:
            # There are a few different possible restore formats.
            #     restore pd name;
            #     restore pd;
            #     restore graph;
            #     restore;
            name = self.get('name')
            if name == 'pd':
                if len(self.extra_params):
                    val = '%s %s' % (self.RESTORE, str(self.extra_params[0]))
                else:
                    val = '%s (subpatch)' % self.RESTORE
            elif name == 'graph':
                val = '%s (graph-on-parent subpatch)' % self.RESTORE
            elif name:
                val = '%s %s' % (self.RESTORE, name)
            else:
                val = self.RESTORE

            return val
        else:
            return self.element
