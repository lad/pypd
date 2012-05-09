
__doc__ = """Read a file containing attribute names for each known object.

The purpose of this "known objects" file is to provide attribute names
for the Python objects that we create when parsing the PD patch file.
The parameters given in each line in the patch file map onto attributes
defined in this "known objects" file.

The file should contain an [elements] and [objects] section, and
optionally an [aliases] section. For example:

[elements]
obj             x, y, name
floatatom       x, y, width, lower, upper, label_pos, label, receive, send
text            x, y, text

[objects]
!=              rhs
%               rhs
vslider         width, height, bottom, top, log, init, send, receive, \
                label, label_x, label_y, font, font_size, \
                bg_color, fg_color, label_color, default_value, steady_on_click

[aliases]
vslider         vsl
hslider         hsl
"""


sep = ','

def read(path):
    # let exceptions bubble up
    with open(path) as f:
        return _parse_known_lines(f.readlines())


def _parse_known_lines(lines):
    """Parse the given lines into a dict of object name to attribute list.

    The key (the object name) is the text that occurs after the chunk type
    in a PD patch file.  The values are the attribute names that are
    defined for that type, with the following exceptions:

        'array-data'    Array data (#A) doesn't have an element name,
                        so we use this name for convenience.
        'canvas-5'      There are two canvas definitions. One with 5 tokens
        'canvas-6'      at the start of the patch, 6 tokens otherwise."""

    # sections is a dict, the key is the section name, the value is a
    # dict of items found within that section definition.
    sections, cur_section = {}, None

    # iterator strips spaces at beginning/end and removes blank lines
    for line in _line_iter(lines):
        if line.startswith('[') and line.endswith(']'):
            # section header
            cur_section = line[1:-1]            # strip surrounding []
            sections[cur_section] = {}
        else:
            key_line = line.split(' ', 1)
            # length is never zero, line_iter strips out blank lines
            if len(key_line) == 2:
                key, valstr = key_line
                vals = [val.strip() \
                        for val in valstr.split(sep)]
            else:
                key, vals = key_line[0], []

            try:
                sections[cur_section][key] = vals
            except KeyError, ex:
                raise ValueError('No section header')

    return sections


def _line_iter(lines):
    linelst = []
    for line in (s for s in (line.strip() for line in lines) \
                            if s and not s.startswith('#')):
        # A definition can be continued on the next line if it ends with a
        # "\" character.
        if line.endswith('\\'):
            linelst.append(line[:-1])
        else:
            linelst.append(line)
            yield ' '.join(linelst)
            linelst = []
