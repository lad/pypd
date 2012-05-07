#!/usr/bin/env python

import sys
from itertools import izip_longest
import pypd_known_reader

__doc__ = """Pure Data Element Definitions

We need to maintain the names of each attribute for each PD element.
We also need to know the order in which the attributes appear in each
textual Pd object definition.

One option is to write a class for each PD element type which would
contain attribute names and also store the order these attributes
appear in the object definition.

The scheme used here stores the attribute names in order for each PD
object type. This requires less code to maintain since there is just
a single list of attributes in order here.
"""

# TODO Don't do this inline on import

# vanilla.txt contains all the object names and their attributes known to
# pd-vanilla. This is read into a dict where the keys are all names that can
# occur after the chunk type in a PD patch line. The values are the attributes
# that are defined for that type, with the following exceptions:
#
#     'array-data'      Array data (#A) doesn't actually have an element name.
#                       We use this name for convenience.
#     'canvas-5'        There are two canvas definitions. One with 5 params
#     'canvas-6'        at the start of the patch, 6 params otherwise.

vanilla_cfg = pypd_known_reader.read('vanilla.txt')
VANILLA_ELEMENTS, VANILLA_OBJECTS = vanilla_cfg['elements'], \
                                    vanilla_cfg['objects']

ALIASES = []
for objname, alist in vanilla_cfg['aliases'].iteritems():
    VANILLA_OBJECTS.update([(a, VANILLA_OBJECTS[objname]) for a in alist])

# We need these every time we see an 'obj', so save them here...
OBJ_ATTRS = VANILLA_ELEMENTS['obj']
OBJ_NUM_ATTRS = len(OBJ_ATTRS)
TYPE_INDEX = 2


def is_vanilla(name):
    return name in VANILLA_OBJECTS or name in VANILLA_ELEMENTS


def all_vanilla():
    for name in VANILLA_OBJECTS:
        yield name


def is_num_or_var(text):
    # Return known if the object is just a number or dollar-arg,
    # otherwise it's an unknown abstraction.
    try:
        if len(text) > 2 and text[:2] == '\$':
            return True
        else:
            float(text)
            return True
    except ValueError:
        return False


def make_dict(attrs, params):
    kv = dict(izip_longest(attrs, params))
    if kv.has_key(None):
        # If we have a key set to None, then params is longer than attrs
        del kv[None]
        extra = params[len(attrs):]
    else:
        extra = []
    return kv, extra


# TODO This return value is too big now. Refactor into a class
def get(name, params, warn=True):
    """Get element definition filled with the given params.

    A four valued tuple is returned containing:
        . a list of attribute names in the order they occur in the Pd
          patch file format
        . a dict of attribute names and values from "params"
        . a list of the values from "params" not used in generating the
          dict.
        . a flag indicating whether this given "name" is a known Pd
          object, or whether "name" is likely to be another abstraction
          (i.e.  another patch).

    "name" is used to lookup a list of attribute names defined for each Pd
    element/object. The dict returned uses the attributes names as as
    keys, and the corresponding value from the given "params" as the value
    for each key.

    Attribute values are set to None if there are too few values in
    "params". When there are too many parameters the remaining values are
    return as a list in the second argument of the returned tuple.

    The final arg of the return tuple indicates whether a definition was
    found for the given "name". If a definition is not found, the name is
    likely to be an external abstraction.
    """
    # The PD line format is quite inconsistent, so we have to deal with a few
    # special cases here...
    len_params = len(params)

    # Each of these cases attempt to get a list of attribute names for the
    # "name" passed in. The attribute names and the values from "params" are
    # put into a dictionary and returned to the caller.
    # NOTES:
    # - This code is Python 2.6 compatible, so I haven't used the new
    #   collections.OrderedDict.
    # - I've decided against implementing a 2.6 compatible ordered-dict, as
    #   this dict will be exposed to users of PyPd, and I'd be concerned about
    #   any incompatible edge cases where the custom imlementation may differ
    #   from what is expected of a standard dict.

    if name == 'canvas':
        if len_params == 5:
            name = 'canvas-5'
        else:
            name = 'canvas-6'

        attrs = VANILLA_ELEMENTS[name]
        (kv, extra_params) = make_dict(attrs, params)
        return (attrs, kv, extra_params, True)
    elif name == 'obj':
        # There are a few different 'obj' cases to handle here...

        # All 'obj' should start with x, y and type.
        if len_params >= OBJ_NUM_ATTRS:
            oattrs = VANILLA_OBJECTS.get(params[TYPE_INDEX])
            if oattrs is not None:
                known = True
                attrs = OBJ_ATTRS + oattrs
            else:
                # No definition for this object type, use the minimal 'obj'
                # attributes
                attrs = OBJ_ATTRS
                # Since the type wasn't found, check if it's a a number or
                # dollar-arg (a variable). If not, it's a external abstration.
                known = is_num_or_var(params[TYPE_INDEX])

            (kv, extra_params) = make_dict(attrs, params)

            return (attrs, kv, extra_params, known)
        else:
            # Don't even have x,y,type. Save what we can and return it.
            (kv, extra_params) = make_dict(OBJ_ATTRS, params)
            return (OBJ_ATTRS, kv, extra_params, False)
    else:
        try:
            attrs = VANILLA_ELEMENTS[name]
            known = True
        except KeyError:
            # We may encounter elements which this code doesn't know about.
            # In this case we add an empty definition.
            # - Could just use a defaultdict here and omit the warning.
            #   Is there something better to do here?
            if warn:
                print 'Warning: No built-in definition for %s.' % name
            VANILLA_ELEMENTS[name] = []
            attrs = []
            known = False

        (kv, extra_params) = make_dict(attrs, params)
        return (attrs, kv, extra_params, known)

def print_element(name):
    (attrs, k, e, known) = get('obj', ['x', 'y', name])
    if not known:
        (attrs, k, e, known) = get(name, [], warn=False)

    if known:
        if attrs:
            print ' '.join(attrs)
        else:
            print 'Known but empty definition'
    else:
        print 'No definition for %s' % name

if __name__ == '__main__':
    if len(sys.argv) == 2:
        print_element(sys.argv[1])
