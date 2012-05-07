import unittest
import os
import time
from pypd.cmd import Opts


def flatten(lst):
    """Flatten the given list of iterables into a single list."""
    return [i for sublist in lst for i in sublist]


class TestOpts(unittest.TestCase):

    def test_empty_options(self):
        self.assertRaises(ValueError, Opts, [], [])
        try:
            opts = Opts([], [])
        except ValueError, ex:
            self.assertTrue(len(str(ex)) > 0)

    def test_attribute_error(self):
        opts = Opts(['-h'], ['help'])
        try:
            opts.blah
        except AttributeError, ex:
            self.assertTrue(ex)

        try:
            opts.x
        except AttributeError, ex:
            self.assertTrue(ex)

    def test_dir(self):
        value_opts = ['%s_arg' % chr(i) for i in range(ord('a'), ord('m') + 1)]
        flag_opts = ['%s_flag' % chr(i) for i in range(ord('n'), ord('z') + 1)]
        all_options = ['%s=' % a for a in value_opts] + flag_opts
        opts = Opts([], all_options)
        attrs = dir(opts)
        for opt in value_opts + flag_opts:
            self.assertTrue(opt in attrs)

    def test_duplicate_options(self):
        # flag: long option matches
        self.assertRaises(ValueError, Opts, ['-h'], ['help', 'help'])
        # flag: first char matches
        self.assertRaises(ValueError, Opts, ['-h'], ['help', 'hrlp'])
        # flag: first char matches
        self.assertRaises(ValueError, Opts,
                          [], ['abc', 'def', 'ghi', 'akl'])

        # value: long option matches
        self.assertRaises(ValueError, Opts,
                          ['-i dir'], ['inc=', 'inc='])
        # value: first char matches
        self.assertRaises(ValueError, Opts, ['-h'], ['inc=', 'imp='])
        # value: first char matches
        self.assertRaises(ValueError, Opts,
                          [], ['abc=', 'def=', 'ghi=', 'akl='])

    def test_one_flag(self):
        # empty command line
        opts = Opts([], ['flag1'])
        self.assertFalse(opts.flag1)

        # One flag given (short name)
        opts = Opts(['-f'], ['flag1'])
        self.assertTrue(opts.flag1)

        # One flag given (long name)
        opts = Opts(['--flag1'], ['flag1'])
        self.assertTrue(opts.flag1)

        # Unknown flag given short and long names
        self.assertRaises(ValueError, Opts, ['--flagx'], ['flag1'])
        self.assertRaises(ValueError, Opts, ['--flag1', '--flagx'],
                                                 ['flag1'])
        self.assertRaises(ValueError, Opts, ['-x'], ['flag1'])
        self.assertRaises(ValueError, Opts, ['-f', '-x'], ['flag1'])

    def test_multi_flags(self):
        flag_opts = ['%s_arg' % chr(i) for i in range(ord('a'), ord('z') + 1)]

        # empty command line, options set to 0
        opts = Opts([], flag_opts)
        for flag in flag_opts:
            self.assertFalse(getattr(opts, flag))

        # command line has long name for all options
        opts = Opts(['--%s' % f for f in flag_opts], flag_opts)
        for flag in flag_opts:
            self.assertTrue(getattr(opts, flag))
            self.assertTrue(getattr(opts, flag[0]))

        # command line has long name for all options
        opts = Opts(['-%s' % f[0] for f in flag_opts], flag_opts)
        for flag in flag_opts:
            self.assertTrue(getattr(opts, flag))
            self.assertTrue(getattr(opts, flag[0]))

        # command line has long name for half the options
        opts = Opts(['--%s' % f \
                         for i, f in enumerate(flag_opts) if i % 2], flag_opts)
        for i, flag in enumerate(flag_opts):
            if i % 2:
                self.assertTrue(getattr(opts, flag))
                self.assertTrue(getattr(opts, flag[0]))
            else:
                self.assertFalse(getattr(opts, flag))
                self.assertFalse(getattr(opts, flag[0]))

        # command line has short name for half the options
        opts = Opts(['-%s' % f[0] \
                         for i, f in enumerate(flag_opts) if i % 2], flag_opts)
        for i, flag in enumerate(flag_opts):
            if i % 2:
                self.assertTrue(getattr(opts, flag))
                self.assertTrue(getattr(opts, flag[0]))
            else:
                self.assertFalse(getattr(opts, flag))
                self.assertFalse(getattr(opts, flag[0]))

    def test_one_value_option(self):
        # empty command line
        opts = Opts([], ['dirs='])
        self.assertTrue(opts.d == [])
        self.assertTrue(opts.dirs == [])

        # One value given (short)
        opts = Opts(['-d', 'val1'], ['dirs='])
        self.assertTrue(opts.d == ['val1'])
        self.assertTrue(opts.dirs == ['val1'])

        # One value given (long)
        opts = Opts(['--dirs', 'val1'], ['dirs='])
        self.assertTrue(opts.d == ['val1'])
        self.assertTrue(opts.dirs == ['val1'])

        # Multi values given (short)
        cmdline = ['-d', 'value'] * 10
        result = ['value'] * 10
        opts = Opts(cmdline, ['dirs='])
        self.assertTrue(opts.d == result)
        self.assertTrue(opts.dirs == result)

        # Multi values given (long)
        cmdline = ['--dirs', 'value'] * 10
        result = ['value'] * 10
        opts = Opts(cmdline, ['dirs='])
        self.assertTrue(opts.d == result)
        self.assertTrue(opts.dirs == result)

        # Missing value
        self.assertRaises(ValueError, Opts, ['-d'], ['dirs='])

    def test_multi_value_options(self):
        # empty command line
        value_opts = ['%s_arg' % chr(i) for i in range(ord('a'), ord('z') + 1)]
        opts = Opts([], ['%s=' % a for a in value_opts])
        for vo in value_opts:
            self.assertTrue(getattr(opts, vo) == [])

        # One value given (short)
        opts = Opts(['-a', 'val1'], ['%s=' % a for a in value_opts])
        self.assertTrue(opts.a == ['val1'])
        self.assertTrue(opts.a_arg == ['val1'])

        # One value given (long)
        opts = Opts(['--a_arg', 'val1'], ['%s=' % a for a in value_opts])
        self.assertTrue(opts.a == ['val1'])
        self.assertTrue(opts.a_arg == ['val1'])

        # One value for all options given (short)
        line = flatten([('-%s' % a[0], 'val_%s' % a[0]) for a in value_opts])
        opts = Opts(line, ['%s=' % a for a in value_opts])
        for vo in value_opts:
            self.assertTrue(getattr(opts, vo[0]) == ['val_%s' % vo[0]])
            self.assertTrue(getattr(opts, vo) == ['val_%s' % vo[0]])

        # One value for all options given (long)
        line = flatten([('--%s' % a, 'val_%s' % a) for a in value_opts])
        opts = Opts(line, ['%s=' % a for a in value_opts])
        for vo in value_opts:
            self.assertTrue(getattr(opts, vo[0]) == ['val_%s' % vo])
            self.assertTrue(getattr(opts, vo) == ['val_%s' % vo])

        # Several values for all options given (short)
        line = [('-%s' % a[0], 'val1_%s' % a[0]) for a in value_opts]
        line.extend([('--%s' % a[0], 'val2_%s' % a[0]) for a in value_opts])
        line.extend([('--%s' % a[0], 'val3_%s' % a[0]) for a in value_opts])
        line = flatten(line)
        opts = Opts(line, ['%s=' % a for a in value_opts])
        for vo in value_opts:
            result = ['val%d_%s' % (i, vo[0]) for i in range(1, 4)]
            self.assertTrue(getattr(opts, vo[0]) == result)
            self.assertTrue(getattr(opts, vo) == result)
            self.assertTrue(getattr(opts, vo[0]) == result)
            self.assertTrue(getattr(opts, vo) == result)
            self.assertTrue(getattr(opts, vo[0]) == result)
            self.assertTrue(getattr(opts, vo) == result)

        # Several values for all options given (long)
        line = [('--%s' % a, 'val1_%s' % a) for a in value_opts]
        line.extend([('--%s' % a, 'val2_%s' % a) for a in value_opts])
        line.extend([('--%s' % a, 'val3_%s' % a) for a in value_opts])
        line = flatten(line)
        opts = Opts(line, ['%s=' % a for a in value_opts])
        for vo in value_opts:
            result = ['val%d_%s' % (i, vo) for i in range(1, 4)]
            self.assertTrue(getattr(opts, vo[0]) == result)
            self.assertTrue(getattr(opts, vo) == result)
            self.assertTrue(getattr(opts, vo[0]) == result)
            self.assertTrue(getattr(opts, vo) == result)
            self.assertTrue(getattr(opts, vo[0]) == result)
            self.assertTrue(getattr(opts, vo) == result)

        # Several values for all options given (short and long)
        line = [('--%s' % a, 'val1_%s' % a) for a in value_opts]
        line.extend([('-%s' % a[0], 'val2_%s' % a[0]) for a in value_opts])
        line.extend([('--%s' % a, 'val3_%s' % a) for a in value_opts])
        line = flatten(line)
        opts = Opts(line, ['%s=' % a for a in value_opts])
        for vo in value_opts:
            result = ['val1_%s' % vo, 'val2_%s' % vo[0], 'val3_%s' % vo]
            self.assertTrue(getattr(opts, vo[0]) == result)
            self.assertTrue(getattr(opts, vo) == result)

        # Missing value
        self.assertRaises(ValueError, Opts, ['-d'], ['dirs='])

    def test_multi_flag_multi_value_options(self):
        # empty command line
        value_opts = ['%s_arg' % chr(i) for i in range(ord('a'), ord('m') + 1)]
        flag_opts = ['%s_flag' % chr(i) for i in range(ord('n'), ord('z') + 1)]
        all_options = ['%s=' % a for a in value_opts] + flag_opts
        opts = Opts([], all_options)
        for vo in value_opts:
            self.assertTrue(getattr(opts, vo) == [])
        for f in flag_opts:
            self.assertFalse(getattr(opts, f))

        # Several short flags
        opts = Opts(['-n', '-w', '-z'], all_options)
        self.assertTrue(opts.n)
        self.assertTrue(opts.n_flag)
        self.assertTrue(opts.w)
        self.assertTrue(opts.w_flag)
        self.assertTrue(opts.z)
        self.assertTrue(opts.z_flag)

        # Several long flags
        opts = Opts(['--n_flag', '--w_flag', '--z_flag'], all_options)
        self.assertTrue(opts.n)
        self.assertTrue(opts.n_flag)
        self.assertTrue(opts.w)
        self.assertTrue(opts.w_flag)
        self.assertTrue(opts.z)
        self.assertTrue(opts.z_flag)

        # Several short flags and short values
        opts = Opts(['-t', '-s', '-n', '-m', 'mval1', '-a', 'aval',
                        '-m', 'mval2'], all_options)
        self.assertTrue(opts.t)
        self.assertTrue(opts.t_flag)
        self.assertTrue(opts.s)
        self.assertTrue(opts.s_flag)
        self.assertTrue(opts.n)
        self.assertTrue(opts.n_flag)
        self.assertTrue(opts.m == ['mval1', 'mval2'])
        self.assertTrue(opts.m_arg == ['mval1', 'mval2'])
        self.assertTrue(opts.a == ['aval'])
        self.assertTrue(opts.a_arg == ['aval'])

        # Several short flags and long values
        opts = Opts(['-t', '-s', '-n', '--m_arg', 'mval1',
                          '--a_arg', 'aval', '--m_arg', 'mval2'], all_options)
        self.assertTrue(opts.t)
        self.assertTrue(opts.t_flag)
        self.assertTrue(opts.s)
        self.assertTrue(opts.s_flag)
        self.assertTrue(opts.n)
        self.assertTrue(opts.n_flag)
        self.assertTrue(opts.m == ['mval1', 'mval2'])
        self.assertTrue(opts.m_arg == ['mval1', 'mval2'])
        self.assertTrue(opts.a == ['aval'])
        self.assertTrue(opts.a_arg == ['aval'])

        # Several long flags and short values
        opts = Opts(['--t_flag', '--s_flag', '--n_flag',
                        '-m', 'mval1', '-a', 'aval', '-m', 'mval2'],
                        all_options)
        self.assertTrue(opts.t)
        self.assertTrue(opts.t_flag)
        self.assertTrue(opts.s)
        self.assertTrue(opts.s_flag)
        self.assertTrue(opts.n)
        self.assertTrue(opts.n_flag)
        self.assertTrue(opts.m == ['mval1', 'mval2'])
        self.assertTrue(opts.m_arg == ['mval1', 'mval2'])
        self.assertTrue(opts.a == ['aval'])
        self.assertTrue(opts.a_arg == ['aval'])

    def test_required(self):
        # missing 'b'
        self.assertRaises(ValueError, Opts, ['-ac'], ['a', 'b', 'c'],
                          required=['b'])
        # same except with 'b' given this time -> no exception
        self.assertTrue(Opts(['-abc'], ['a', 'b', 'c'], required=['b']))

        # missing 'seven'
        self.assertRaises(ValueError, Opts, ['--eight', '--nine'],
                          ['seven', 'eight', 'nine'],
                          required=['seven', 'eight'])
        # same except with 'eight' this time -> no exception
        self.assertTrue(Opts(['--seven', '--eight', '--nine'],
                        ['seven', 'eight', 'nine'],
                        required=['seven', 'eight']))

        # mixed short and long names: missing 'c', 'd', 'e'
        self.assertRaises(ValueError, Opts, ['-a', 'b'],
                          ['aflag', 'bflag', 'cflag', 'dflag', 'eflag'],
                          required=['cflag', 'dflag', 'eflag'])

        # invalid required name
        self.assertRaises(ValueError, Opts, ['-a', '-b', '-c'],
                          ['aflag', 'bflag', 'cflag'],
                          required=['aflag', 'zzz'])

    def test_excluded(self):
        # 'a' and 'c' not allowed together
        self.assertRaises(ValueError, Opts, ['-a', '-c'], ['a', 'b', 'c'],
                          excluded=[['a', 'c']])

        # 'a' by itself is ok
        self.assertTrue(Opts(['-a'], ['a', 'b', 'c'],
                        excluded=[['a', 'c']]))
        # 'c' by itself is ok
        self.assertTrue(Opts(['-c'], ['a', 'b', 'c'],
                        excluded=[['a', 'c']]))

        # mixed short and long names, multiple exclude lists
        names = ['%sflag' % chr(s) for s in range(ord('a'), ord('g') + 1)]
        exclude_lists = [['cflag', 'eflag', 'gflag'],
                         ['aflag', 'gflag'],
                         ['aflag', 'bflag'],
                         ['bflag', 'eflag']]

        self.assertRaises(ValueError, Opts, ['-e', '-c'], names,
                          excluded=exclude_lists)
        self.assertRaises(ValueError, Opts, ['-c', '--gflag'], names,
                          excluded=exclude_lists)
        self.assertRaises(ValueError, Opts, ['--eflag', '-g'], names,
                          excluded=exclude_lists)
        self.assertRaises(ValueError, Opts, ['-g', '--cflag', 'e'], names,
                          excluded=exclude_lists)

        self.assertRaises(ValueError, Opts, ['-a', '--gflag'], names,
                          excluded=exclude_lists)
        self.assertRaises(ValueError, Opts, ['-a', '--bflag'], names,
                          excluded=exclude_lists)

        self.assertRaises(ValueError, Opts, ['--bflag', '--eflag'], names,
                          excluded=exclude_lists)

        # these should be valid
        self.assertTrue(Opts(['--aflag', '--cflag', '-d'], names,
                                  excluded=exclude_lists))
        self.assertTrue(Opts(['--bflag', '--gflag'], names,
                                  excluded=exclude_lists))
        self.assertTrue(Opts(['--aflag', '-d', '--dflag'], names,
                                  excluded=exclude_lists))
