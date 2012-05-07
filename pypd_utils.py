#!/usr/bin/env python

"""Various utility classes that don't fit elsewhere."""

import sys


def toPdColor(red, green, blue):
    """RGB to PD format color"""

    return (red * -65536) + (green * -256) + (blue * -1)


def funcname(frame_num=0):
    """With frame_num = 0 this returns the printable name of the calling
       function. Increasing frame numbers return the names of the calling
       functions back up the stack."""

    return sys._getframe(frame_num + 1).f_code.co_name
