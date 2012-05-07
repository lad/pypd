#!/usr/bin/env python

import sys
import os
import getopt
import pypd

__doc__ = """Show information about Pure data patch files.

Usage: %s [OPTION]... [FILE]...
-v, --vanilla     Print objects found in the patch file which are not known
                  to PD vanilla. If the patch is compatible with PD vanilla
                  no output is shown.
-e, --extended    Print objects found in the patch file which are not known
                  to PD extended. If the patch is compatible with PD
                  extended no output is shown.
-m, --missing     Print objects not found in any search directory.
-t, --tree        Print a tree of the structure of the patch file.
-d, --depend      Print a list of the directories needed for the
                  abstractions used in the patch file.
-i, --include     Add a directory to the list of directories that will be
                  searched when objects are found in the patch file which
                  are not known to PD vanilla.
-n, --nonames     Don't output filenames when multiple files are given.
-h, --help        Prints this help
-x, --examples    Print some examples.
""" # % os.path.basename(sys.argv[0])

usage = __doc__[__doc__.find('Usage'):]


class PdOpts(object):

    """Parse command line options into attributes."""

    """All actions require arguments except help and examples."""
    ACTION_REQUIRES_ARGS = [True, True, True, True, True, False, False]

    MULTI_OPTS_ERR = 'Please specify one of {-v|-e|-m|-t|-d}'

    def __init__(self, argv):
        self.argv = argv
        options, self.args = getopt.getopt(
                argv[1:],
                'vemtdi:p:nhx',
                ['vanilla', 'extended', 'missing', 'tree', 'depend',
                 'include=', 'pd=', 'nonames', 'help', 'examples'])
        self.action = None
        self.include_dirs = []
        self.print_names = True

        for opt, arg in options:
            if opt in ('-v', '--vanilla'):
                if self.action:
                    raise getopt.GetoptError(self.MULTI_OPTS_ERR)
                self.action = PdList.VANILLA

            elif opt in ('-e', '--extended'):
                if self.action:
                    raise getopt.GetoptError(self.MULTI_OPTS_ERR)
                self.action = PdList.EXTENDED

            elif opt in ('-m', '--missing'):
                if self.action:
                    raise getopt.GetoptError(self.MULTI_OPTS_ERR)
                self.action = PdList.MISSING

            elif opt in ('-t', '--tree'):
                if self.action:
                    raise getopt.GetoptError(self.MULTI_OPTS_ERR)
                self.action = PdList.TREE

            elif opt in ('-d', '--depend'):
                if self.action:
                    raise getopt.GetoptError(self.MULTI_OPTS_ERR)
                self.action = PdList.DEPENDS

            elif opt in ('-i', '--include'):
                self.include_dirs.append(os.path.realpath(arg))

            elif opt in ('-n', '--nonames'):
                self.print_names = False

            elif opt in ('-h', '--help'):
                self.action = PdList.HELP

            elif opt in ('-x', '--examples'):
                self.action = PdList.EXAMPLES

        if self.action:
            if self.ACTION_REQUIRES_ARGS[self.action - 1] and not self.args:
                raise getopt.GetoptError('No arguments given.')
            elif self.action in (PdList.VANILLA, PdList.EXTENDED) and \
                 self.include_dirs:
                raise getopt.GetoptError('-i is not valid with -v or -e')

    def examples(self):
        print """
pdlist examples
---------------

...todo...

"""


class PdList(object):

    """These are the possible action chosen by the command line arguments."""
    (VANILLA, EXTENDED, MISSING, TREE, DEPENDS, HELP, EXAMPLES) = range(1, 8)

    def __init__(self, action, includes):
        #cfg = pdconfig.PdConfigParser(pdplatform.pref_file)
        #cfg_includes = cfg.get('include') or []
        #cfg_includes.extend(includes)
        #self.inc = pdincludes.PdIncludes(cfg_includes)
        pass

    def is_vanilla(self):
        pass

    def is_extended(self):
        pass

    def tree(self):
        pass

    def depends(self):
        pass


