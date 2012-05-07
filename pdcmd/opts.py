#!/usr/bin/env python

import sys
import os
import getopt


__doc__ = """Easy command line parsing without the tedium."""


class Opts(object):

    """Parse command line options into attributes.

    Opts([command-line], ['long-option-name-1', ...])

    Command line options are separated into two groups: flags options,
    which take no value and value options which have a value given after
    the option and can be specified multiple times.

    The names of the flag and value options that are passed to the
    constructor become attributes of the Opts object and can be used
    to access the results of the parsed command line.

    args = ['-v', '--dir', '/usr']
    opts = Opts(args, ['verbose', 'dirs', 'help'])
    opts.v, opts.verbose == 1, 1
    opts.d, opts.dirs == 0, 0
    """

    MULTI_OPTS_ERR = 'Please specify one option from: %s'

    def __init__(self, cmdline, opt_names, required=[], excluded=[]):
        self.cmdline = cmdline
        self.opt_names = opt_names

        # _cmd_mask: an ORed mask of the flag (non-value) arguments
        # _cmd_values: a dict keyed by short option name (no ":" or "=").
        #              The value is a list the values from the command line.
        # _opt_flags: a dict keyed by short name. One value for each flag
        #             option in opt_names (powers of 2)
        self._cmd_mask, self._cmd_values, self._opt_flags = 0, {}, {}

        if not opt_names:
            raise ValueError('No options given.')

        # short_names and long_names are what will be passed into getopt
        num_flags, self.short_names, self.long_names = 0, [], []
        # Since we have a custom __getattr__ we save the names of our
        # attribute here for __dir__
        self.attr_names = ['cmdline', 'opt_names']

        def isdup(sname, lname):
            return sname in self.attr_names or lname in self.attr_names

        for long_name in opt_names:
            if long_name.endswith('='):
                long_name = long_name[:-1]
                short_name = long_name[0]
                if isdup(short_name, long_name):
                    raise ValueError('Duplicate options given.')
                self.attr_names.append(short_name)
                self.attr_names.append(long_name)

                # create an entry in _cmd_values for this (value) option
                self._cmd_values[short_name] = []
                short_name = short_name + ':'
                long_name = long_name + '='
            else:
                short_name = long_name[0]
                if isdup(short_name, long_name):
                    raise ValueError('Duplicate options given.')
                self.attr_names.append(short_name)
                self.attr_names.append(long_name)

                # create a unique flag for each flag option
                self._opt_flags[short_name] = pow(2, num_flags)
                num_flags += 1

            self.short_names.append(short_name)
            self.long_names.append(long_name)

        self.attr_names.extend(['cmdline', 'opt_names'])

        if not cmdline:
            self.args = None
            # Nothing to parse
            return

        try:
            # getopt needs a string for the short names, long names are a list
            options, self.args = getopt.getopt(cmdline,
                                               ''.join(self.short_names),
                                               self.long_names)
        except getopt.GetoptError, ex:
            raise ValueError(str(ex))

        for opt, arg in options:
            short_name = opt.rsplit('-')[-1][0]
            val_list = self._cmd_values.get(short_name)
            if val_list is not None:
                val_list.append(arg)
            else:
                self._cmd_mask |= self._opt_flags[short_name]

        for req in required:
            try:
                if not getattr(self, req):
                    raise ValueError('Missing required argument: %s' % req)
            except AttributeError, ex:
                raise ValueError('Invalid required argument: %s' % req)

        for excl_names in excluded:
            if len([name for name in excl_names if getattr(self, name)]) > 1:
                raise ValueError(self.MULTI_OPTS_ERR % \
                                 ', '.join(['--%s' % s for s in excl_names]))

    def __getattr__(self, name):
        """Make the parsed command line available as attributes."""

        if len(name) == 1:
            short_name = name
        elif name in self.attr_names:
            short_name = name[0]
        else:
            raise AttributeError("Opts instance has no attribute "
                                 "'%s'" % name)

        flag = self._opt_flags.get(short_name)
        if flag:
            # For flag options the command mask will have been set if that
            # flag was given on the command line
            return bool(self._cmd_mask & flag)
        else:
            # For value options _cmd_values contains a list of the values given
            # on the command line for that option (may be given multiple times)
            val = self._cmd_values.get(short_name)
            if val is not None:
                return val
            else:
                raise AttributeError("Opts instance has no attribute "
                                     "'%s'" % name)

    def __dir__(self):
        """Return list of attributes including short and long option names."""
        return dir(object) + self.attr_names
