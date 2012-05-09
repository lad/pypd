import pypd_class_attrs
from itertools import izip_longest

class Object(object):

    """Abstraction for PD elements and objects.

    Each line in the PD patch file is used to create an instance of this
    class."""

    @staticmethod
    def factory(line_num, chunk, element, params):
        """Create an appropriate Object instance with the given details."""

        # Determine the attribute names appropriate for this element
        # and its parameters.
        attrs = pypd_class_attrs.get(element, params)

        # Make a dict mapping attribute names to their values
        kv = Object._make_instance_dict(attrs, params)

        # All instances get these attributes too.
        kv.update(line_num = line_num,
                  chunk = chunk,
                  element = element,
                  ordered_attrs = attrs,
                  num_ordered_attrs = len(attrs))

        # Return the created object.
        return Object(kv)

    @staticmethod
    def _make_instance_dict(attrs, values):
        """Create a map from the attribute names to their values."""

        kv = dict(izip_longest(attrs, values))
        if kv.has_key(None):
            # If a key is set to None we have more values than attribute names
            del kv[None]
        # Also add arg1 ... argn for each value.
        kv.update([('arg%d' % (n + 1), value) \
                   for n, value in enumerate(values)])
        return kv

    def __init__(self, kv):
        """Simple constructor takes a dictionary of attribute names/values.

        Don't use this directly, use the static factory."""
        self.__dict__.update(kv.items())

    def __setattr__(self, name, value):
        raise AttributeError('Object instances are immutable')

    def __iter__(self):
        """Yield each attribute name/value."""
        for k in self.ordered_attrs:
            yield k, getattr(self, k, None)

    def __str__(self):
        """Return the original text suitable for storing in a patch file."""
        line_vals = [self.chunk, self.element]
        line_vals.extend([v for k,v in self])
        return ' '.join(line_vals)
