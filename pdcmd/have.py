#!/usr/bin/env python

import os
import difflib
from collections import defaultdict

import config
import opts
import includes
import element

#SCRIPT_NAME = os.path.basename(sys.argv[0])

__doc__ = """Check the availability of the given Pure Data object.

Usage: %s [OPTION]... OBJECT...
-i, --include=DIR   Add a directory to the list of locations that will be
                    searched to find the given object name.
-v, --vanilla       Check if the object is available in PD vanilla.
-c, --closest       Search for the closest matches to the name given.
-e, --examples      Show examples.
-h, --help          Print this help.
"""# % SCRIPT_NAME

USAGE = __doc__[__doc__.find('Usage'):]

EXAMPLES = __doc__.split('\n')[0] + """

Examples:
    # %s vslider bang
    vslider << vanilla built-in >>
    bang << vanilla built-in >>

    # %s once
    once
        /usr/lib/pd-extended/extra/iemlib
        /usr/lib/pd-extended/extra/purepd

    # %s -i /usr/local/lib/pd/my/patches myobject
    myobject /usr/local/lib/pd/my/patches/project1/

    # %s rand
    rand: not found. Closest matches:
        random << vanilla built-in >>
        vradio << vanilla built-in >>
        rain /usr/lib/pd-extended/extra/pmpd/examples
        hradio << vanilla built-in >>
        sand /usr/lib/pd-extended/extra/pmpd/examples
        rand~ /usr/lib/pd-extended/extra/cyclone

    # %s abs
    abs << vanilla built-in >>

    # %s -c abs
    abs: Closest matches:
        abs << vanilla built-in >>
        tabset /usr/lib/pd-extended/extra/zexy
        abs~
            /usr/lib/pd-extended/extra/markex
            /usr/lib/pd-extended/extra/vanilla
            /usr/lib/pd-extended/extra/zexy
            /usr/lib/pd-extended/extra/creb
            /usr/lib/pd-extended/extra/cyclone
        vabs /usr/lib/pd-extended/extra/smlib
"""# % ((SCRIPT_NAME,) * 6)

VANILLA_DIR = '<< vanilla built-in >>'


def match(in_names, dirs=[], vanilla_only=False, closest_only=False):
    """Search the known include paths for the given object names.

    A tuple is returned containing two dicts is returned. The first contains
    each name and the list of directories where it can be found. The second
    dict contains entries for each name that we didn't find, or entries for
    all names if closest_only is set to True. The entries themselves are
    a dictionary of closest matches for each name, and the directories where
    each match can be found.
    """

    # Get the configured include directories and add any directories passed in
    cfg = pdconfig.PdConfigParser(pdplatform.pref_file)
    cfg_includes = cfg.get('include')
    if dirs:
        if cfg_includes:
            cfg_includes.extend(dirs)
        else:
            cfg_includes = dirs
    includes = pdincludes.PdIncludes(cfg_includes)

    vanilla_objects = list(pdelement.all_vanilla())
    installed_objects = list(includes)
    # the return values
    name_dirs, closest_name_dirs = {}, {}

    close_match = difflib.get_close_matches
    for in_name in in_names:
        # check for exact match in vanilla (but not when matching closest only)
        if not closest_only and pdelement.is_vanilla(in_name):
            name_dirs[in_name] = [VANILLA_DIR]
            continue

        # If vanilla_only is True we don't check the paths on disk, just
        # built-ins
        if not closest_only and not vanilla_only:
            name_dirs[in_name] = includes.get(in_name)
        else:
            name_dirs[in_name] = None

        if not name_dirs[in_name]:
            closest_name_dirs[in_name] = defaultdict(list)

            # Find the closest matching vanilla object names and make an
            # entry for each one in closest_name_dirs
            for close_name in close_match(in_name, vanilla_objects):
                closest_name_dirs[in_name][close_name] = [VANILLA_DIR]

            if not vanilla_only:
                # Find the closest matching names for installed objected
                for close_name in close_match(in_name, installed_objects):
                    close_dirs = includes.get(close_name)
                    closest_name_dirs[in_name][close_name].extend(close_dirs)

    return name_dirs, closest_name_dirs

spaces = lambda indent: indent and ' ' * indent or ''


def print_name_dirs(name, dirs, indent=0):
    """Print (optionally indented) name and directory list."""

    if len(dirs) == 1:
        s = '%s%s: %s' % (spaces(indent), name, dirs[0])
        if len(s) < 80:
            print s
            return

    print '%s%s:' % (spaces(indent), name)
    if indent:
        print spaces(indent * 2),
        s = '\n' + spaces(indent * 2 + 1)
    else:
        print spaces(3),
        s = '\n' + spaces(4)
    print s.join(dirs)


def print_results(opts, name_dirs, closest_name_dirs):
    """Format and print results to stdout"""

    for name in opts.args:
        dirs = name_dirs[name]
        if dirs:
            print_name_dirs(name, list(dirs))
        else:
            print '%s:' % name,
            if not opts.closest:
                print 'not found.',

            if closest_name_dirs.get(name):
                print 'Closest matches:'
                fdirs = dict(closest_name_dirs[name])  # take a copy

                # If we did a closest only match, check if there's an exact
                # match and print it first.
                if opts.closest and fdirs.get(name):
                    print_name_dirs(name, list(fdirs[name]), indent=4)
                    del fdirs[name]

                for fname in fdirs:
                    print_name_dirs(fname, list(fdirs[fname]), indent=4)
            else:
                print 'No matches.'

def have(cmdline):
    try:
        script_name = cmdline[0]
        __doc__ == __doc__ % script_name
        EXAMPLES = EXAMPLES % ((script_name,) * 6)

        opts = pdopts.PdOpts(cmdline[1:],
                             ['include=', 'vanilla', 'closest', 'help',
                              'examples'],
                              excluded=[['help', 'examples'],
                                        ['include', 'vanilla']])
    except pdopts.PdOptsError, err:
        print str(err), '\n'
        print USAGE
        return 1

    if opts.help:
        print USAGE
        return 1
    elif opts.examples:
        print EXAMPLES
        return 1
    elif not opts.args:
        print __doc__
        return 1

    print_results(opts, *match(opts.args, opts.include,
                               vanilla_only=opts.vanilla,
                               closest_only=opts.closest))
    return 0
