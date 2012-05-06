
# vanilla.txt contains all the object names and their attributes known to
# pd-vanilla. This is read into a dict where the keys are all names that can
# occur after the chunk type in a PD patch line. The values are the attributes
# that are defined for that type, with the following exceptions:
#
#     'array-data'      Array data (#A) doesn't have an element name.
#                       Use this name for convenience.
#     'canvas-5'        There are two canvas definitions. One with 5 tokens
#     'canvas-6'        at the start of the patch, 6 tokens otherwise.


sep = ','

def read(path):
    return read_known_lines(readlines(path))


def readlines(path):
    # let exceptions bubble up
    with open(path) as f:
        return f.readlines()


def read_known_lines(lines):
    # sections is a dict, the key is the section name, the value is a
    # dict of items found within that section definition.
    sections, cur_section = {}, None

    # iterator strips spaces at beginning/end and removes blank lines
    for line in line_iter(lines):
        if line.startswith('[') and line.endswith(']'):
            # section header
            cur_section = line[1:-1]
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


def line_iter(lines):
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
