import pypd_known_reader

__doc__ = """Pure Data element and object definitions."""


# We could use a class here, but there's really no need.
ELEM_DEFS = {}
OBJ_DEFS = {}
MIN_OBJ_PARAMS = 0
TYPE_INDEX = 2

ELEMENTS_SECTION = 'elements'
OBJECTS_SECTION = 'objects'
ALIASES_SECTION = 'aliases'


def init(vanilla_defs_path):
    """Read and initialise class definitions using the given file."""
    global ELEM_DEFS, OBJ_DEFS, MIN_OBJ_PARAMS

    vanilla_cfg = pypd_known_reader.read(vanilla_defs_path)
    ELEM_DEFS = vanilla_cfg[ELEMENTS_SECTION]
    OBJ_DEFS = vanilla_cfg[OBJECTS_SECTION]

    if vanilla_cfg.has_key(ALIASES_SECTION):
        for objname, alist in vanilla_cfg[ALIASES_SECTION].iteritems():
            if objname in ELEM_DEFS:
                dct = ELEM_DEFS
            elif objname in OBJ_DEFS:
                dct = OBJ_DEFS
            else:
                raise ValueError('Cannot create alias. No element or object '
                                 'called "%s".' % objname)

            dct.update([(alias, dct[objname]) for alias in alist])

    MIN_OBJ_PARAMS = len(ELEM_DEFS['obj'])


def get(element_name, params):
    """Return a PdClassDef object for the given name and parameters."""
    if element_name == 'canvas':
        return _get_canvas_def(params)
    elif element_name == 'obj':
        return _get_obj_def(params)
    else:
        return _get_elem_def(element_name)


def _get_canvas_def(params):
    if len(params) == 5:
        return ELEM_DEFS['canvas-5']
    else:
        return ELEM_DEFS['canvas-6']


def _get_obj_def(params):
    # There are a few different 'obj' cases to handle here...

    # All 'obj' should start with x, y and type.
    if len(params) < MIN_OBJ_PARAMS:
        # We don't even have the minimal object definition, this patch
        # line may be malformed.
        attrs = []
    else:
        oattrs = OBJ_DEFS.get(params[TYPE_INDEX])
        if oattrs is not None:
            # All entries in OBJ_DEFS are PD 'obj' elements. These all
            # start with "x, y, type" as in the 'obj' definition, so we
            # prepend those attribute names.
            attrs = ELEM_DEFS['obj'] + oattrs
        else:
            # No definition for this object type. Check if it's a number of
            # a PD dollar-arg (a variable).
            if _is_const_param(params[TYPE_INDEX]):
                attrs = ELEM_DEFS['obj']
            else:
                # This is probably an external abstraction.
                attrs = []

    return attrs


def _get_elem_def(name):
    return ELEM_DEFS.get(name) or []


def _is_num_param(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def _is_var_param(text):
    return len(text) > 2 and text[:2] == '\$'


def _is_const_param(text):
    return _is_num_param(text) or _is_var_param(text)
