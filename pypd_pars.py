import pypd_object
from pypd_exceptions import InvalidPatch, InvalidLine
from pypd_tree import Tree
import pypd_class_attrs

# Some constants we need to recognize in the patch file
nchunk = '#N'
cchunk = '#C'
achunk = '#A'
xchunk = '#X'
canvas = 'canvas'       # Since there are two different canvas definitions
canvas5 = 'canvas5'     # we need to distinguish them. canvas5/canvas6 are
canvas6 = 'canvas6'     # internal names only, never exposed.
restore = 'restore'
connect = 'connect'
struct = 'struct'
obj = 'obj'
array_data = 'array-data'


def parse(path, includes=[]):
    return parse_lines(readlines(path), includes)


def readlines(path):
    # Universal file reader copes with unix and dos line endings.
    with open(path, 'U') as f:
        # let exceptions bubble up
        return f.readlines()


def parse_header(line_iter, includes):
    # First line should be a canvas or one or more struct definitions then
    # the canvas.
    canvas, structs = None, []
    for line_num, chunk, element, params in line_iter:
        attrs = pypd_class_attrs.get(element, params)
        obj = Object(text, includes)
        if obj.element == Object.CANVAS:
            canvas = obj
            break
        elif obj.element == Object.STRUCT:
            structs.append(obj)
        else:
            raise InvalidLine("%s (%s)" % (text, obj.element), line_num)

    if not canvas or canvas.element != Object.CANVAS:
        raise InvalidPatch('No starting canvas definition found')
    return canvas, structs


def parse_lines(lines, includes=[]):
    """Parse the lines of text into a tree of PD objects."""
    line_iter = chunk_element_iter(pd_line_iterator(lines))

    canvas, structs = parse_header(line_iter, includes)

    tree = cur_node = Tree(canvas)

    for line_num, chunk, element, params in line_iter:

        obj = Object(text, includes)
        if obj.element == Object.CANVAS:
            # Add a branch when we encounter a canvas
            branch = Tree(obj)
            cur_node.addBranch(branch)
            cur_node = branch
        elif obj.element == Object.RESTORE and obj.name() != Object.RESTORE:
            # Pop back up to the parent when we hit a restore object.
            # We ignore restore objects that are called 'restore', i.e.
            # they don't have a name. These are "#C restore;" lines
            # which don't seem to serve any real purpose, so we ignore
            # them
            cur_node.add(obj)
            cur_node = cur_node.parent
        else:
            cur_node.add(obj)

    return tree, structs


elem_params = { nchunk: lambda params: (params[1], params[2:]),
                cchunk: lambda params: (params[1], params[2:]),
                # #A chunk format doesn't have an element name, use
                # 'array_data' as the name
                achunk: lambda params: (array_data, params),
                xchunk: lambda params: (params[1], params[2:])}


def chunk_element_iter(pd_line_iter):
    """Wrap pd_line_iterator splitting off the chunk and element parts."""

    try:
        for line_num, line_text in pd_line_iter:
            params = line_text.split()
            chunk = params[0]
            element, params = elem_params[chunk](params)

            if chunk == Object.cchunk and element != Object.restore:
                raise ValueError('Invalid chunk/element combination: ' \
                                    '"%s %s"' % (chunk, element))
            yield line_num, chunk, element, params
    except IndexError:
        raise ValueError('Too few values to parse in parameters: '
                            '"%s"' % str(params))
    except KeyError:
        raise ValueError('Unrecognized chunk type: "%s"' % chunk)


linesep = ';'
escaped_linesep = '\\;'


def pd_line_iterator(lines):
    """Yield the starting line number and text of each PD logical line.

    Logical lines end with a ';' character. This generator assemples
    multiple physical lines into a single logical line without the ending
    separator charater. A tuple of the starting line number and text is
    yielded."""

    linelst = []
    # Don't strip lines before enumerate, we need the line numbers of
    # the original list of lines.
    for line_num, line in enumerate_stripped_lines(lines):
        if not line:
            continue
        elif pd_line_end(line):
            # Last line: save it in the list of lines but strip the linesep
            # and any whitespace that preceeds it.
            linelst.append((line_num, line[:-1].rstrip()))

            # Yield start-line-number, full-line-text
            yield linelst[0][0], ' '.join([l[1] for l in linelst])
            linelst = []
        else:
            # not the end of a logical line, save it away
            linelst.append((line_num, line))


def enumerate_stripped_lines(lines):
    for line_num, line in enumerate(lines):
        yield line_num, line.strip(' \t\n').expandtabs(1)


def pd_line_end(line):
    return line.endswith(linesep) and not line.endswith(escaped_linesep)
