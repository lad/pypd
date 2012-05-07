def make_name_value_dict(attrs, values):
    # Create a map from the attribute names to their values
    kv = dict(izip_longest(attrs, values))
    if kv.has_key(None):
        # If a key is set to None we have more values than attribute names
        del kv[None]
    # Also add arg1 ... argn for each value.
    kv.update([('arg%d' % n, value) for n, value in enumerate(values)])
    return kv


def factory(name, clsdef, **kwargs):
    """Return an instance of Object using kwargs if name is known."""

    cls = type(name, (Object,), {'_metadata': metadata, 'name': name})
    # return an instance of the new class - kwargs provides the attribute names
    # and values
    return cls(**kwargs)


class Object(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs.items())

    def __iter__(self):
        for k in self._metadata['ordered_attrs']:
            yield k, getattr(self, k, None)

    def __str__(self):
        line_vals = [self._metadata['chunk'], self.name]
        oa = self._metadata['ordered_attrs']
        line_vals.extend([str(getattr(self, k)) for k in oa])
        return ' '.join(line_vals)



    """
    def known(self):
        return self.metadata['vanilla'] or self.metadata['local']

    def __str__(self):
        vals = [self.attrs[k] for k in self.attr_names \
                                if self.attrs[k] is not None]
        if self.extra_params:
            vals += self.extra_params

        # Special case for canvas and array-data
        if self.chunk == self.achunk:
            return ' '.join([self.chunk] + vals)
        else:
            return ' '.join([self.chunk, self.element] + vals)

    def name(self):
        if self.element == self.obj:
            return self.attrs.get('type') or self.element
        elif self.element == self.canvas:
            return 'canvas %s' % self.get('name')
        elif self.element == self.restore:
            # There are a few different possible restore formats.
            #     restore pd name;
            #     restore pd;
            #     restore graph;
            #     restore;
            name = self.get('name')
            if name == 'pd':
                if len(self.extra_params):
                    val = '%s %s' % (self.restore, str(self.extra_params[0]))
                else:
                    val = '%s (subpatch)' % self.restore
            elif name == 'graph':
                val = '%s (graph-on-parent subpatch)' % self.restore
            elif name:
                val = '%s %s' % (self.restore, name)
            else:
                val = self.restore

            return val
        else:
            return self.element
    """