##### MAIN #####


def list_patch(cmdline):

    script_name = cmdline[0]
    global __doc__
    __doc__ = __doc__ % script_name


    # First get options and args...

    try:
        opts = PdOpts(sys.argv)
    except getopt.GetoptError, err:
        print str(err), '\n'
        print usage
        sys.exit(1)

    if not opts.action:
        if opts.args:
            print 'No arguments given.\n'
            print usage
        else:
            print __doc__
        sys.exit(0)
    if opts.action == PdList.HELP:
        print usage
        sys.exit(0)
    elif opts.action == PdList.EXAMPLES:
        opts.examples()
        sys.exit(0)

    pdlist = PdList(opts.action, opts.include_dirs)
    exit_codes = []

    #cfg = pdconfig.PdConfigParser(pdplatform.pref_file)
    #includes = cfg.get('include') or []
    #includes.extend(opts.include_dirs)
    #inc = pdincludes.PdIncludes(includes)
    inc = []

    if not opts.print_names:
        if opts.action in (PdList.DEPENDS, PdList.MISSING):
            output_set = set()
            have_missing = False

    for fname in opts.args:
        try:
            if opts.print_names:
                print '%s' % fname,

            patch = pypd.Patch(fname, inc)
            if opts.action == PdList.TREE:
                if opts.print_names:
                    print
                for (node, obj_id, level) in patch:
                    print '%s%s' % (' ' * (level * 4), node.value.name())

                exit_codes.append(0)

            elif opts.action == PdList.VANILLA:
                names = set([node.value.name() for (node, obj_id, level) in \
                             patch.select(vanilla=False)])
                if names:
                    if opts.print_names:
                        print 'is not pd-vanilla compatible. Missing:'
                        for name in names:
                            print '\t', name
                elif opts.print_names:
                    print 'is vanilla compatible'

                exit_codes.append(bool(names))

            elif opts.action == PdList.EXTENDED:
                names = set([node.value.name() for (node, obj_id, level) in \
                             patch.select(known=False)])
                if names:
                    if opts.print_names:
                        print 'is not pd-extended compatible. Missing:'
                        for name in names:
                            print '\t', name
                elif opts.print_names:
                    print 'is pd-extended compatible'

                exit_codes.append(bool(names))

            elif opts.action == PdList.MISSING:
                names = set([node.value.name() for (node, obj_id, level) in \
                             patch.select(known=False)])
                if opts.print_names:
                    print
                    for name in names:
                        print '\t', name
                else:
                    output_set.update(names)

                exit_codes.append(bool(names))

            elif opts.action == PdList.DEPENDS:
                def fn(node_id_level):
                    return bool(node_id_level[0].value.include)

                includes = set([node.value.include \
                                for (node, o, l) in filter(fn, patch) \
                                for node.value.include in node.value.include])

                if opts.print_names:
                    print
                    if includes:
                        print '    %s' % '\n    '.join(includes)
                elif includes:
                    output_set.update(includes)

                # Check for missing abstractions
                if any([node.value.name() for (node, obj_id, level) in \
                        patch.select(known=False)]):
                    if opts.print_names:
                        print 'Contains missing abstractions. Use -m to ' \
                              'see these.'
                    else:
                        have_missing = True

                exit_codes.append(0)

        except Exception, ex:
            if opts.print_names:
                print
            print '***** Failed to parse file "%s"' % fname
            print str(ex)
            exit_codes.append(1)
            #traceback.print_exc(ex)

    if not opts.print_names and \
       opts.action in (PdList.DEPENDS, PdList.MISSING):
        out = list(output_set)
        out.sort()
        print '\n'.join(out)
        if have_missing:
            print 'Contains missing abstractions. Use -m to see these.'

    # Exit with 0 for success or 1 for error
    sys.exit(any(exit_codes))

if __name__ == '__main__':
    list_patch(sys.argv)
