#!/usr/bin/env python

import os
import sys
import getopt
import config

__doc__ = """Setup PD installation and include paths.

Usage: %s [-i <dir>] [-r key] [-w | -u] ...

  -i <dir> saves each directory and uses these to search for PD
           abstractions when parsing PD patch files.
  -r <key> removes <key> from the config file
  -w forces windows path matching (case-insensitive)
  -u forces unix path matching (case-sensitive)
""" % (sys.argv[0])

Usage = __doc__[__doc__.find('Usage'):]

if __name__ == '__main__':
    # Use getopt() for compatibility with older pythons
    try:
        options, args = getopt.getopt(sys.argv[1:],
                                      "p:i:r:wuh",
                                      ["pd=", "include=", "remove=", "windows",
                                       "unix", "help"])
        if not options:
            print __doc__
            sys.exit(0)
    except getopt.GetoptError, err:
        print str(err)
        print Usage
        sys.exit(1)

    # Extract command line options
    (include_dirs, remove_keys, case_match) = ([], [], None)
    for opt, arg in options:
        if opt in ('-i', '--include'):
            include_dirs.append(os.path.realpath(arg))
        elif opt in ('-r', '--remove'):
            remove_keys.append(arg)
        elif opt in ('-w', '--windows'):
            if case_match is None:
                case_match = True
            else:
                print 'Please specify only one of -w or -u\n'
                print Usage
                sys.exit(1)
        elif opt in ('-u', '--unix'):
            if case_match is None:
                case_match = False
            else:
                print 'Please specify only one of -w or -u\n'
                print Usage
                sys.exit(1)
        elif opt in ('-h', '--help'):
            print __doc__
            sys.exit(0)

    # Check for trailing arguments and ensure at least one option was given
    if args or not (include_dirs or remove_keys or (case_match is not None)):
        print Usage
        sys.exit(1)

    # Make the pref directory if necessary
    if not os.path.isdir(pdplatform.pref_dir):
        os.makedirs(pdplatform.pref_dir)

    # Open/create a config file and write in the new values/remove any
    # requested keys.
    cfg = pdconfig.PdConfigParser(pdplatform.pref_file)
    if include_dirs:
        cfg['include'] = include_dirs

    if case_match is not None:
        cfg['case_match'] = str(case_match)

    if remove_keys:
        for key in remove_keys:
            del cfg[key]
